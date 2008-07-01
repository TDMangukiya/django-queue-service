import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site


# See Queue.get_attributes for how QueueAttributes is used
QueueAttributes = None


class Queue(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    default_expire = models.PositiveIntegerField(default=5, help_text="In minutes.")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        rel_url = reverse('queue', kwargs={'queue_name':self.name})
        return u'http://%s%s' % (Site.objects.get_current().domain, rel_url)

    def clear_expirations(self):
        """
        Change visibility to True for messages whose expiration time has elapsed.
        """
        qs = self.message_set.filter(visible=False, expires__lt=datetime.datetime.now())
        qs.update(expires=None, visible=True)
        return None

    def get_attributes(self):
        global QueueAttributes
        if not QueueAttributes:
            # Dynamically define a model that's never stored in the database.
            # This is useful because returning the QueueAttributes as a 
            # Django model allows us to use the JSON and XML serializers 
            # directly on these objects.
            class DummyMeta:
                app_label = 'queue'
            QueueAttributes = type('QueueAttribs', (models.Model,), {
                'number_of_messages': models.PositiveIntegerField(),
                'number_unread': models.PositiveIntegerField(),
                'visibility_timeout': models.PositiveIntegerField(),
                '__module__':'dummy.queue.models',
                'Meta':DummyMeta
            })
        q_attribs = QueueAttributes(pk=0)
        q_attribs.number_of_messages = self.message_set.count()
        q_attribs.number_unread = self.message_set.filter(visible=True).count()
        q_attribs.visibility_timeout = self.default_expire * 60 # in seconds
        return q_attribs

class MessageManager(models.Manager):
    def pop_many(self, queue=None, expire_interval=5, num=25):
        """Return visible Message objects if available, or an empty list. Any Message
        returned is set to 'invisible', so that future pop() invocations won't 
        retrieve it until after an expiration time (default of 5 minutes).

        ``queue`` can either be the name of a queue or an instance of Queue.

        """
        if queue is None:
            # The following code allows us to do:
            # q.message_set.pop_many() when we already have an instance of q at hand
            f = self
        else:
            f = isinstance(queue, Queue) and queue.message_set or \
                                         self.filter(queue__name=queue)
        now = datetime.datetime.now()
        results = f.filter(models.Q(visible=True) | models.Q(expires__lt=now)).order_by('timestamp', 'id')[0:num]

        # now we bulk update messages in this set with 
        # visible=False and expires=now+expire_interval
        expires = now + datetime.timedelta(minutes=expire_interval)
        id_list = [m.id for m in results]
        qs = self.filter(id__in=id_list)
        qs.update(expires=expires, visible=False)
        return results

    def pop(self, queue=None, expire_interval=5):
        """ returns a visible Message if available, or None. Any Message
        returned is set to 'invisible', so that future pop() invocations won't 
        retrieve it until after an expiration time (default of 5 minutes).
        
        queue can either be the name of a queue or an instance of Queue.
        """
        try:
            if queue is None:
                # The following code allows us to do:
                # q.message_set.pop() when we already have an instance of q at hand
                f = self
            else:
                f = isinstance(queue, Queue) and queue.message_set or \
                                             self.filter(queue__name=queue)
            result = f.filter(visible=True).order_by('timestamp', 'id')[0:1].get()
            result.visible = False
            result.expires = datetime.datetime.now() + datetime.timedelta(minutes=expire_interval)
            result.save()
            return result
        except Message.DoesNotExist:
            return None

    def clear_expirations(self, queue):
        # This method has been moved to the Queue object but is left here
        # for backward compatibility
        q = isinstance(queue, Queue) and queue or Queue.objects.get(name=queue)
        q.clear_expirations()


class Message(models.Model):
    message = models.TextField()
    visible = models.BooleanField(default=True, db_index=True)
    expires = models.DateTimeField(null=True, blank=True, db_index=True,
                help_text="After this time has elapsed, the visibility of the message \
                           is changed back from False to True (when clear_expirations is executed).")
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True, default=datetime.datetime.now)
    queue = models.ForeignKey(Queue)
    objects = MessageManager()

    def save(self):
        if not self.id:
            self.timestamp = datetime.datetime.now()
        super(Message, self).save()

    def __unicode__(self):
        return u"<%s>:%s" % (self.id, self.message)


from queue.admin import *


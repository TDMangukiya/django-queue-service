import datetime
from django.db import models


class Queue(models.Model):
    name = models.CharField(maxlength=255, unique=True, db_index=True)
    default_expire = models.PositiveIntegerField(default=5, help_text="In minutes.")

    def __unicode__(self):
        return self.name

    class Admin:
        list_display = ('name', 'default_expire')

    def clear_expirations(self):
        """
        Changes visibility to True for messages whose expiration time has elapsed.
        queue can either be the name of a queue or an instance of Queue.
        """
        from django.db import connection, transaction, DatabaseError
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE %s set expires=%%s, visible=%%s \
                       where queue_id=%%s and visible=%%s and \
                       expires < %%s" % Message._meta.db_table, 
                       [None, True, self.id, False, datetime.datetime.now()])
        except DatabaseError:
            # @RD: These updates could be allowed to fail silently.
            pass
        else:
            transaction.commit_unless_managed()
        return None

class MessageManager(models.Manager):
    def pop_many(self, queue=None, expire_interval=5, num=25):
        """ returns visibles Message if available, or an empty list. Any Message
        returned is set to 'invisible', so that future pop() invocations won't 
        retrieve it until after an expiration time (default of 5 minutes).
        
        queue can either be the name of a queue or an instance of Queue.
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
        from django.db import connection, transaction, DatabaseError
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE %s set expires=%%s, visible=%%s \
                       where id in %s" % (Message._meta.db_table, str(tuple(id_list))),
                       [expires, False])
        except DatabaseError:
            # @RD -> Open issue: Do we need to catch this exception?
            pass
        else:
            transaction.commit_unless_managed()
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
    queue = models.ForeignKey(Queue, raw_id_admin=True)
    objects = MessageManager()

    def save(self):
        if not self.id:
            self.timestamp = datetime.datetime.now()
        super(Message, self).save()

    def __unicode__(self):
        return u"<%s>:%s" % (self.id, self.message)

    class Admin:
        list_display = ('id', 'visible', 'expires', 'queue')
        list_filter = ('visible',)


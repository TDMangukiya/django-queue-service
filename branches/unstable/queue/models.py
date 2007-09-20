import datetime
from django.db import models

class Queue(models.Model):
    """
    >>> from queue.models import Queue
    >>> test_queue = Queue(name="test_queue")
    >>> test_queue.save()
    >>> print test_queue.default_expire
    5
    """
    name = models.CharField(maxlength=255, unique=True, db_index=True)
    default_expire = models.PositiveIntegerField(default=5, help_text="In minutes.")

    def __str__(self):
        return self.name

    class Admin:
        pass

class MessageManager(models.Manager):
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
        """
        Changes visibility to True for messages whose expiration time has elapsed.
        queue can either be the name of a queue or an instance of Queue.
        """
        q = isinstance(queue, Queue) and queue or Queue.objects.get(name=queue)
        from django.db import connection, transaction, DatabaseError
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE %s set expires=%%s, visible=%%s \
                       where queue_id=%%s and visible=%%s and \
                       expires < %%s" % self.model._meta.db_table, 
                       [None, True, q.id, False, datetime.datetime.now()])
        except DatabaseError:
            # @RD: For thread safety: these updates could be allowed to fail silently
            # @RD: Perhaps, this isn't needed.
            pass
        else:
            transaction.commit_unless_managed()
        return None

class Message(models.Model):
    """
    >>> from queue.models import Queue
    >>> default = Queue.objects.get(name="default")
    >>> print default.name
    default
    >>> default.message_set.count()
    3
    >>> test2 = Queue.objects.create(name='test2')
    >>> from queue.models import Message
    >>> test2msg = test2.message_set.create(message='test2 message')
    >>> x=Message(message="t1",queue=default)
    >>> x.save()
    >>> x=Message(message="t2",queue=default)
    >>> x.save()
    >>> x=Message(message="t3",queue=default)
    >>> x.save()
    >>> print Message.objects.pop('default').message
    a
    >>> print Message.objects.pop(default).message
    b
    >>> y=Message.objects.pop('default')
    >>> print y.message
    c
    >>> y.visible
    False
    >>> print len(default.message_set.all())
    6
    >>> x=Message(message="hello",queue=default)
    >>> x.save()
    >>> print x.message
    hello
    >>> x.timestamp == None
    False
    >>> x.visible
    True
    >>> x=Message(queue=default)
    >>> x.save()
    >>> print ">>%s<<" % x.message
    >><<
    >>> x.visible
    True
    
    >>> len(Message.objects.filter(visible=True, queue=default))
    5
    >>> x=Message(message="aa",queue=default).save()
    >>> x=Message(message="bb",queue=default).save()
    >>> x=Message(message="cc",queue=default).save()
    >>> a=Message.objects.pop('default')
    >>> b=Message.objects.pop('default')
    >>> c=Message.objects.pop('default')
    >>> a.expires=datetime.datetime.now()
    >>> a.save()
    >>> b.expires=datetime.datetime.now()
    >>> b.save()
    >>> import time
    >>> time.sleep(.02) # needed on fast machines for the below test to succeed
    >>> Message.objects.clear_expirations(default)
    >>> len(default.message_set.filter(visible=True))
    7
    >>> t2x = test2.message_set.pop()
    >>> print t2x.message
    test2 message
    >>> print t2x.visible, t2x.expires is not None
    False True
    """
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
    
    def __str__(self):
        return "QM<%s> : %s" % (self.id, self.message)
            
    class Admin:
        pass


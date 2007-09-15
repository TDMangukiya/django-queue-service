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
    name = models.CharField(maxlength=255,unique=True)
    default_expire = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

    class Admin:
        pass
    
# Create your models here.
class MessageManager(models.Manager):
    def pop(self,queue_name,expire_interval=5):
        """ returns a visible Message if available, or None. Any Message
        returned is set to 'invisible', so that future pop() invocations won't 
        retrieve it until after an expiration time (default of 5 minutes)."""
        q = None
        try:
            q = Queue.objects.get(name=queue_name)
        except Queue.DoesNotExist:
            pass
        if q is None: 
            return None
        queryset = q.message_set.filter(visible=True).order_by('timestamp', 'id')
        if len(queryset) < 1:
            return None
        else:
            result = queryset[0]
            result.visible = False
            result.expires = datetime.datetime.now()+datetime.timedelta(minutes=expire_interval)
            result.save()
            return result
            
    def clear_expirations(self,queue_name):
        q = None
        try:
            q = Queue.objects.get(name=queue_name)
        except Queue.DoesNotExist:
            pass
        if q is None: 
            return None
        queryset = q.message_set.filter(visible=False,expires__lt=datetime.datetime.now())
        for msg in queryset:
            msg.expires = None
            msg.visible = True
            msg.save()
        return None

class Message(models.Model):
    """
    >>> from queue.models import Queue
    >>> default = Queue.objects.get(name="default")
    >>> print default.name
    default
    >>> from queue.models import Message
    >>> x=Message(message="t1",queue=default)
    >>> x.save()
    >>> x=Message(message="t2",queue=default)
    >>> x.save()
    >>> x=Message(message="t3",queue=default)
    >>> x.save()
    >>> print Message.objects.pop('default').message
    a
    >>> print Message.objects.pop('default').message
    b
    >>> y=Message.objects.pop('default')
    >>> print y.message
    c
    >>> y.visible
    False
    >>> print len(Message.objects.all())
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
    
    >>> len(Message.objects.filter(visible=True))
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
    >>> Message.objects.clear_expirations('default')
    >>> len(Message.objects.filter(visible=True))
    7
    """
    message = models.TextField()
    visible = models.BooleanField(default=True)
    expires = models.DateTimeField(null=True,blank=True)
    timestamp = models.DateTimeField(null=True,blank=True,default=datetime.datetime.now)
    queue = models.ForeignKey(Queue,raw_id_admin=True)
    objects = MessageManager()
    
    def save(self):
        if not self.id:
            self.timestamp = datetime.datetime.now()
        super(Message, self).save()
    
    def __str__(self):
        return "QM<%s> : %s" % (self.id,self.message)
            
    class Admin:
        pass


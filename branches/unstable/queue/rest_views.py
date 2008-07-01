"""
Ref: /docs/DQS_REST.PDF defines the REST actions we are aiming to implement.
"""
import datetime

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success

from qs.queue import check_allowed_methods, Status
from qs.queue.models import Message, Queue


def call_view_function_for_method(view_name, request, **kwargs):
    '''This is a helper function that looks up a view sub-function
    to call based on the request's REST verb. Thus, we avoid repetitive
    conditional blocks of the type:
        if request.METHOD == 'POST':
        elif request.METHOD == 'PUT':
        elif ...
    '''
    from qs.queue import rest_views
    fn_name = '%s_%s' % (view_name, request.method.lower())
    if hasattr(rest_views, fn_name):
        status = Status(request.REQUEST)
        return getattr(rest_views, fn_name)(request, status, **kwargs)
    else:
        raise NotImplemented

# ----- root level view functions
def root(request):
    return call_view_function_for_method('root', request)
root = check_allowed_methods(['GET', 'POST'])(root)
root = commit_on_success(root)

def root_post(request, status):
    '''POST = create queue (requires: QueueName)'''
    try:
        queue_name = request.REQUEST['QueueName']
        q, created = Queue.objects.get_or_create(name=queue_name)
        if not created:
            status.error = 'QueueAlreadyExists'
        else:
            status.result = {'QueueUrl':q.get_absolute_url()}
    except KeyError:
        status.response = HttpResponseNotAllowed()
    return status()

def root_get(request, status):
    '''GET = list queues'''
    status.result = [dict(QueueName=q.name, QueueUrl=q.get_absolute_url()) for q in Queue.objects.all()]
    return status()

# ----- queue level view functions
def queue(request, queue_name):
    status = Status(request.REQUEST)
    try:
        q = Queue.objects.get(name=queue_name)
    except Queue.DoesNotExist:
        status.response = HttpResponseNotFound()
        return status()
    return call_view_function_for_method('queue', request, queue=q)
queue = check_allowed_methods(['GET', 'POST', 'PUT', 'DELETE'])(queue)
queue = commit_on_success(queue)

def queue_post(request, status, queue):
    "POST = send message (requires: Message)"
    try:
        message = request.POST['Message']
        m = queue.message_set.create(message=message)
        status.result = {'MessageId':m.pk, 'VisibilityTimeout':queue.default_expire}
    except KeyError:
        status.response = HttpResponseNotAllowed()
    return status()

def queue_get(request, status, queue):
    '''
    GET = list messages (accepts: NumberOfMessages)
        = view queue attributes (if QueryType is "Attributes")
    '''
    if request.REQUEST.get('QueryType', None) == 'Attributes':
        # view attributes
        q_attribs = queue.get_attributes()
        status.result = [q_attribs]
    else:
        # list messages
        n = int(request.REQUEST.get('NumberOfMessages', 25))
        if n > 100:
            n = 100 # TBD: Disallow very large result sets?
        message_list = [dict(MessageId=m.pk, MessageBody=m.message) for m in queue.message_set.pop_many(num=n)]
        status.result = message_list
    return status()

def queue_put(request, status, queue):
    '''PUT = set queue attributes (requires: VisibilityTimeout in seconds)
    To be discussed: Queue.default_attribute is currently defined in minutes.
    We need to decide if we should change that to seconds. Alternatively, we 
    could modify the REST implementation to treat that parameter in minute units.
    '''
    vis = request.REQUEST.get('VisibilityTimeout', None)
    if vis is not None:
        # Convert 1 - 59 seconds as 1 min, 60 - 119 seconds as 2 mins, etc.
        # 0 is interpreted as 0
        # This will change if we decide to stay with 
        # minute units instead of seconds.
        vis = int(vis)
        queue.default_expire = vis/60 + int(vis!=0)
        queue.save()
        q_attribs = queue.get_attributes()
        status.result = [q_attribs]
    else:
        status.error = 'VisibilityTimeout was not provided in the query string.'
    return status()

def queue_delete(request, status, queue):
    'DELETE = delete queue (accepts: ForceDeletion="no/yes" -- used for non-empty queues)'
    force = request.REQUEST.get('ForceDeletion', 'no') == 'yes'
    if not force:
        # Ensure that Q is empty
        if queue.message_set.count() > 0:
            status.error = 'QueueNotEmpty'
        else: # queue is empty
            queue.delete()
    else: # delete regardless of queue's emptiness
        queue.delete()
    return status()

# ----- message level view functions
def message(request, queue_name, message_id):
    status = Status(request.REQUEST)
    try:
        m = Message.objects.get(pk=message_id, queue__name=queue_name)
    except Message.DoesNotExist:
        status.response = HttpResponseNotFound()
        return status()
    return call_view_function_for_method('message', request, message=m)
message = check_allowed_methods(['GET', 'DELETE'])(message)
message = commit_on_success(message)

def message_get(request, status, message):
    "GET = Peek at a message without changing its visibility"
    status.result = dict(MessageId=message.pk, MessageBody=message.message)
    return status()

def message_delete(request, status, message):
    "DELETE = Delete message"
    message.delete()
    return status()

import datetime
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound
from django.utils.encoding import smart_str
from queue import check_allowed_methods, Status
from queue.models import Message, Queue

def call_view_function_for_method(view_name, request, **kwargs):
    from queue import rest_views
    fn_name = '%s_%s' % (view_name, request.method.lower())
    if hasattr(rest_views, fn_name):
        status = Status(request.REQUEST)
        return getattr(rest_views, fn_name)(request, status, **kwargs)
    else:
        raise NotImplemented

def root(request):
    return call_view_function_for_method('root', request)
create_queue = check_allowed_methods(['GET', 'POST'])(root)

def root_post(request, status):
    '''POST = create queue (requires: QueueName)'''
    try:
        queue_name = request.REQUEST['QueueName']
        q, created = Queue.objects.get_or_create(name=queue_name)
        if not created:
            status.error = 'QueueAlreadyExists'
    except KeyError:
        status.response = HttpResponseNotAllowed()
    return status()

def root_get(request, status):
    '''GET = list queues'''
    status.result = Queue.objects.all()
    return status()

def queue(request, queue_name):
    '''
    POST = send message (requires: Message)
    GET = list messages (accepts: NumberOfMessages)
        = view queue attributes (if QueryType is "Attributes")
    PUT = set queue attributes (requires: VisibilityTimeout in seconds)
    DELETE = delete queue (accepts: ForceDeletion="no/yes" -- used for non-empty queues)
    '''
    status = Status(request.REQUEST)
    try:
        q = Queue.objects.get(name=queue_name)
    except Queue.DoesNotExist:
        status.response = HttpResponseNotFound()
        return status()
    return call_view_function_for_method('queue', request, q=q)
create_queue = check_allowed_methods(['GET', 'POST', 'PUT', 'DELETE'])(queue)

def queue_post(request, status, q):
    try:
        message = request.POST['Message']
        q.message_set.create(message=message)
    except KeyError:
        status.response = HttpResponseNotAllowed()
    return status()

def queue_get(request, status, q):
    if request.REQUEST.get('QueryType', None) == 'Attributes':
        # view attributes
        raise NotImplemented
    else:
        # list messages
        n = int(request.REQUEST.get('NumberOfMessages', 25))
        if n > 100:
            n = 25 # TBD: Disallow very large result sets?
        message_list = q.message_set.pop_many(num=n)
        status.result = message_list
    return status()




# Create your views here.
from django.utils import simplejson
from queue.models import Message, Queue
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseNotFound
from django import newforms as forms
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime


def check_allowed_methods(methods=['GET']):
    '''Convenient decorator that verifies that a view is being called with 
an allowed set of request methods and no others.
Returns HttpResponseForbidden if view is called with a disallowed method.'''
    def _decorator(view_func):
        def _wrapper(request, *args, **kwargs):
            if request.method in methods:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        _wrapper.__doc__ = view_func.__doc__
        _wrapper.__dict__ = view_func.__dict__
        return _wrapper
    return _decorator

# Queue Methods
@check_allowed_methods(['POST'])
def create_queue(request):
    # test post with
    # curl -i http://localhost:8000/createqueue/ -d name=default
    requested_name = request.POST.get('name', None)
    if requested_name is None:
        return HttpResponseForbidden()
    q = Queue(name=requested_name)
    q.save()
    return HttpResponse("", mimetype='text/plain')

@check_allowed_methods(['POST', 'DELETE'])
def delete_queue(request):
    # test post with
    # curl -i http://localhost:8000/deletequeue/ -d name=default
    requested_name = request.POST.get('name', None)
    if requested_name is None:
        return HttpResponseForbidden()
    try:
        q = Queue.objects.get(name=requested_name)
        if q.message_set.count() > 0:
            return HttpResponseNotAllowed()
        q.delete()
        return HttpResponse("", mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()

@check_allowed_methods(['POST'])
def purge_queue(request):
    # test post with
    # curl -i http://localhost:8000/purgequeue/ -d name=default
    requested_name = request.POST.get('name', None)
    if requested_name is None:
        return HttpResponseForbidden()
    try:
        q = Queue.objects.get(name=requested_name)
        q.message_set.all().delete()
        return HttpResponse("", mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()

@check_allowed_methods(['GET'])
def list_queues(request):
    # test post with
    # curl -i http://localhost:8000/listqueues/
    result_list = []
    for queue in Queue.objects.all():
        result_list.append(queue.name)
    return HttpResponse(simplejson.dumps(result_list), mimetype='application/json')

#
# Message methods - all of these will be operating on messages against a queue...
#

@check_allowed_methods(['GET'])
def get(request, queue_name, response_type='text'):
    # test count with
    # curl -i http://localhost:8000/q/default/
    # curl -i http://localhost:8000/q/default/json/
    
    # print "GET queue_name is %s" % queue_name
    q = None
    # pre-emptive queue name checking...
    try:
        q = Queue.objects.get(name=queue_name)
    except Queue.DoesNotExist:
        return HttpResponseNotFound()
    #
    msg = q.message_set.pop()
    if response_type == 'json':
        msg_dict = {}
        if msg:
            msg_dict['message'] = msg.message
            msg_dict['id'] = msg.id
        return HttpResponse(simplejson.dumps(msg_dict), mimetype='application/json')
    else:
        response_data = ''
        if msg:
            response_data = msg.message
        return HttpResponse(response_data, mimetype='text/plain')

#@check_allowed_methods(['POST'])
def clear_expirations(request, queue_name):
    # test count with
    # curl -i http://localhost:8000/q/default/clearexpire/
    # @TODO: This should only work with a POST as the following code changes data
    try:
        Message.objects.clear_expirations(queue_name)
        return HttpResponse("", mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()

@check_allowed_methods(['GET'])
def count(request, queue_name, response_type='text'):
    # test count with
    # curl -i http://localhost:8000/q/default/count/
    # curl -i http://localhost:8000/q/default/count/json/
    try:
        q = Queue.objects.get(name=queue_name)
        num_visible = q.message_set.filter(visible=True).count()
        if response_type == 'json':
            msg_dict = {"count":"%s" % num_visible}
            return HttpResponse(simplejson.dumps(msg_dict), mimetype='application/json')
        else:
            return HttpResponse("%s" % num_visible, mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()

@check_allowed_methods(['POST', 'DELETE'])
def delete(request, queue_name):
    # test post with
    # curl -i http://localhost:8000/q/default/delete/ -d message_id=1
    #print "deleting: %s" % message_id
    message_id=request.POST['message_id']
    try:
        q = Queue.objects.get(name=queue_name)
        msg = q.message_set.get(pk=message_id)
        msg.delete()
        return HttpResponse("OK", mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()
    except Message.DoesNotExist:
        return HttpResponseNotFound()

@check_allowed_methods(['POST'])
def put(request, queue_name):
    # test post with
    # curl -i http://localhost:8000/q/default/put/ -d message=hello
    try:
        q = Queue.objects.get(name=queue_name)
        msg = Message(message=request.POST['message'], queue=q)
        msg.save()
        return HttpResponse("OK", mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()


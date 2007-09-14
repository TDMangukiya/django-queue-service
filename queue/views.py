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


# Queue Methods
def create_queue(request):
    # test post with
    # curl -i http://localhost:8000/createqueue/ -d name=default
    if request.method == "POST":
        requested_name = request.POST.get('name', None)
        if requested_name is None:
            return HttpResponseForbidden()
        msg = Queue(name=requested_name)
        msg.save()
        return HttpResponse("", mimetype='text/plain')
    return HttpResponseForbidden()

def delete_queue(request):
    # test post with
    # curl -i http://localhost:8000/deletequeue/ -d name=default
    if request.method == "POST":
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
    return HttpResponseForbidden()

def purge_queue(request):
    # test post with
    # curl -i http://localhost:8000/purgequeue/ -d name=default
    if request.method == "POST":
        requested_name = request.POST.get('name', None)
        if requested_name is None:
            return HttpResponseForbidden()
        try:
            q = Queue.objects.get(name=requested_name)
            q.message_set.all().delete()
            return HttpResponse("", mimetype='text/plain')
        except Queue.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponseForbidden()    

def list_queues(request):
    # test post with
    # curl -i http://localhost:8000/listqueues/
    result_list = []
    for queue in Queue.objects.all():
        result_list.append(queue.name)
    return HttpResponse(simplejson.dumps(result_list), mimetype='text/plain')
    return HttpResponse(simplejson.dumps(result_list), mimetype='application/javascript')

#
# Message methods - all of these will be operating on messages against a queue...
#

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
        return HttpResponse(simplejson.dumps(msg_dict), mimetype='application/javascript')
    else:
        response_data = ''
        if msg:
            response_data = msg.message
        return HttpResponse(response_data, mimetype='text/plain')

def clear_expirations(request, queue_name):
    # test count with
    # curl -i http://localhost:8000/q/default/clearexpire/
    try:
        Message.objects.clear_expirations(queue_name)
        return HttpResponse("", mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()

def count(request, queue_name, response_type='text'):
    # test count with
    # curl -i http://localhost:8000/q/default/count/
    # curl -i http://localhost:8000/q/default/count/json/
    try:
        q = Queue.objects.get(name=queue_name)
        num_visible = q.message_set.filter(visible=True).count()
        if response_type == 'json':
            msg_dict = {"count":"%s" % num_visible}
            return HttpResponse(simplejson.dumps(msg_dict), mimetype='application/javascript')
        else:
            return HttpResponse("%s" % num_visible, mimetype='text/plain')
    except Queue.DoesNotExist:
        return HttpResponseNotFound()

def delete(request, queue_name):
    # test post with
    # curl -i http://localhost:8000/q/default/delete/ -d message_id=1
    #print "deleting: %s" % message_id
    if request.method == "POST":
        # print request.POST
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
    return HttpResponse("WHAT?", mimetype='text/plain')
    
def put(request, queue_name):
    # test post with
    # curl -i http://localhost:8000/q/default/put/ -d message=hello
    if request.method == "POST":
        print request.POST
        try:
            q = Queue.objects.get(name=queue_name)
            msg = Message(message=request.POST['message'], queue=q)
            msg.save()
            return HttpResponse("OK", mimetype='text/plain')
        except Queue.DoesNotExist:
            return HttpResponseNotFound()
    return HttpResponse("WHAT?", mimetype='text/plain')

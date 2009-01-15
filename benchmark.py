# rm /tmp/sqs.db && django-admin.py syncdb && python server.py
try:
    import httplib2
except ImportError:
    print "This benchmarking program requires the use to httplib2, available"
    print "at http://code.google.com/p/httplib2/. Please download and install"
    print "it before using this module..."

from django.utils import simplejson
import sys
from utils import median, mean, stddev

# Source code is public domain.
if sys.platform == "win32":
    from time import clock
else:
    from time import time as clock
  
def create_test_queue():
    client = httplib2.Http()
    body_string = "name=test1"
    (response,content) = client.request(uri='http://localhost:8000/createqueue/',method='POST', body=body_string)
    if response['status'] == '200':
        print "Queue created"
        print response

def list_queues():
    client = httplib2.Http()
    (response,content) = client.request(uri='http://localhost:8000/listqueues/',method='GET')
    if response['status'] == '200':
        x = simplejson.loads(content)
        for queue_name in x:
            print "Queue: %s" % queue_name

def add_message(message="hello"):
    client = httplib2.Http()
    body_string = "message=%s" % message
    (response,content) = client.request(uri='http://localhost:8000/q/test1/put/',method='POST', body=body_string)
    return (response,content)
    
def get_message():
    client = httplib2.Http()
    (response,content) = client.request(uri='http://localhost:8000/q/test1/json/',method='GET')
    if response['status'] == '200':
        x = simplejson.loads(content)
        return x
    return None

def delete_message(message_id=None):
    if message_id is None:
        return None
    client = httplib2.Http()
    body_string = "message_id=%s" % message_id
    (response,content) = client.request(uri='http://localhost:8000/q/test1/delete/',method='POST',body=body_string)

def add_messages(number=1000):
    for i in xrange(number):
        add_message()

def clock_adds(number=100):
    times = []
    for i in xrange(number):
        start = clock()
        add_message()
        time_taken = clock() - start
        times.append(time_taken)
    median_time = median(times)
    mean_time = mean(times)
    stddev_time = stddev(times)
    return (median_time,mean_time,stddev_time)
    
def clock_gets(number=100):
    times = []
    for i in xrange(number):
        start = clock()
        x=get_message()
        time_taken = clock() - start
        times.append(time_taken)
    median_time = median(times)
    mean_time = mean(times)
    stddev_time = stddev(times)
    return (median_time,mean_time,stddev_time)

def clock_get_delete(number=100):
    times = []
    for i in xrange(number):
        start = clock()
        x=get_message()
        delete_message(message_id=x['id'])
        time_taken = clock() - start
        times.append(time_taken)
    median_time = median(times)
    mean_time = mean(times)
    stddev_time = stddev(times)
    return (median_time,mean_time,stddev_time)

create_test_queue()
list_queues()

# add_message()
# x=get_message()
# message_id=x['id']
# # print "to delete: ",message_id
# delete_message(message_id=message_id)

def work_it():
    add_message()
    x=get_message()
    delete_message(message_id=x['id'])

worked = 0
(med,men,std) = clock_adds()
(med2,men2,std2) = clock_get_delete()
print "%d\t%s\t%s\t%s\t%s\t%s\t%s" % (worked,med*1000,men*1000,std*1000,med2*1000,men2*1000,std2*1000)
for x in xrange(25):
    for y in xrange(1000):
        work_it()
        worked+=1
    (med,men,std) = clock_adds()
    (med2,men2,std2) = clock_get_delete()
    print "%d\t%s\t%s\t%s\t%s\t%s\t%s" % (worked,med*1000,men*1000,std*1000,med2*1000,men2*1000,std2*1000)
    

added = 0
print "rows\tmedian add (ms)\tmean add (ms)\tstddev add (ms)\tmedian get (ms)\tmean get (ms)\tstddev get (ms)"
for steps in xrange(25):
    (med,men,std) = clock_adds()
    (med2,men2,std2) = clock_get_delete()
    print "%d\t%s\t%s\t%s\t%s\t%s\t%s" % (added,med*1000,men*1000,std*1000,med2*1000,men2*1000,std2*1000)
    add_messages(1000)
    added+=1000

(med,men,std) = clock_adds()
(med2,men2,std2) = clock_get_delete()
print "%d\t%s\t%s\t%s\t%s\t%s\t%s" % (added,med*1000,men*1000,std*1000,med2*1000,men2*1000,std2*1000)


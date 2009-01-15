import httplib, urllib

w = httplib.HTTPConnection('localhost:8000')

# Delete queue
w.request('DELETE', '/queue4/?ForceDeletion=yes')
r = w.getresponse()
data1 = r.read()
r.close()

# Create queue
params = urllib.urlencode({'QueueName':'queue4'})
w.request('POST', '/', params)
r = w.getresponse()
data2 = r.read()
r.close()

# Create message
params = urllib.urlencode({'Message':'This is a test message in to queue4'})
w.request('POST', '/queue4/', params)
r = w.getresponse()
data3 = r.read()
e = eval(data3)
msg_id = e['result']['MessageId']
r.close()

# Get messages
w.request('GET', '/queue4/')
r = w.getresponse()
data4 = r.read()
r.close()

# Peek message
w.request('GET', '/queue4/%s/' % msg_id)
r = w.getresponse()
data5 = r.read()
r.close()



w.close()

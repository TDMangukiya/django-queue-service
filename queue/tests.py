"""
>>> from django.test.client import Client
>>> web = Client()
>>>
>>> r = web.get("/listqueues/")
>>> "default" in r.content and "primary" in r.content
True
>>>
>>> r = web.post('/createqueue/', {'name':'web_test'})
>>> r.status_code
200
>>>
>>> r = web.post('/q/web_test/put/', {'message':'Hello web!'})
>>> print r.status_code, r.content
200 OK
>>>
>>> r = web.get('/q/web_test/count/')
>>> print r.status_code, r.content
200 1
>>>
>>> r = web.get('/q/web_test/')
>>> print r.content
Hello web!
>>>
"""

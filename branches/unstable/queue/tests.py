from django.test import TestCase
from django.test.client import Client

from qs.queue.models import Queue, Message


class CreateMessageCase(TestCase):
    def setUp( self ):
        Queue.objects.create( name='default', default_expire=5)
        Queue.objects.create( name='primary', default_expire=5)
        Queue.objects.create( name='secondary', default_expire=5)

    def testQueue( self ):
        assert Queue.objects.all().count() == 3

    def testDefaultValues( self ):
        dq = Queue.objects.get( name='default' )
        x = Message( message="hello",queue=dq )
        x.save()
        self.failUnlessEqual( x.message, 'hello' )
        self.failIfEqual( x.timestamp, None )
        self.failUnlessEqual(x.visible, True)
        
        x = Message(queue=dq)
        x.save()
        self.failUnlessEqual( x.message, '' )
        self.failUnlessEqual( x.visible, True )

    def testDefaultExpire( self ):
        Queue(name="test_queue").save()
        tq = Queue.objects.get( name='test_queue' )
        self.failUnlessEqual( tq.default_expire, 5)
        
        
    def testMessageOrder( self ):
        import random
        random.seed()

        count = random.randint(100, 200)
        input = [ '%d' % random.randint(0,count) for x in range(count) ]
        dq = Queue.objects.get ( name='default' )

        for message in input:        
            Message.objects.create( message=message, queue=dq, visible=True )
        output = [ Message.objects.pop( 'default' ).message for x in range(count)]
        
        ## verify FIFO
        self.failUnlessEqual( output, input )

    def testVisibleCount( self ):
        dq = Queue.objects.get ( name='default' )
        
        ## Add 50
        for x in range(50):
            Message.objects.create( queue=dq )
            
        ## Subtract 20
        for x in range(20):
            Message.objects.pop('default')
            
        self.failUnlessEqual(len(Message.objects.filter(visible=True)), 30)        
        self.failUnlessEqual(len(Message.objects.filter(visible=False)), 20)        


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_qCreation(self):
        response = self.client.post('/createqueue/', dict( name='web_test'))
        self.failUnlessEqual(200, response.status_code)

        response = self.client.get('/listqueues/')
        self.failUnlessEqual( ['web_test'], eval( response.content) )

    def test_qMessage( self ):
        # First create the queue
        response = self.client.post('/createqueue/', dict( name='web_test'))
        self.failUnlessEqual(200, response.status_code)

        response = self.client.post('/q/web_test/put/', { 'message' : 'Hello Web!' })
        self.failUnlessEqual(200, response.status_code)

        response = self.client.get('/q/web_test/count/')
        self.failUnlessEqual(200, response.status_code)
        self.failUnlessEqual( '1', response.content )

        response = self.client.get('/q/web_test/')
        self.failUnlessEqual(200, response.status_code)
        self.failUnlessEqual( 'Hello Web!', response.content )

    def test_allowed_methods(self):
        '''Issues a POST where a GET is expected (and vice-versa) 
and verifies that a 403:Forbidden response code is received.'''
        response =  self.client.post('/listqueues/')
        self.failUnlessEqual(403, response.status_code)

        # Create the queue needed by the next few tests
        response = self.client.post('/createqueue/', dict(name='web_test'))
        self.failUnlessEqual(200, response.status_code)

        response = self.client.post('/q/web_test/')
        self.failUnlessEqual(403, response.status_code)

        response = self.client.get('/q/web_test/put/', {'message':'Hello Web!'})
        self.failUnlessEqual(403, response.status_code)

        response = self.client.post('/q/web_test/put/', {'message':'Hello Web!'})
        self.failUnlessEqual(200, response.status_code)


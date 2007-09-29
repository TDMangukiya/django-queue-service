import unittest
from queue.models import *
#from models import *
from django.test.utils import create_test_db, destroy_test_db


class CreateMessageCase( unittest.TestCase ):
    def setUp( self ):
        self.db = create_test_db(autoclobber=True, verbosity=0)
        
        Queue.objects.create( name='default', default_expire=5 ).save()
        Queue.objects.create( name='primary', default_expire=5 ).save()
        Queue.objects.create( name='secondary', default_expire=5 ).save()
        
    def tearDown( self ):
        ## todo: destroy_test_db differs from api doc. http://www.djangoproject.com/documentation/testing/
        ## This doesn't seem to have api symmetry with setUP(). investigate later.
        destroy_test_db('test_qqqservice', verbosity=0)
        
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
            Message.objects.create( message=message, queue=dq, visible=True ).save()
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
      
        
from django.test.client import Client

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_qCreation(self):
        response = self.client.post('/createqueue/', dict( name='web_test'))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/listqueues/')
        self.failUnlessEqual( ['web_test'], eval( response.content) )

    def test_qMessage( self ):
        response = self.client.post('/q/web_test/put/', { 'message' : 'Hello Web!' })
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/q/web_test/count/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual( '1', response.content )

        response = self.client.get('/q/web_test/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual( 'Hello Web!', response.content )



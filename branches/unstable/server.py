import os
import wsgiserver
from django.core.handlers.wsgi import WSGIHandler

if not os.environ.get('DJANGO_SETTINGS_MODULE', False):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'qs.settings'

from django.conf import settings

_HOST = getattr(settings, 'DQS_HOST', 'localhost')
_PORT = getattr(settings, 'DQS_PORT', 8000)
_SERVER_NAME = getattr(settings, 'DQS_SERVER_NAME', 'localhost')


def runserver():
    wsgi_apps = WSGIPathInfoDispatcher([('/', WSGIHandler())])
    server = CherryPyWSGIServer((_HOST, int(_PORT)),
                wsgi_apps,
                numthreads=numthreads,
                server_name=_SERVER_NAME)

    # 
    # # Want SSL support? Just set these attributes
    # # server.ssl_certificate = <filename>
    # # server.ssl_private_key = <filename>
    # 
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

    # from wsgiref.simple_server import make_server
    # httpd = make_server('', 8000, WSGIHandler())
    # httpd.serve_forever()
    return server

if __name__ == '__main__':
    runserver()


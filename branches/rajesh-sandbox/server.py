from django.core.handlers.wsgi import WSGIHandler
import wsgiserver

import os

if not os.environ.get('DJANGO_SETTINGS_MODULE', False):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'qs.settings'

if __name__ == '__main__':
    wsgi_apps = [('/', WSGIHandler())]
    # server = wsgiserver.CherryPyWSGIServer(('localhost', 8000), wsgi_apps, server_name='localhost')
    server = wsgiserver.CherryPyWSGIServer(('localhost', 8000), WSGIHandler(), server_name='localhost')
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

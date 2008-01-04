from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^createqueue/$', 'qs.queue.views.create_queue'), #post 'name' of queue
    (r'^deletequeue/$', 'qs.queue.views.delete_queue'), #post 'name' of queue
    (r'^purgequeue/$', 'qs.queue.views.purge_queue'),   #post 'name' of queue
    (r'^listqueues/$', 'qs.queue.views.list_queues'),

    (r'^q/(?P<queue_name>\w+)/put/$', 'qs.queue.views.put'),
    (r'^q/(?P<queue_name>\w+)/clearexpire/$', 'qs.queue.views.clear_expirations'),
    (r'^q/(?P<queue_name>\w+)/count/json/$', 'qs.queue.views.count', {"response_type":"json"}),
    (r'^q/(?P<queue_name>\w+)/count/$', 'qs.queue.views.count', {"response_type":"text"}),
    (r'^q/(?P<queue_name>\w+)/delete/$', 'qs.queue.views.delete'), #post 'message_id' of msg
    (r'^q/(?P<queue_name>\w+)/json/$', 'qs.queue.views.get', {"response_type":"json"}),
    (r'^q/(?P<queue_name>\w+)/$', 'qs.queue.views.get', {"response_type":"text"}),
)

_ENABLE_REST_URLS = getattr(settings, 'DQS_ENABLE_REST_URLS', True)
if _ENABLE_REST_URLS:
    urlpatterns += patterns('qs.queue.rest_views',
        (r'^$', 'root'),
        (r'^(?P<queue_name>\w+)/$', 'queue'),
        (r'^(?P<queue_name>\w+)/(?P<message_id>\d+)/$', 'message'),
    )


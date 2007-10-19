from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^', include('qs.queue.urls')), # Everything goes to the Queue app at the moment
    
    # Uncomment this for admin:
    # (r'^admin/', include('django.contrib.admin.urls')),
)

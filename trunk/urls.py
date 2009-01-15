from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^', include('qs.queue.urls')), # Everything goes to the Queue app at the moment
)

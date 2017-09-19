from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url('', include('cms.urls')),
    url(r'^crowdsourcing/', include('crowdsourcing.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    # See settings.py for detailed instructions on how to build the
    # documentation.
    url(r'^docs/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.DOCUMENTATION_ROOT})
]

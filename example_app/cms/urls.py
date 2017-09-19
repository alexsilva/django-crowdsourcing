from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views import home

urlpatterns = [
    url(r'^$', home)
]

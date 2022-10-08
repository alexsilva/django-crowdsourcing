from example_app.cms.views import home
from django.urls import re_path

urlpatterns = [
    re_path(r'^$', home)
]

"""lottery URL Configuration
"""
from django.conf.urls import url, include
from django.contrib import admin
from lotto.admin import allocateDraw

urlpatterns = [
    url(r'^admin/allocateDraw/(?P<draw>[0-9]+)/$', allocateDraw),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
]

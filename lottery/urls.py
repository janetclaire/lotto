"""lottery URL Configuration """
from django.conf.urls import url, include
from django.contrib import admin
from lotto.admin import allocateDraw
from lotto.views import PunterView, EntryView, LandingPage, GoodluckView, EntriesView

urlpatterns = [
    url(r'^admin/allocateDraw/(?P<draw>[0-9]+)/$', allocateDraw),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^punter/$', PunterView.as_view()),
    url(r'^entry/(?P<punterid>[0-9]+)/$', EntryView.as_view()),
    url(r'^entries/(?P<punterid>[0-9]+)/$', EntriesView.as_view()),
    url(r'^goodluck/(?P<punterid>[0-9]+)/(?P<entry>[0-9]+)/$', GoodluckView.as_view()),
    url(r'', LandingPage.as_view()),
]

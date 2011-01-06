from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'anime.views',
    (r'^$', 'index'),
    (r'^add/$', 'add'),
    (r'^(?P<anime_id>\d+)/$', 'info'),
)
#

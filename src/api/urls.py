from django.conf.urls import url, include
from api.views import LocationStops, LocationDetails, ScreenDetails, WidgetUpdate, ScreenList

screen_patterns = [
    url(r'^(?P<widget>[\w\-]+)/$', WidgetUpdate.as_view(), name='widget-update'),
    url(r'^$', ScreenDetails.as_view(), name='screen'),
]

urlpatterns = [
  url(r'^location/(?P<pk>\d+)/stops/$', LocationStops.as_view(), name='location-stops'),
  url(r'^location/(?P<pk>\d+)/$', LocationDetails.as_view(), name='location'),

  url(r'^screen/(?P<slug>[\w\-]+)/', include(screen_patterns)),
  url(r'^screen/$', ScreenList.as_view(), name='screens'),
]

from django.conf.urls import url, include
from api.views import LocationStops, LocationDetails, ScreenDetails, WidgetUpdate, ScreenList, ScreenShared, LocationDistance, GroupManage

screen_patterns = [
    url(r'^(?P<widget>[\w\-]+)/$', WidgetUpdate.as_view(), name='widget-update'),
    url(r'^group/(?P<pk>\d+)/$', GroupManage.as_view(), name='group-manage'),
    url(r'^shared/(?P<token>[\w\-]+)/$', ScreenShared.as_view(), name='screen-shared'),
    url(r'^$', ScreenDetails.as_view(), name='screen'),
]

location_patterns = [
  url(r'^distance/(?P<stop_id>\d+)/$', LocationDistance.as_view(), name='location-distance'),
  url(r'^stops/$', LocationStops.as_view(), name='location-stops'),
  url(r'^$', LocationDetails.as_view(), name='location'),
]

urlpatterns = [
  url(r'^location/(?P<pk>\d+)/', include(location_patterns)),

  url(r'^screen/(?P<slug>[\w\-]+)/', include(screen_patterns)),
  url(r'^screen/$', ScreenList.as_view(), name='screens'),
]

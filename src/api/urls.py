from django.conf.urls import url, include
from api.views import LocationStops, LocationList, LocationDetails, ScreenManage, WidgetManage, WidgetCreate, ScreenList, ScreenShared, LocationDistance, GroupManage, CityList, TemplateManage, Auth

screen_patterns = [
    url(r'^widgets/$', WidgetCreate.as_view(), name='widget-create'),
    url(r'^group/(?P<pk>\d+)/$', GroupManage.as_view(), name='group-manage'),
    url(r'^shared/(?P<token>[\w\-]+)/$', ScreenShared.as_view(), name='screen-shared'),
    url(r'^(?P<widget>[\w\-]+)/$', WidgetManage.as_view(), name='widget-update'),
    url(r'^$', ScreenManage.as_view(), name='screen'),
]

location_patterns = [
  url(r'^distance/(?P<stop_id>\d+)/$', LocationDistance.as_view(), name='location-distance'),
  url(r'^stops/$', LocationStops.as_view(), name='location-stops'),
  url(r'^$', LocationDetails.as_view(), name='location'),
]

app_name = 'api'
urlpatterns = [
  url(r'^location/(?P<pk>\d+)/', include(location_patterns)),
  url(r'^location/$', LocationList.as_view(), name='locations'),

  url(r'^screen/(?P<slug>[\w\-]+)/', include(screen_patterns)),
  url(r'^screen/$', ScreenList.as_view(), name='screens'),
  url(r'^template/$', TemplateManage.as_view(), name='templates'),

  # Auth
  url(r'^auth/', Auth.as_view(), name='auth'),

  # Extras
  url(r'^city/$', CityList.as_view(), name='cities'),
]

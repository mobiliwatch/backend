from django.conf.urls import url
from api.views import LocationStops, LocationDetails

urlpatterns = [
  url(r'^location/(?P<pk>\d+)/stops/$', LocationStops.as_view(), name='location-stops'),
  url(r'^location/(?P<pk>\d+)/$', LocationDetails.as_view(), name='location'),
]

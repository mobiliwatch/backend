from django.conf.urls import url
from api.views import LocationStops

urlpatterns = [
  url(r'^location/(?P<pk>\d+)/stops/$', LocationStops.as_view(), name='location-stops'),
]

from django.conf.urls import url, include
from django.contrib.auth import views as auth
from users.views import Signup, LocationRegionCreate, LocationTransports, LocationDelete, TwitterAuth, TripRegionCreate, TripDelete, TripView

location_patterns = [
    url('^$', LocationTransports.as_view(), name='location-transports'),
    url('^delete/$', LocationDelete.as_view(), name='location-delete'),
]

trip_patterns = [
    url('^$', TripView.as_view(), name='trip'),
    url('^delete/$', TripDelete.as_view(), name='trip-delete'),
]

urlpatterns = (

    # Base user
    url('^signup/$', Signup.as_view(), name='signup'),
    url('^login/$', auth.login, name='login'),
    url('^logout/$', auth.logout, name='logout'),

    # Oauth
    url('^twitter/$', TwitterAuth.as_view(), name='oauth-twitter'),

    # User locations
    url('^location/(?P<region>\w+)/new/$', LocationRegionCreate.as_view(), name='location-region-create'),
    url('^location/(?P<pk>\d+)/', include(location_patterns)),

    # User trips
    url('^trip/(?P<region>\w+)/new/$', TripRegionCreate.as_view(), name='trip-region-create'),
    url('^trip/(?P<pk>\d+)/', include(trip_patterns)),
)

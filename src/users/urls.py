from django.conf.urls import url, include
from django.contrib.auth import views as auth
from users.views import Signup, LocationCreate, LocationTransports, LocationDelete

location_patterns = [
    url('^$', LocationTransports.as_view(), name='location-transports'),
    url('^delete/$', LocationDelete.as_view(), name='location-delete'),
]

urlpatterns = (

    # Base user
    url('^signup/$', Signup.as_view(), name='signup'),
    url('^login/$', auth.login, name='login'),
    url('^logout/$', auth.logout, name='logout'),

    # User locations
    url('^location/new/$', LocationCreate.as_view(), name='location-create'),
    url('^location/(?P<pk>\d+)/', include(location_patterns)),
)

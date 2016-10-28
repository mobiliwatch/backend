from django.conf.urls import url
from django.contrib.auth import views as auth
from users.views import Signup, LocationCreate, LocationTransports

urlpatterns = (

    # Base user
    url('^signup/$', Signup.as_view(), name='signup'),
    url('^login/$', auth.login, name='login'),
    url('^logout/$', auth.logout, name='logout'),

    # User locations
    url('^location/new/$', LocationCreate.as_view(), name='location-create'),
    url('^location/(?P<pk>\d+)/$', LocationTransports.as_view(), name='location-transports'),
)

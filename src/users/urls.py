from django.conf.urls import url
from django.contrib.auth import views as auth
from users.views import Signup

urlpatterns = (
    url('^signup/$', Signup.as_view(), name='signup'),
    url('^login/$', auth.login, name='login'),
    url('^logout/$', auth.logout, name='logout'),
)

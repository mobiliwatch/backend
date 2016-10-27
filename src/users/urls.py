from django.conf.urls import url
from django.contrib.auth import views as auth

urlpatterns = (
    url('^login/$', auth.login, name='login'),
    url('^logout/$', auth.logout, name='logout'),
)

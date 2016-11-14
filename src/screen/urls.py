from django.conf.urls import url
from screen.views import ScreenCreate, ScreenDetails

urlpatterns = (

    url('^new/$', ScreenCreate.as_view(), name='screen-create'),
    url('^(?P<slug>[\w\-]+)/$', ScreenDetails.as_view(), name='screen'),

)

from django.conf.urls import url, include
from screen.views import ScreenCreate, ScreenDetails, ScreenDelete

screen_patterns = [
    url('^$', ScreenDetails.as_view(), name='screen'),
    url('^delete/$', ScreenDelete.as_view(), name='screen-delete'),
]

urlpatterns = (

    url('^new/$', ScreenCreate.as_view(), name='screen-create'),
    url('^(?P<slug>[\w\-]+)/', include(screen_patterns)),

)

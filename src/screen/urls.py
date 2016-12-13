from django.conf.urls import url, include
from screen.views import ScreenCreate, ScreenDetails, ScreenDelete, ScreenPreview

screen_patterns = [
    url('^$', ScreenDetails.as_view(), name='screen'),
    url('^preview.png$', ScreenPreview.as_view(), name='screen-preview'),
    url('^delete/$', ScreenDelete.as_view(), name='screen-delete'),
]

urlpatterns = (

    url('^new/$', ScreenCreate.as_view(), name='screen-create'),
    url('^(?P<slug>[\w\-]+)/', include(screen_patterns)),

)

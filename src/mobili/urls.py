from django.conf.urls import url, include
from django.contrib import admin
from mobili.views import Help, Home

urlpatterns = [
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^user/', include('users.urls')),
    url(r'^screen/', include('screen.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^help/(?P<slug>\w+)/$', Help.as_view(), name='help'),
    url(r'^help/?$', Help.as_view(), name='help-home', kwargs={'slug' : 'home'}),

    # Home page
    url(r'^$', Home.as_view(), name='home'),
]

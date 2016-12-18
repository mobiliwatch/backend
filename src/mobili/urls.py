from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib import admin
from mobili.views import HelpView

urlpatterns = [
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^user/', include('users.urls')),
    url(r'^screen/', include('screen.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^help/(?P<slug>\w+)/$', HelpView.as_view(), name='help'),
    url(r'^help/?$', HelpView.as_view(), name='help-home', kwargs={'slug' : 'home'}),

    # Home page
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
]

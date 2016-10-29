from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = [
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^user/', include('users.urls')),
    url(r'^admin/', admin.site.urls),

    # Home page
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
]

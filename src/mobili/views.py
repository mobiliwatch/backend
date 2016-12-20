from django.views.generic import TemplateView
from django.http import Http404
from django.core.cache import cache
from django.conf import settings
from screen.models import Screen


class Home(TemplateView):
    """
    Display home page
     * dashboard when authenticated
     * welcome when anonymous
    """
    def get_template_names(self):
        if self.request.user.is_authenticated():
            return 'home/main.html'
        return 'welcome.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(Home, self).get_context_data(*args, **kwargs)
        ctx['demo_url'] = self.get_demo_url()
        return ctx

    def get_demo_url(self):
        """
        Load demo screen shared url
        """
        if settings.SCREEN_DEMO_ID is None:
            return None
        try:
            screen = Screen.objects.get(pk=settings.SCREEN_DEMO_ID)
            return screen.frontend_shared_url
        except Screen.DoesNotExist:
            return None

class Help(TemplateView):
    """
    Load rendered pages from cache
    """
    template_name = 'help.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(Help, self).get_context_data(*args, **kwargs)
        ctx.update(self.get_help(self.kwargs['slug']))
        return ctx

    def get_help(self, slug):
        """
        Load help content from cache
        """

        # Load page
        cache_key = 'help:{}'.format(slug)
        content = cache.get(cache_key)
        if not content:
            raise Http404

        # Load TOC
        toc = cache.get('help-toc')

        return {
            'toc': toc,
            'slug': slug,
            'content': content,
        }

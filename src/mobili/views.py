from django.views.generic import TemplateView
from django.http import Http404
from django.core.cache import cache

class HelpView(TemplateView):
    """
    Load rendered pages from cache
    """
    template_name = 'help.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(HelpView, self).get_context_data(*args, **kwargs)
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

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache
import os
import re
import glob
import markdown

class Command(BaseCommand):
    help = 'Build all help pages'

    re_h1 = re.compile(r'<h1>(.*)</h1>')
    re_h2 = re.compile(r'<h2>(.*)</h2>')

    def handle(self, *args, **options):
        toc = []

        # Browse help file
        help_dir = os.path.realpath(os.path.join(settings.BASE_DIR, '../help'))
        for path in glob.glob(help_dir + '/*.md'):
            toc.append(self.render(path))

        # Save toc in cache
        cache.set('help-toc', toc)

    def render(self, path):
        # Build cache key
        slug = os.path.basename(path)
        if slug.endswith('.md'):
            slug = slug[:-3]
        cache_key = 'help:{}'.format(slug)
        print('Rendering: {}'.format(cache_key))

        # Render
        with open(path) as f:
            output = markdown.markdown(f.read())

        cache.set(cache_key, output)

        # Parse H1/H2
        out = {
            'slug' : slug,
        }
        title = self.re_h1.search(output)
        if title is None:
            out['title'] = slug
        else:
            out['title'] = title.group(1)
        out['paragraphs'] = self.re_h2.findall(output)

        return out

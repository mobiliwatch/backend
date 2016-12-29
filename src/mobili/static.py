from django.core.cache import cache
from django.conf import settings
import os.path
import glob
import markdown
import re

CACHE_MASK = 'pages:{}:{}'
TIMEOUT = 3 * 3600


class Pages(object):
    """
    Static pages from markdown file
    using cache to skip FS access
    """
    re_corpus = re.compile(r'(\d+)-([\w\-]+).md')
    re_h1 = re.compile(r'<h1>(.*)</h1>')
    re_h2 = re.compile(r'<h2>(.*)</h2>')

    def __init__(self, prefix):
        """
        Load available contents from cache then FS
        """
        self.prefix = prefix
        self.key_corpus = CACHE_MASK.format(self.prefix, '__corpus__')
        self.key_toc = CACHE_MASK.format(self.prefix, '__toc__')
        self.corpus = cache.get(self.key_corpus) or self.build_corpus()
        self.toc = cache.get(self.key_toc) or self.build_toc()

    def build_corpus(self):
        """
        Initialize corpus from FS
        """
        directory = os.path.realpath(os.path.join(settings.BASE_DIR, '..', self.prefix))
        out = {}
        for path in glob.glob(directory + '/*.md'):

            # Extract slug & position
            res = self.re_corpus.match(os.path.basename(path))
            if res is None:
                raise Exception('Invalid slug format {}'.format(path))

            # Save them in corpus
            position, slug = res.groups()
            position = int(position)
            out[slug] = (path, position)

        # Save in cache
        cache.set(self.key_corpus, out, TIMEOUT)

        return out

    def has(self, slug):
        """
        Check we have a page in corpus
        """
        return slug in self.corpus

    def render(self, slug):
        """
        Render a page from corpus
        Check cache first, fallback to rendering
        """
        assert self.has(slug)
        path, position = self.corpus[slug]

        # Check cache
        cache_key = CACHE_MASK.format(self.prefix, slug)
        html = cache.get(cache_key)
        if html is not None:
            return html

        # Render & cache html
        with open(path) as f:
            html = markdown.markdown(f.read())
        cache.set(cache_key, html, TIMEOUT)

        print('rendered {}'.format(slug))

        # Toc
        self.update_toc(slug, position, html)

        return html

    def build_toc(self):
        """
        Build initial Full pages & TOC
        """
        self.toc = {}
        for slug in self.corpus:
            self.render(slug)

        return self.toc

    def update_toc(self, slug, position, html):
        """
        Update TOC with new infos from rendered page
        """
        # Use toc without current item
        toc = [i for i in self.toc if i['slug'] != slug]

        # Parse H1/H2 to update TOC
        page = {
            'slug' : slug,
            'position' : position,
        }
        title = self.re_h1.search(html)
        if title is None:
            page['title'] = slug
        else:
            page['title'] = title.group(1)
        page['paragraphs'] = self.re_h2.findall(html)
        toc.append(page)

        # Sort TOC by position
        self.toc = sorted(toc, key=lambda x : x['position'])

        # Save in cache
        cache.set(self.key_toc, self.toc, TIMEOUT)

    def cleanup(self):
        """
        Delete corpus, toc and pages
        """
        # Pages
        for slug in self.corpus:
            cache_key = CACHE_MASK.format(self.prefix, slug)
            cache.delete(cache_key)

        # Corpus & toc
        cache.delete(self.key_toc)
        cache.delete(self.key_corpus)

from django.core.cache import cache
import requests
import hashlib
import json

class CachedApi(object):
    timeout = 3*3600

    def __init__(self, use_cache=True):
        self.use_cache = use_cache

    def build_key(self, key_parts):
        h = hashlib.md5(key_parts.encode('utf-8')).hexdigest()
        return 'api:{}'.format(h)

    def get(self, key_parts):
        """
        Retrieve from cache
        """
        cache_key = self.build_key(key_parts)
        return cache.get(cache_key)

    def store(self, key_parts, data):
        """
        Store in cache
        """
        cache_key = self.build_key(key_parts)
        cache.set(cache_key, data, self.timeout)

    def request(self, path=None, params={}, url=None):
        """
        Cached requests
        """
        assert (path is None) ^ (url is None), \
            'You need to use either a path or url'

        # Build unique query hash
        if url is None:
            url = '{}/{}'.format(self.API_URL, path)
        payload = url + '\n' + json.dumps(params, indent=4, sort_keys=True)

        # Use cache
        if self.use_cache:
            cached_data = self.get(payload)
            if cached_data:
                return cached_data

        # Make request
        resp = requests.get(url, params=params, timeout=self.timeout)
        if not resp.ok:
            print(resp.content)
            raise Exception('Invalid resp {} on {}'.format(resp.status_code, url))

        # Save in cache
        data = resp.json()
        self.store(payload, data)

        return data

from django.core.cache import cache
import requests
import hashlib
import json
import os

class CachedApi(object):

    def __init__(self, use_cache=True):
        self.cache_dir = './cache' # TODO
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.use_cache = use_cache

    def request(self, path, params={}):
        """
        Cached requests
        """

        # Build unique query hash
        url = '{}/{}'.format(self.API_URL, path)
        payload = url + '\n' + json.dumps(params, indent=4, sort_keys=True)
        h = hashlib.md5(payload.encode('utf-8')).hexdigest()
        cache_key = 'api:{}'.format(h)

        # Use cache
        if self.use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        # Make request
        resp = requests.get(url, params=params)
        if not resp.ok:
            print(resp.content)
            raise Exception('Invalid resp {} on {}'.format(resp.status_code, url))

        # Save in cache
        data = resp.json()
        cache.set(cache_key, data, 12*3600)

        return data

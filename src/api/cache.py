import requests
import json
import hashlib
import os

class CachedApi(object):

    def __init__(self):
        self.cache_dir = './cache' # TODO
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.use_cache = True

    def request(self, path, params={}):
        """
        Cached requests
        """

        # Build unique query hash
        url = '{}/{}'.format(self.API_URL, path)
        payload = url + '\n' + json.dumps(params, indent=4, sort_keys=True)
        h = hashlib.md5(payload.encode('utf-8')).hexdigest()
        cache_path = os.path.join(self.cache_dir, '{}.json'.format(h))

        # Use cache
        if self.use_cache and os.path.exists(cache_path):
            return json.load(open(cache_path))

        # Make request
        resp = requests.get(url, params=params)
        if not resp.ok:
            print(resp.content)
            raise Exception('Invalid resp {} on {}'.format(resp.status_code, url))

        # Save in cache
        with open(cache_path, 'wb') as f:
            f.write(resp.content)

        return resp.json()

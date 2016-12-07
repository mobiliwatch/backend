import requests
import base64
from django.conf import settings

class Twitter(object):
    API_URL = 'https://api.twitter.com'

    def __init__(self):
        self.token = self.auth()

    def auth(self):
        """
        Authenticate with app credentials
        No user context
        """
        token = base64.b64encode('{}:{}'.format(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
        ).encode('utf-8')).decode('utf-8')
        url = self.API_URL + '/oauth2/token'
        headers = {
            'Authorization' : 'Basic {}'.format(token),
        }
        data = {
            'grant_type' : 'client_credentials',
        }
        resp = requests.post(url, headers=headers, data=data)
        if not resp.ok:
            raise Exception('Invalid twitter Auth {} : {}'.format(resp.status_code, resp.content))
        auth = resp.json()
        if auth['token_type'] != 'bearer':
            raise Exception('Invalid token type {}'.format(auth['token_type']))

        return auth['access_token']

    def search_tweets(self, terms, since_id=None):
        """
        Search in tweets, using terms & last tweet id (optional)
        """
        url = self.API_URL + '/1.1/search/tweets.json'
        headers = {
            'Authorization' : 'Bearer {}'.format(self.token),
        }
        params = {
            'q' : terms,
        }
        if since_id is None:
            params['count'] = 10
        else:
            params['since_id'] = since_id
        resp = requests.get(url, headers=headers, params=params)
        if not resp.ok:
            raise Exception('Invalid search response {} : {}'.format(resp.status_code, resp.content))

        return resp.json()

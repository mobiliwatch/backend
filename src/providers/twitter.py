import requests
import base64
import oauth2 as oauth
import cgi
from django.conf import settings

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHENTICATE_URL = 'https://api.twitter.com/oauth/authenticate'

class Twitter(object):
    API_URL = 'https://api.twitter.com'

    def __init__(self):
        self.consumer = oauth.Consumer(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET
        )

    def build_oauth_url(self):
        """
        Build the oauth url with a One time token
        A secret token has to be stored in the session
        for next step check
        """
        client = oauth.Client(self.consumer)

        # Step 1. Get a request token from Twitter.
        resp, content = client.request(REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response from Twitter.")

        # Step 2. Store the request token in a session for later use.
        token = dict(cgi.parse_qsl(content))

        # Step 3. Redirect the user to the authentication URL.
        url = '{}?oauth_token={}'.format(AUTHENTICATE_URL, token[b'oauth_token'].decode('utf-8'))
        return url, token[b'oauth_token_secret'].decode('utf-8')

    def check_oauth_token(self, token, token_secret, verifier):
        """
        Second step of oauth authentication
        Exchange short lived token for the long lasting one
        """
        # Step 1. Use the request token in the session to build a new client.
        token = oauth.Token(token, token_secret)
        token.set_verifier(verifier)
        client = oauth.Client(self.consumer, token)

        # Step 2. Request the authorized access token from Twitter.
        resp, content = client.request(ACCESS_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response from Twitter.")

        return dict(cgi.parse_qsl(content))

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

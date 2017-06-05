from django.views.generic import CreateView, DetailView, DeleteView, View
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth import login
from providers import Twitter
from users.forms import UserCreationForm, LocationCreationForm, TripCreationForm
from users.models import User
from users.mixins import ObjectRegionCreate, LocationMixin, TripMixin

class Signup(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        # TODO: use region-create
        return reverse('location-region-create', args=('isere',))

    def form_valid(self, form):
        # Create user & build redirect
        out = super(Signup, self).form_valid(form)

        # Login user
        login(self.request, self.object)

        return out

class LocationRegionCreate(ObjectRegionCreate):
    """
    Create a new Location in a region
    """
    form_class = LocationCreationForm
    template_name = 'location/create.html'

    def get_success_url(self, location):
        return HttpResponseRedirect(reverse('location-transports', args=(location.pk, )))

class LocationTransports(LocationMixin, DetailView):
    """
    Manage transports around a location
    """
    template_name = 'location/transports.html'

class LocationDelete(LocationMixin, DeleteView):
    """
    Delete a location
    """
    template_name = 'location/delete.html'

    def get_success_url(self):
        return reverse('home')

class TripRegionCreate(ObjectRegionCreate):
    """
    Create a new trip in a region
    """
    form_class = TripCreationForm
    template_name = 'trip/create.html'

    def get_form_kwargs(self, *args, **kwargs):
        ctx = super().get_form_kwargs(*args, **kwargs)
        region = self.get_region().slug
        ctx['locations'] = self.request.user.locations.filter(region=region)
        return ctx

    def get_success_url(self, trip):
        return HttpResponseRedirect(reverse('trip', args=(trip.pk, )))

class TripView(TripMixin, DetailView):
    """
    View a trip
    """
    template_name = 'trip/view.html'

class TripDelete(TripMixin, DeleteView):
    """
    Delete a trip
    """
    template_name = 'trip/delete.html'

    def get_success_url(self):
        return reverse('home')

class TwitterAuth(LoginRequiredMixin, View):
    """
    Authenticate user with Twitter Oauth flow
    """

    def get(self, *args, **kwargs):
        tw = Twitter()
        session_key = 'twitter.oauth'
        if 'oauth_token' in self.request.GET and 'oauth_verifier' in self.request.GET:
            # Check oauth token
            secret = self.request.session.get(session_key)
            if not secret:
                raise Exception('Missing secret in session')
            conf = tw.check_oauth_token(
                self.request.GET['oauth_token'],
                secret,
                self.request.GET['oauth_verifier']
            )

            # Save token on user
            self.request.user.twitter_token = conf[b'oauth_token'].decode('utf-8')
            self.request.user.twitter_secret = conf[b'oauth_token_secret'].decode('utf-8')
            self.request.user.save()

            # Go to home
            redirect_url = reverse('home')
        else:
            # Calc new auth url
            redirect_url, secret = tw.build_oauth_url()

            # Store in session secret twitter token
            self.request.session[session_key] = secret

        return HttpResponseRedirect(redirect_url)

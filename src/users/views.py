from django.views.generic import CreateView, DetailView, DeleteView, ListView, View
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth import login
import region
from providers import Twitter
from users.forms import UserCreationForm, LocationCreationForm
from users.models import User

class Signup(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse('location-create')

    def form_valid(self, form):
        # Create user & build redirect
        out = super(Signup, self).form_valid(form)

        # Login user
        login(self.request, self.object)

        return out

class LocationCreate(LoginRequiredMixin, ListView):
    """
    List regions available to create a location
    """
    template_name = 'location/regions.html'
    context_object_name = 'regions'

    def get_queryset(self):
        # Load all regions
        return region.all()


class LocationRegionCreate(LoginRequiredMixin, CreateView):
    """
    Create a new Location in a region
    """
    form_class = LocationCreationForm
    template_name = 'location/create.html'

    def get_region(self):
        """
        Load specified region
        """
        try:
            return region.get(self.kwargs['region'])
        except:
            raise Http404

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['region'] = self.get_region()
        return ctx

    def form_valid(self, form):
        # Assign user & region
        location = form.save(commit=False)
        location.region = self.get_region().slug
        location.user = self.request.user
        location.save()

        return HttpResponseRedirect(reverse('location-transports', args=(location.pk, )))

class LocationMixin(LoginRequiredMixin):
    """
    Access a location from user
    """
    context_object_name = 'location'

    def get_queryset(self):
        return self.request.user.locations.all()

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

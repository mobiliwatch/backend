from django.views.generic import CreateView, DetailView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth import login
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

class LocationCreate(LoginRequiredMixin, CreateView):
    """
    Create a new Location
    """
    form_class = LocationCreationForm
    template_name = 'location/create.html'

    def form_valid(self, form):
        # Assign user
        location = form.save(commit=False)
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

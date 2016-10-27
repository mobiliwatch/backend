from django.views.generic import CreateView
from django.urls import reverse
from django.contrib.auth import login
from users.forms import UserCreationForm
from users.models import User

class Signup(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        # TODO: redirect to location creator
        return reverse('home')

    def form_valid(self, form):
        # Create user & build redirect
        out = super(Signup, self).form_valid(form)

        # Login user
        login(self.request, self.object)

        return out

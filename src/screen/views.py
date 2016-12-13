from django.views.generic import CreateView, DetailView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db import transaction
from screen.forms import ScreenCreationForm


class ScreenCreate(LoginRequiredMixin, CreateView):
    """
    Create a new screen
    """
    form_class = ScreenCreationForm
    template_name = 'screen/create.html'

    def get_form_kwargs(self, *args, **kwargs):
        kw = super(ScreenCreate, self).get_form_kwargs(*args, **kwargs)
        kw['user'] = self.request.user
        return kw

    def form_valid(self, form):

        # Build screen with widgets
        # inside a transaction
        with transaction.atomic():
            screen = form.save(commit=False)
            screen.user = self.request.user
            screen.slugify()
            screen.save()
            screen.clone_widgets(form.cleaned_data['screen_template'], form.cleaned_data['location'])

        # Redirect to screen view
        return HttpResponseRedirect(screen.frontend_url)

class ScreenMixin(LoginRequiredMixin):
    """
    Load a screen
    """
    context_object_name = 'screen'

    def get_queryset(self):
        return self.request.user.screens.all()


class ScreenDetails(ScreenMixin, DetailView):
    """
    View a screen
    """
    template_name = 'screen/details.html'


class ScreenDelete(ScreenMixin, DeleteView):
    """
    Delete a screen
    """
    template_name = 'screen/delete.html'

    def get_success_url(self):
        return reverse('home')

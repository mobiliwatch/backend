from django.views.generic import CreateView
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
import region

class ObjectRegionCreate(LoginRequiredMixin, CreateView):
    """
    Create an object attached to a user and a region
    """
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
        x = form.save(commit=False)
        x.region = self.get_region().slug
        x.user = self.request.user
        x.save()

        return self.get_success_url(x)

class LocationMixin(LoginRequiredMixin):
    """
    Access a location from user
    """
    context_object_name = 'location'

    def get_queryset(self):
        return self.request.user.locations.all()

class TripMixin(LoginRequiredMixin):
    """
    Access a trip from user
    """
    context_object_name = 'trip'

    def get_queryset(self):
        return self.request.user.trips.all()

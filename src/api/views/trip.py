from rest_framework.generics import RetrieveAPIView
from users.models import Trip
from django.http import Http404
from api.serializers import TripSerializer

class TripMixin(object):
    """
    Load trip from id in url
    """
    def get_trip(self):
        try:
            return self.request.user.trips.get(id=self.kwargs['pk'])
        except Trip.DoesNotExist:
            raise Http404

class TripDetails(TripMixin, RetrieveAPIView):
    """
    Get details for a trip
    """
    serializer_class = TripSerializer

    def get_queryset(self):
        return self.request.user.trips.all()

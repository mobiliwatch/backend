from rest_framework.generics import ListAPIView
from api.serializers import CitySerializer
from transport.models import City


class CityList(ListAPIView):
    """
    List available cities
    """
    queryset = City.objects.filter(position__isnull=False)
    serializer_class = CitySerializer

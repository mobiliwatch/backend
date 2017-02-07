from providers import OSMRouter
from users.models import Location

r = OSMRouter()
r.walk_trip(Location.objects.get(pk=1).point, Location.objects.get(pk=3).point)

from users import models


def async_location_stop_update(message):
    """
    Asynchronously update a location stop
    metadata (distance + duration)
    """
    ls = models.LocationStop.objects.get(id=message.content['location_stop'])
    ls.update_metadata()
    ls.save()

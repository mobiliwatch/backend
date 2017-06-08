from channels.auth import channel_session_user, channel_session_user_from_http
from channels import Channel
from users import models
import logging

logger = logging.getLogger('users.consumers')

def trip_required(func):
    """
    Check trip from id is available
    to connected user from WebSocket
    """
    def wrapper(message, pk, token=None):

        try:
            # Authenticated
            message.trip = message.user.trips.get(pk=pk)
        except Exception as e:
            logger.error('Trip {} is required: {}'.format(pk , e))
            return

        return func(message, pk, token)
    return wrapper

def async_location_stop_update(message):
    """
    Asynchronously update a location stop
    metadata (distance + duration)
    """
    ls = models.LocationStop.objects.get(id=message.content['location_stop'])
    ls.update_metadata()
    ls.save()

def async_trip_init(message):
    """
    Asynchronously init a trip
    so that we don't lock any process
    Connected to channel trip.init
    """
    trip = models.Trip.objects.get(id=message.content['trip'])

    # Send trip solution
    trip.send_ws_update()

@channel_session_user_from_http
@trip_required
def ws_trip_add(message, slug, token=None):
    """
    Connected to websocket.connect
    """

    # Use this channel for this trip
    message.trip.ws_group.add(message.reply_channel)

    # Async screen init
    Channel('trip.init').send({
        'trip' : message.trip.id,
    })

@channel_session_user
@trip_required
def ws_trip_message(message, slug, token=None):
    """
    Connected to websocket.receive
    """

    # Should not be used in our workflow...
    print('Received WS Msg', message)

@channel_session_user
@trip_required
def ws_trip_disconnect(message, slug, token=None):
    """
    Connected to websocket.disconnect
    """

    # Do not use this channel anymore for this trip
    message.trip.ws_group.discard(message.reply_channel)

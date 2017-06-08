from channels.routing import route, include
from screen.consumers import (
    ws_screen_add, ws_screen_message, ws_screen_disconnect,
    async_screen_init, async_screen_widget
)
from users.consumers import (
    ws_trip_add, ws_trip_message, ws_trip_disconnect,
    async_trip_init, async_location_stop_update
)

screen_routing = [
    # Websockets for a specific screen
    route("websocket.connect", ws_screen_add),
    route("websocket.receive", ws_screen_message),
    route("websocket.disconnect", ws_screen_disconnect),
]

trip_routing = [
    # Websockets for a specific screen
    route("websocket.connect", ws_trip_add),
    route("websocket.receive", ws_trip_message),
    route("websocket.disconnect", ws_trip_disconnect),
]


channel_routing = [
    # Screen : Authenticated and Anonymous with token
    include(screen_routing, path=r"^/screen/(?P<slug>[\w\-]+)/$"),
    include(screen_routing, path=r"^/screen/(?P<slug>[\w\-]+)/shared/(?P<token>[\w\-]+)/$"),

    # Trip
    include(trip_routing, path=r"^/trip/(?P<pk>\d+)/$"),

    # Internal routing
    route('screen.init', async_screen_init),
    route('screen.widget', async_screen_widget),
    route('locationstop.update', async_location_stop_update),
    route('trip.init', async_trip_init),
]

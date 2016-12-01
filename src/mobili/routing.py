from channels.routing import route, include
from screen.consumers import ws_screen_add, ws_screen_message, ws_screen_disconnect, async_screen_init, async_screen_widget
from users.consumers import async_location_stop_update

screen_routing = [
    # Websockets for a specific screen
    route("websocket.connect", ws_screen_add),
    route("websocket.receive", ws_screen_message),
    route("websocket.disconnect", ws_screen_disconnect),
]


channel_routing = [
    # Authenticated version
    include(screen_routing, path=r"^/screen/(?P<slug>[\w\-]+)/$"),

    # Anonymous version
    include(screen_routing, path=r"^/screen/(?P<slug>[\w\-]+)/shared/(?P<token>[\w\-]+)/$"),

    # Internal routing
    route('screen.init', async_screen_init),
    route('screen.widget', async_screen_widget),
    route('locationstop.update', async_location_stop_update),
]

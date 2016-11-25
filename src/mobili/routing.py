from channels.routing import route, include
from screen.consumers import ws_screen_add, ws_screen_message, ws_screen_disconnect, async_screen_init

screen_routing = [
    # Websockets for a specific screen
    route("websocket.connect", ws_screen_add),
    route("websocket.receive", ws_screen_message),
    route("websocket.disconnect", ws_screen_disconnect),
]


channel_routing = [
    include(screen_routing, path=r"^/screen/(?P<slug>[\w\-]+)/$"),

    # Internal routing
    route('screen_init', async_screen_init),
]

from channels.auth import channel_session_user, channel_session_user_from_http
from channels import Group
import logging

logger = logging.getLogger('screen.consumers')


def screen_required(func):
    """
    Check screen from slug is available
    to connected user from WebSocket
    """
    def wrapper(message, slug):
        try:
            message.screen = message.user.screens.get(slug=slug)
        except Exception as e:
            logger.error('Screen {} is required: {}'.format(slug, e))
            return

        return func(message, slug)
    return wrapper

def async_screen_init(message):
    """
    Asynchronously init a screen
    so that we don't lock any process
    Connected to channel screen_init
    """
    screen = message.content['screen']

    # Mark this screen as active
    if not message.screen.active:
        message.screen.active = True
        message.screen.save()

    # Send initial update for widgets
    for widget in screen.all_widgets:
        widget.send_ws_update()


@channel_session_user_from_http
@screen_required
def ws_screen_add(message, slug):
    """
    Connected to websocket.connect
    """

    # Use this channel for this screen
    message.screen.ws_group.add(message.reply_channel)

    # Async screen init
    # TODO
    Group('screen_init').send({
        'screen' : message.screen,
    })

@channel_session_user
@screen_required
def ws_screen_message(message, slug):
    """
    Connected to websocket.receive
    """
    # Mark this screen as active
    if not message.screen.active:
        message.screen.active = True
        message.screen.save()

    # Should not be used in our workflow...
    print('Received WS Msg', message)

@channel_session_user
@screen_required
def ws_screen_disconnect(message, slug):
    """
    Connected to websocket.disconnect
    """
    # Mark this screen as inactive
    if not message.screen.active:
        message.screen.active = False
        message.screen.save()

    # Do not use this channel anymore for this screen
    message.screen.ws_group.discard(message.reply_channel)

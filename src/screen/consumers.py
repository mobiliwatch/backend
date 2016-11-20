from channels.auth import channel_session_user, channel_session_user_from_http
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

@channel_session_user_from_http
@screen_required
def ws_screen_add(message, slug):
    """
    Connected to websocket.connect
    """

    # Use this channel for this screen
    message.screen.ws_group.add(message.reply_channel)

    # Mark this screen as active
    if not message.screen.active:
        message.screen.active = True
        message.screen.save()

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

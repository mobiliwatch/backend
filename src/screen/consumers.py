from channels import Group

# Connected to websocket.connect
def ws_add(message):
    Group("chat").add(message.reply_channel)
    Group("chat").send({
        "text": "HELLO new user",
    })

# Connected to websocket.receive
def ws_message(message):
    Group("chat").send({
        "text": "[reply pong] %s" % message.content['text'],
    })

# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)

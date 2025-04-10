# chat/routing.py
from django.urls import re_path

from . import consumers
from api import consumers as api_consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/private/(?P<receiver_name>\w+)/$', consumers.Consumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(r"transaction/complete/$", api_consumers.Consumer.as_asgi()),
]

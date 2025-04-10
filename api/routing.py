# from django.urls import re_path

# from .api import consumers

# # websocket_urlpatterns = [
# #     # We use re_path() due to limitations in URLRouter.
# #     re_path(r"ws/job-status/$", consumers.Consumer.as_asgi()),
# # ],
# websocket_urlpatterns = [
#     re_path(r'ws/hey/(?P<receiver_name>\w+)/$', consumers.Consumer.as_asgi()),
#     re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
# ]

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyanase_api.settings')
django.setup()
# consumers.py


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"group_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user = text_data_json['user']
        message = text_data_json['message']

        # Save the message to the database
        Message.objects.create(user=user, content=message)

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': user,
                'message': message
            }
        )

    async def chat_message(self, event):
        user = event['user']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'user': user,
            'message': message
        }))


# consumers.py
class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the receiver_name from the URL kwargs
        self.receiver_name = self.scope['url_route']['kwargs']['receiver_name']

        # Assuming the logged-in user has a username (or use the user ID)
        self.sender_name = self.scope['user'].username

        # Create the private room group name
        # dynamically based on sender and receiver
        self.room_group_name = f"private_{min(self.sender_name, self.receiver_name)}_{max(self.sender_name, self.receiver_name)}"

        # Join the private room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Check for any unread messages and send them to the receiver
        messages = Message.objects.filter(receiver=self.receiver, read=False)
        for msg in messages:
            await self.send(text_data=json.dumps({
                "message": msg.content,
                "sender": msg.sender.username,
            }))

        # Mark these messages as "read"
        messages.update(read=True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Store the message in the database (as before)
        Message.objects.create(
            sender=self.sender, receiver=self.receiver, content=message)

        # Send to receiver if they are online
        if self.receiver.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.sender.username,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))


# class Consumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         print(message)

#         await self.send(text_data=json.dumps({
#             'message': message
#         }))

#     def send(self, event):
#         print("EVENT TRIGERED")
#         # Receive message from room group
#         message = event['message']
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'type': 'message',
#             'message': message
#         }))

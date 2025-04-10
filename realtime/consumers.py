import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyanase_api.settings')
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import Message
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.db.models import Q

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
        sender = self.scope['user']

        # Create the private room group name
        # dynamically based on sender and receiver
        self.room_group_name = f"private_{min(sender.pk, int(self.receiver_name))}_{max(sender.pk, int(self.receiver_name))}"

        # Join the private room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Check for any unread messages and send them to the receiver
        messages = await self.get_messages(self.receiver_name, sender.pk)

        for msg in messages:
            sender_username = await sync_to_async(lambda: msg.sender.username)()
            await self.send(text_data=json.dumps({
                "message": msg.content,
                "sender": sender_username,
                'created': msg.created.strftime('%Y-%m-%d %H:%M:%S')
            }))

        # Mark these messages as "read"
        # await self.mark_messages_as_read(messages)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender = text_data_json['sender']
        print('SENDER: ', sender, 'RECEIVER: ', self.receiver_name, 'MESSAGE: ', message)

        # Store the message in the database (as before)
        await self.store_message(sender, self.receiver_name, message)

        # Send the message to the receiver if they are online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))

    @sync_to_async
    def get_messages(self, receiver_name, sender_name):
        return list(
            Message.objects.filter(
                Q(sender=sender_name, receiver=receiver_name) | Q(sender=receiver_name, receiver=sender_name), read=False
            )
        )

    @sync_to_async
    def mark_messages_as_read(self, messages):
        # Mark the messages as read
        messages.update(read=True)

    @sync_to_async
    def store_message(self, sender_name, receiver_name, message):
        # Store a new message in the database
        sender = User.objects.get(pk=sender_name)
        receiver = User.objects.get(pk=receiver_name)
        return Message.objects.create(sender=sender, receiver=receiver, content=message)


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

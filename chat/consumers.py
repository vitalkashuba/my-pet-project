import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

"""AsyncWebsocketConsumer бібліотека о чьом """
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Приєднатися до групи кімнати
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Повідомити всіх про підключення
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.user.username,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'username': self.user.username,
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return

            # Зберегти в БД
            message = await self.save_message(content)

            # Надіслати всім у кімнаті
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'content': content,
                    'username': self.user.username,
                    'timestamp': message.created_at.strftime('%H:%M'),
                }
            )

    # --- Обробники подій групи ---

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'content': event['content'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'is_own': event['username'] == self.user.username,
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system',
            'content': f"{event['username']} приєднався до чату",
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system',
            'content': f"{event['username']} покинув чат",
        }))

    # --- DB helpers ---

    @database_sync_to_async
    def save_message(self, content):
        from chat.models import Room, Message
        room = Room.objects.get(slug=self.room_slug)
        return Message.objects.create(
            room=room,
            author=self.user,
            content=content,
        )

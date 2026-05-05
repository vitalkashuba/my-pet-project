import json
import math
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Зберігаємо активних користувачів в памʼяті: { user_id: {username, lat, lng, channel} }
active_users = {}


def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    to_rad = lambda x: x * math.pi / 180
    dlat = to_rad(lat2 - lat1)
    dlng = to_rad(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class GeoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()
        active_users[self.user.id] = {
            'username': self.user.username,
            'lat': None,
            'lng': None,
            'channel': self.channel_name,
        }

    async def disconnect(self, close_code):
        if not hasattr(self, 'user') or not self.user.is_authenticated:
            return
        active_users.pop(self.user.id, None)

        # Повідомити всіх що цей користувач пішов
        for uid, u in active_users.items():
            await self.channel_layer.send(u['channel'], {
                'type': 'send_json',
                'data': {
                    'type': 'user_left',
                    'user_id': self.user.id,
                }
            })

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'location_update':
            lat = data.get('lat')
            lng = data.get('lng')
            if lat is None or lng is None:
                return

            me = active_users.get(self.user.id, {})
            me['lat'] = lat
            me['lng'] = lng
            active_users[self.user.id] = me

            nearby = self._get_nearby(lat, lng, radius=100)

            # Надіслати поточному користувачу список тих хто поруч
            await self.send(text_data=json.dumps({
                'type': 'nearby_users',
                'users': [
                    {'user_id': uid, 'username': u['username'], 'lat': u['lat'], 'lng': u['lng']}
                    for uid, u in nearby.items()
                ]
            }))

            # Повідомити тих хто поруч про нашу позицію
            for uid, u in nearby.items():
                await self.channel_layer.send(u['channel'], {
                    'type': 'send_json',
                    'data': {
                        'type': 'user_location',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'lat': lat,
                        'lng': lng,
                    }
                })

        elif msg_type == 'private_message':
            to_id = data.get('to_user_id')
            content = data.get('content', '').strip()
            if not content or not to_id:
                return
            target = active_users.get(to_id)
            if not target:
                return
            await self.channel_layer.send(target['channel'], {
                'type': 'send_json',
                'data': {
                    'type': 'private_message',
                    'from_user_id': self.user.id,
                    'from_username': self.user.username,
                    'content': content,
                }
            })

    def _get_nearby(self, lat, lng, radius=100):
        result = {}
        for uid, u in active_users.items():
            if uid == self.user.id:
                continue
            if u['lat'] is None or u['lng'] is None:
                continue
            dist = haversine(lat, lng, u['lat'], u['lng'])
            if dist <= radius:
                result[uid] = u
        return result

    # Викликається через channel_layer.send
    async def send_json(self, event):
        await self.send(text_data=json.dumps(event['data']))

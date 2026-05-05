from django.urls import re_path
from . import consumers
from . import geo_consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_slug>[\w-]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/geo/$', geo_consumer.GeoConsumer.as_asgi()),
]

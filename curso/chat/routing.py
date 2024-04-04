from django.urls import path
from .consumers import GameConsumer

websocket_urlpatterns=[
    path('ws/room/<room_id>/',GameConsumer.as_asgi())
]
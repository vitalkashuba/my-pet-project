from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.map_view, name='map'),
    path('', views.index, name='index'),
    path('room/<slug:room_slug>/', views.room, name='room'),
    path('create/', views.create_room, name='create_room'),
    path('register/', views.register, name='register'),
]

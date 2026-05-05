from django.contrib import admin
from .models import Room, Message


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_by', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'room', 'content', 'created_at']
    list_filter = ['room']
    search_fields = ['content', 'author__username']

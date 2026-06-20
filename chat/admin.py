from django.contrib import admin
from .models import ChatRoom, Message


class MessageInline(admin.TabularInline):
    model  = Message
    extra  = 0
    fields = ('sender', 'content', 'is_read', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display  = ('pk', 'listing_title', 'buyer', 'seller', 'updated_at')
    list_filter   = ('created_at',)
    inlines       = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'content', 'is_read', 'created_at')
    list_filter  = ('is_read',)

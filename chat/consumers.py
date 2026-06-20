import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id   = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f'chat_{self.room_id}'
        self.user       = self.scope['user']

        # Chặn người không có quyền
        if not self.user.is_authenticated:
            await self.close()
            return

        room = await self.get_room(self.room_id)
        if room is None or not await self.is_member(room, self.user):
            await self.close()
            return

        # Vào group channel
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Đánh dấu tin đã đọc khi mở chat
        await self.mark_read(room, self.user)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('message', '').strip()
        if not content:
            return

        # Lưu vào DB
        msg = await self.save_message(self.room_id, self.user, content)

        # Broadcast cho cả phòng
        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':      'chat_message',
                'message':   msg['content'],
                'sender':    msg['sender'],
                'sender_id': msg['sender_id'],
                'timestamp': msg['timestamp'],
                'msg_id':    msg['id'],
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message':   event['message'],
            'sender':    event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'msg_id':    event['msg_id'],
        }))

    # ── DB helpers ───────────────────────────────────────────
    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return ChatRoom.objects.get(pk=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_member(self, room, user):
        return room.buyer == user or room.seller == user

    @database_sync_to_async
    def save_message(self, room_id, user, content):
        room = ChatRoom.objects.get(pk=room_id)
        msg  = Message.objects.create(room=room, sender=user, content=content)
        # Cập nhật updated_at phòng chat (để sort inbox)
        room.save()
        return {
            'id':        msg.pk,
            'content':   msg.content,
            'sender':    user.username,
            'sender_id': user.pk,
            'timestamp': msg.created_at.strftime('%H:%M'),
        }

    @database_sync_to_async
    def mark_read(self, room, user):
        room.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

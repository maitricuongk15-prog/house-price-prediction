from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    """
    Mỗi phòng chat gắn với 1 tin rao (listing_id).
    Gồm 2 thành viên: buyer (người hỏi) và seller (chủ tin).
    """
    listing_id  = models.IntegerField(db_index=True)
    listing_title = models.CharField(max_length=200, blank=True)
    buyer       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_as_buyer')
    seller      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_as_seller')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        # Mỗi cặp buyer-seller chỉ có 1 phòng chat cho 1 listing
        unique_together = ('listing_id', 'buyer', 'seller')
        ordering = ['-updated_at']

    def __str__(self):
        return f'Chat #{self.pk}: {self.buyer} ↔ {self.seller} | Tin #{self.listing_id}'

    def get_other_user(self, user):
        return self.seller if user == self.buyer else self.buyer

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    @property
    def room_name(self):
        return f'listing_{self.listing_id}_buyer_{self.buyer_id}'


class Message(models.Model):
    room      = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content   = models.TextField()
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.content[:40]}'

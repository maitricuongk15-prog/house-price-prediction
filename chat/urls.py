from django.urls import path
from . import views

urlpatterns = [
    path('hop-thu/',                    views.inbox,      name='inbox'),
    path('nhan-tin/<int:listing_id>/',  views.start_chat, name='start_chat'),
    path('chat/<int:room_id>/',         views.chat_room,  name='chat_room'),
]

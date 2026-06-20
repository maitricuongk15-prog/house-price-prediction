from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import ChatRoom, Message


@login_required
def start_chat(request, listing_id):
    """
    Người mua bấm 'Nhắn tin' từ trang chi tiết tin rao.
    Tạo hoặc lấy phòng chat, redirect vào room.
    """
    # Lấy thông tin listing từ predictor app
    from predictor.models import Listing
    listing = get_object_or_404(Listing, pk=listing_id)

    # Không cho tự chat với chính mình
    if request.user == listing.owner:
        return redirect('listing_detail', pk=listing_id)

    room, _ = ChatRoom.objects.get_or_create(
        listing_id=listing_id,
        buyer=request.user,
        seller=listing.owner,
        defaults={'listing_title': listing.title},
    )
    return redirect('chat_room', room_id=room.pk)


@login_required
def chat_room(request, room_id):
    """Trang chat chính với lịch sử tin nhắn."""
    room = get_object_or_404(ChatRoom, pk=room_id)

    # Chỉ buyer hoặc seller mới được vào
    if request.user not in (room.buyer, room.seller):
        return redirect('home')

    chat_messages = room.messages.select_related('sender').all()
    other         = room.get_other_user(request.user)

    # Đánh dấu đã đọc
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'chat/chat_room.html', {
        'room':          room,
        'chat_messages': chat_messages,
        'other':         other,
    })


@login_required
def inbox(request):
    """Danh sách tất cả phòng chat của user."""
    rooms = ChatRoom.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).prefetch_related('messages').select_related('buyer', 'seller')

    # Gắn thêm số tin chưa đọc
    room_data = []
    for room in rooms:
        last_msg = room.messages.last()
        unread   = room.unread_count(request.user)
        other    = room.get_other_user(request.user)
        room_data.append({
            'room':     room,
            'last_msg': last_msg,
            'unread':   unread,
            'other':    other,
        })

    return render(request, 'chat/inbox.html', {'room_data': room_data})
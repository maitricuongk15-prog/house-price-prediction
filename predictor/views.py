import joblib
import numpy as np
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, SavedListing
from .forms import PredictForm, ListingForm, RegisterForm

# ── Load model một lần khi khởi động ──────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_model', 'house_model.pkl')
_bundle = None

def get_model():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def predict_price(area, floors, bedrooms, bathrooms, city, legal_status, furniture, property_type=None):
    # Model gốc chỉ train trên nhà có phòng ở (nhà phố/biệt thự/chung cư).
    # Đất nền không có cấu trúc nhà nên dùng floors/bedrooms/bathrooms giả sẽ
    # cho kết quả sai lệch nhiều — tốt hơn là không dự đoán còn hơn dự đoán sai.
    if property_type == 'dat_nen':
        return None

    bundle = get_model()
    model      = bundle['model']
    le_city    = bundle['le_city']
    le_legal   = bundle['le_legal']
    le_furnish = bundle['le_furnish']

    # Encode (xử lý giá trị chưa gặp)
    def safe_encode(le, val):
        if val in le.classes_:
            return le.transform([val])[0]
        return 0

    # Chung cư không có "số tầng của cả toà" trong dataset gốc —
    # dùng giá trị mặc định hợp lý, kết quả mang tính tham khảo.
    floors    = floors    if floors    is not None else 1
    bedrooms  = bedrooms  if bedrooms  is not None else 0
    bathrooms = bathrooms if bathrooms is not None else 0

    city_enc    = safe_encode(le_city,    city)
    legal_enc   = safe_encode(le_legal,   legal_status)
    furnish_enc = safe_encode(le_furnish, furniture)

    X = np.array([[area, floors, bedrooms, bathrooms,
                   city_enc, legal_enc, furnish_enc]])
    return round(float(model.predict(X)[0]), 3)


# ── Trang chủ ─────────────────────────────────────────────
def home(request):
    listings = Listing.objects.filter(status='active')[:6]
    return render(request, 'predictor/home.html', {'listings': listings})


# ── Dự đoán giá ───────────────────────────────────────────
def predict(request):
    result = None
    form = PredictForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        price = predict_price(
            d['area'], d['floors'], d['bedrooms'], d['bathrooms'],
            d['city'], d['legal_status'], d['furniture'],
            d['property_type']
        )
        result = {
            'price': price,
            'city': d['city'],
            'area': d['area'],
            'property_type': d['property_type'],
        }
    return render(request, 'predictor/predict.html', {'form': form, 'result': result})


# ── Danh sách tin rao ─────────────────────────────────────
def listing_list(request):
    qs = Listing.objects.filter(status='active')

    q     = request.GET.get('q', '')
    city  = request.GET.get('city', '')
    min_p = request.GET.get('min_price', '')
    max_p = request.GET.get('max_price', '')
    min_a = request.GET.get('min_area', '')
    ptype = request.GET.get('property_type', '')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(address__icontains=q))
    if city:
        qs = qs.filter(city=city)
    if ptype:
        qs = qs.filter(property_type=ptype)
    if min_p:
        qs = qs.filter(price__gte=float(min_p))
    if max_p:
        qs = qs.filter(price__lte=float(max_p))
    if min_a:
        qs = qs.filter(area__gte=float(min_a))

    from .models import CITY_CHOICES, PROPERTY_TYPE_CHOICES
    return render(request, 'predictor/listing_list.html', {
        'listings': qs,
        'city_choices': CITY_CHOICES,
        'property_type_choices': PROPERTY_TYPE_CHOICES,
        'params': request.GET,
    })


# ── Chi tiết tin rao ──────────────────────────────────────
def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedListing.objects.filter(user=request.user, listing=listing).exists()
    related = Listing.objects.filter(city=listing.city, status='active').exclude(pk=pk)[:3]
    return render(request, 'predictor/listing_detail.html', {
        'listing': listing,
        'is_saved': is_saved,
        'related': related,
    })


# ── Đăng tin mới ──────────────────────────────────────────
@login_required
def listing_create(request):
    form = ListingForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        listing = form.save(commit=False)
        listing.owner = request.user
        # Tự động dự đoán giá ML (trả None nếu là đất nền)
        try:
            listing.predicted_price = predict_price(
                listing.area, listing.floors, listing.bedrooms, listing.bathrooms,
                listing.city, listing.legal_status, listing.furniture,
                listing.property_type
            )
        except Exception:
            listing.predicted_price = None
        listing.save()
        messages.success(request, 'Đã đăng tin thành công!')
        return redirect('listing_detail', pk=listing.pk)
    return render(request, 'predictor/listing_form.html', {'form': form, 'action': 'Đăng tin'})


# ── Sửa tin ───────────────────────────────────────────────
@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    form = ListingForm(request.POST or None, request.FILES or None, instance=listing)
    if form.is_valid():
        listing = form.save(commit=False)
        try:
            listing.predicted_price = predict_price(
                listing.area, listing.floors, listing.bedrooms, listing.bathrooms,
                listing.city, listing.legal_status, listing.furniture,
                listing.property_type
            )
        except Exception:
            listing.predicted_price = None
        listing.save()
        messages.success(request, 'Đã cập nhật tin!')
        return redirect('listing_detail', pk=listing.pk)
    return render(request, 'predictor/listing_form.html', {'form': form, 'action': 'Cập nhật'})


# ── Xoá tin ───────────────────────────────────────────────
@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.status = 'hidden'
        listing.save()
        messages.success(request, 'Đã ẩn tin rao.')
        return redirect('profile')
    return render(request, 'predictor/listing_confirm_delete.html', {'listing': listing})


# ── Lưu / bỏ lưu tin ─────────────────────────────────────
@login_required
def toggle_save(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    obj, created = SavedListing.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        obj.delete()
        messages.info(request, 'Đã bỏ lưu.')
    else:
        messages.success(request, 'Đã lưu vào danh sách yêu thích!')
    return redirect('listing_detail', pk=pk)


# ── Hồ sơ cá nhân ────────────────────────────────────────
@login_required
def profile(request):
    my_listings = Listing.objects.filter(owner=request.user).exclude(status='hidden')
    saved = SavedListing.objects.filter(user=request.user).select_related('listing')
    return render(request, 'predictor/profile.html', {
        'my_listings': my_listings,
        'saved': saved,
    })


# ── Auth ──────────────────────────────────────────────────
def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Chào mừng {user.username}!')
        return redirect('home')
    return render(request, 'predictor/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'predictor/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')

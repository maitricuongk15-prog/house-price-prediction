from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.home,             name='home'),
    path('du-doan/',                 views.predict,          name='predict'),

    # Listings
    path('nha-dat/',                 views.listing_list,     name='listing_list'),
    path('nha-dat/<int:pk>/',        views.listing_detail,   name='listing_detail'),
    path('nha-dat/dang-tin/',        views.listing_create,   name='listing_create'),
    path('nha-dat/<int:pk>/sua/',    views.listing_edit,     name='listing_edit'),
    path('nha-dat/<int:pk>/xoa/',    views.listing_delete,   name='listing_delete'),
    path('nha-dat/<int:pk>/luu/',    views.toggle_save,      name='toggle_save'),

    # Auth
    path('dang-ky/',                 views.register,         name='register'),
    path('dang-nhap/',               views.login_view,       name='login'),
    path('dang-xuat/',               views.logout_view,      name='logout'),

    # Profile
    path('ho-so/',                   views.profile,          name='profile'),
]

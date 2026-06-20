from django.contrib import admin
from .models import Listing, SavedListing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'property_type', 'city', 'price', 'predicted_price', 'status', 'owner', 'created_at')
    list_filter   = ('status', 'property_type', 'city', 'legal_status', 'furniture')
    search_fields = ('title', 'address', 'owner__username')
    readonly_fields = ('predicted_price', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(SavedListing)
class SavedListingAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'saved_at')
    list_filter  = ('saved_at',)

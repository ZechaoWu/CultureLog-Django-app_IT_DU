from django.contrib import admin
from .models import Genre, MediaItem, Review

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'release_date', 'created_by')
    list_filter = ('type', 'genres')
    search_fields = ('title', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__username', 'media_item__title')

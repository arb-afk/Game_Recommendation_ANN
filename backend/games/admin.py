from django.contrib import admin
from .models import Game, Rating, Review, Download


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['appid', 'title', 'primary_genre', 'developer', 'release_year', 'price', 'recommendations', 'created_at']
    search_fields = ['title', 'name', 'appid', 'developer', 'publisher', 'genres']
    list_filter = ['release_year', 'created_at']
    readonly_fields = ['primary_genre', 'genre_list', 'category_list', 'average_rating', 'total_downloads', 'total_reviews']
    fieldsets = (
        ('Basic Information', {
            'fields': ('appid', 'title', 'name', 'description')
        }),
        ('Release Information', {
            'fields': ('release_year', 'release_date')
        }),
        ('Game Details', {
            'fields': ('genres', 'genre_list', 'primary_genre', 'categories', 'category_list')
        }),
        ('Pricing & Stats', {
            'fields': ('price', 'recommendations', 'developer', 'publisher')
        }),
        ('User Interaction', {
            'fields': ('average_rating', 'total_downloads', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'game__title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'created_at']
    search_fields = ['user__username', 'game__title', 'content']
    list_filter = ['created_at']


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['user__username', 'game__title']


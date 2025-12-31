from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    appid = models.IntegerField(unique=True, help_text="Steam App ID")
    title = models.CharField(max_length=500, db_index=True)
    name = models.CharField(max_length=500, blank=True, help_text="Alternative name field from CSV")
    release_year = models.IntegerField(null=True, blank=True)
    release_date = models.CharField(max_length=100, blank=True, help_text="Release date as string from CSV")
    genres = models.CharField(max_length=500, blank=True, help_text="Semicolon-separated genres")
    categories = models.CharField(max_length=500, blank=True, help_text="Semicolon-separated categories")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recommendations = models.IntegerField(default=0, help_text="Number of recommendations from CSV")
    developer = models.CharField(max_length=500, blank=True)
    publisher = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True, help_text="Game description (can be added later)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-recommendations', 'title']
        indexes = [
            models.Index(fields=['appid']),
            models.Index(fields=['release_year']),
        ]
    
    def __str__(self):
        return self.title or self.name or f"Game {self.appid}"
    
    @property
    def genre_list(self):
        """Return genres as a list"""
        if self.genres:
            return [g.strip() for g in self.genres.split(';') if g.strip()]
        return []
    
    @property
    def category_list(self):
        """Return categories as a list"""
        if self.categories:
            return [c.strip() for c in self.categories.split(';') if c.strip()]
        return []
    
    @property
    def primary_genre(self):
        """Return the first genre as primary genre"""
        genres = self.genre_list
        return genres[0] if genres else 'Unknown'
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return 0.0
    
    @property
    def total_downloads(self):
        """Total downloads from users + initial recommendations count"""
        user_downloads = self.downloads.count()
        return user_downloads + self.recommendations
    
    @property
    def total_reviews(self):
        return self.reviews.count()


class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'game']
    
    def __str__(self):
        game_name = self.game.title or self.game.name or f"Game {self.game.appid}"
        return f"{self.user.username} - {game_name}: {self.rating} stars"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        game_name = self.game.title or self.game.name or f"Game {self.game.appid}"
        return f"{self.user.username} - {game_name}"


class Download(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'game']
    
    def __str__(self):
        game_name = self.game.title or self.game.name or f"Game {self.game.appid}"
        return f"{self.user.username} downloaded {game_name}"


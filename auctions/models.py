from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

#Your application should have at least three models in addition to the User model: one for auction listings, one for bids, and one for comments made on auction listings
class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.username}"
    
class Category(models.Model):
    category = models.CharField(max_length=64, unique=True)
    
    def __str__(self):
        return f"{self.category}"
    
class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.URLField(blank=True)
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0.1)])
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    category = models.ManyToManyField(Category, blank=True, related_name="categories")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} from {self.seller}"
    
    
class Bid(models.Model):
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bid")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bid} on {self.item}"
    
class Comment(models.Model):
    comment = models.TextField()
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.comment}"
    
class Watchlist(models.Model):
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watchlist")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    
    def __str__(self):
        return f"{self.user} put {self.item} into their watchlist"
    
    class Meta:
        unique_together = ["item", "user"]

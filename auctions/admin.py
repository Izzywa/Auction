from django.contrib import admin
from .models import User, Listings, Bid, Comment, Watchlist, Category

class ListingInline(admin.TabularInline):
    model = Listings
    fk_name = "seller"
    
class CommentInline(admin.TabularInline):
    model = Comment
    fk_name = "commenter"
    
class WatchlistInline(admin.TabularInline):
    model = Watchlist
    fk_name = "user"
    
class CategoryInline(admin.TabularInline):
    model = Listings.category.through
    
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name")
    inlines = [
        ListingInline, CommentInline, WatchlistInline]
    
class ListingsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "seller")
    filter_horizontal = ("category",)
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "comment", "commenter")
    
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "user")
    
class CategoryAdmin(admin.ModelAdmin):
   list_display = ("id", "category")
   inlines = [
       CategoryInline
   ]
    
    
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listings, ListingsAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)
admin.site.register(Category, CategoryAdmin)
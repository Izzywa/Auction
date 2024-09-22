from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:listing_id>", views.view_listing, name="view_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("place_bid/<int:listing_id>", views.place_bid, name="place_bid"),
    path("close_bid/<int:listing_id>", views.close_bid, name="close_bid"),
    path("create_comment/<int:listing_id>", views.create_comment, name="create_comment"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categories, name="category")
]

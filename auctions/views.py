from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.forms import ModelForm, NumberInput, CheckboxSelectMultiple, URLInput, ValidationError, HiddenInput, Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import User, Listings, Category, Watchlist, Bid, Comment
from .helpers import get_max_bid, watchlisted_user, max_bidder

class ListingForm(ModelForm):
    class Meta:
        model = Listings
        fields = ["title", "description", "image", "starting_bid", "category"]
        labels = {
            "title": _("Item Name"),
            "image": _("Image URL"),
            "starting_bid": _("Starting Bid (USD)"),
        }
        widgets = {
            "starting_bid": NumberInput(attrs={"min": 0.1}),
            "category":CheckboxSelectMultiple(),
            "image": URLInput(attrs={"autocomplete": "off"})
        }
        
class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid", "item"]
        widgets = {
            "item": HiddenInput(),
        }
        labels = {
            "bid": _("Bid ($)"),
        }

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get("item")
        bid = cleaned_data.get("bid")
        
        max_bid = get_max_bid(item)
        
        if item.bid.count() == 0:
            if bid < max_bid:
                raise ValidationError(
                "Bid must be at least as large as the starting bid."
                )
        else:
            if bid <= max_bid:
                raise ValidationError(
                    "Bid must be bigger than previous bid."
                )
        
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment",  "item"]
        widgets = {
            "item": HiddenInput(),
            "comment": Textarea(attrs={"placeholder":"Insert your comment here."})
        }
        labels = {
            "comment": ""
        }

def index(request):
    listings = []
    for listing in Listings.objects.filter(active=True):
        listings.append({"listing": listing, "max_bid": get_max_bid(listing)})
        
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            user_id = request.user.id
            categories = request.POST.getlist("category")
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return render(request, "auctions/create_listing.html", {
                    "form": form
                }) 
            if len(categories) > 3:
                messages.warning(request, "Choose no more than 3 categories.", extra_tags="warning")
                return render(request, "auctions/create_listing.html", {
                    "form": form
                })               
            title = request.POST["title"]
            description = request.POST["description"]
            image = request.POST["image"]
            starting_bid = request.POST["starting_bid"]
            created_listing = Listings(title=title, description=description, image=image, starting_bid=starting_bid, seller=user)
            created_listing.save()
            if len(categories) is not 0:
                for category in categories:
                    try:
                        category_obj = Category.objects.get(pk=category)
                        created_listing.category.add(category_obj)
                    except Category.DoesNotExist:
                        return render(request, "auctions/create_listing.html", {
                            "form": form
                        })
            id = created_listing.pk
            messages.success(request, "Listing was created!", extra_tags="success")
            return HttpResponseRedirect(reverse("view_listing", args=(id,)))
            
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })
    return render(request, "auctions/create_listing.html", {
        "form": ListingForm()
    })


def view_listing(request, listing_id):
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        messages.warning(request, "Listing does not exist", extra_tags="danger")
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/view_listing.html", {
        "listing": listing,
        "watchlist": watchlisted_user(listing),
        "max_bidder": max_bidder(listing),
        "max_bid": get_max_bid(listing),
        "comments": listing.comments.all(),
        "bid_form": BidForm(initial={"item":listing}),
        "comment_form": CommentForm(initial={"item":listing})
    })
    
@login_required
def watchlist(request):
    if request.method == "POST":
        try:
            user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
             messages.error(request, "User does not exist.", extra_tags="danger")
            
        listing_id = request.POST["listing_id"]
        try:
            listing = Listings.objects.get(pk=listing_id)
        except Listings.DoesNotExist:
            messages.error(request, "Listing does not exist.", extra_tags="danger")
        
        try:
            remove_watchlist = Watchlist.objects.get(user=user, item=listing)
            remove_watchlist.delete()
            print("success")
        except Watchlist.DoesNotExist:
            add_watchlist = Watchlist(item=listing, user=user)
            add_watchlist.save()
        return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
    else:
        watchlist = request.user.watchlist.all()
        listings = []
        for list in watchlist:
            listings.append({"listing":list.item, "max_bid":get_max_bid(list.item)})
            
        return render(request, "auctions/watchlist.html", {
            "listings": listings
        })

@login_required
def place_bid(request, listing_id):
    if request.method == "POST":
        try:
            listing = Listings.objects.get(pk=listing_id)
        except Listings.DoesNotExist:
            messages.error(request, "Listing does not exist.", extra_tags="danger")
            return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
        
        initial_data = {
            "item": listing,
        }
        bid_form = BidForm(request.POST, initial=initial_data)
        if bid_form.is_valid():
            if 'item' in  bid_form.changed_data:
                messages.error(request, "Form not valid.", extra_tags="danger")
                return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
            
            new_bid = Bid(item=listing,bidder=request.user,bid=bid_form.cleaned_data["bid"])
            new_bid.save()
            messages.success(request, "Bid created", extra_tags="success")
            return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
        else:
            return render(request, "auctions/view_listing.html", {
                "listing": listing,
                "watchlist": watchlisted_user(listing),
                "max_bid": get_max_bid(listing),
                "max_bidder": max_bidder(listing),
                "comments": listing.comments.all(),
                "bid_form": bid_form,
                "comment_form": CommentForm(initial={"item":listing})
            })
            
    return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))

@login_required
def close_bid(request, listing_id):
    #If the user is signed in and is the one who created the listing, the user should have the ability to “close” the auction from this page, which makes the highest bidder the winner of the auction and makes the listing no longer active.
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        messages.error(request, "Listing does not exist.", extra_tags="danger")
        return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
    
    if listing.seller != request.user:
        messages.error(request, "Only original lister can close the listing.", extra_tags="danger")
        return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
    
    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))

@login_required
def create_comment(request, listing_id):
    if request.method == "POST":
        try:
            listing = Listings.objects.get(pk=listing_id)
        except Listings.DoesNotExist:
            messages.error(request, "Listing does not exist.", extra_tags="danger")
            return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
        
        initial_data = {
            "item": listing
        }
        comment_form = CommentForm(request.POST, initial=initial_data)
        if comment_form.is_valid():
            if "item" in comment_form.changed_data:
                messages.error(request, "Form not valid.", extra_tags="danger")
                return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
            
            new_comment = Comment(item=listing, commenter=request.user, comment=comment_form.cleaned_data["comment"])
            new_comment.save()
            messages.success(request, "Comment created", extra_tags="success")
            return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
        else: 
            return render(request, "auctions/view_listing.html", {
                "listing": listing,
                "watchlist": watchlisted_user(listing),
                "max_bidder": max_bidder(listing),
                "max_bid": get_max_bid(listing),
                "comments": listing.comments.all(),
                "bid_form": BidForm(initial={"item":listing}),
                "comment_form": comment_form
            })
    return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))

def categories(request, category=""):
    listings = []
    if category:
        try:
            category_obj = Category.objects.get(category=category,)
        except Category.DoesNotExist:
            category = ""
            messages.error(request, "Category does not exist", extra_tags="danger")
            return HttpResponseRedirect(reverse("categories"))
        
        list = Listings.objects.filter(category=category_obj, active=True)
        if len(list) == 0:
            listings = None
        else:
            for item in list:
                listings.append({"listing":item, "max_bid":get_max_bid(item)})
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
        "category": category,
        "listings": listings
    })
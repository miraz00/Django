from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms


from .models import *


def index(request):
    items = AuctionListings.objects.filter(active=True).order_by("-datetime")
    return render(request, "auctions/index.html", {
        "items": items,
        "page": "Active Listings"
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
            messages.success(request, "Log in successful!")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    messages.info(request, "You have been logged out!")
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
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    class CreateListing(forms.Form):
        title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={"autofocus": True}))
        description = forms.CharField(widget=forms.Textarea(), max_length=5000, required=False)
        starting_bid = forms.FloatField(min_value=0, label="Starting bid(in $)")
        url = forms.URLField(required=False, max_length=200)
        category = forms.CharField(required=False, max_length=64)

        def __init__(self, *args, **kwargs):
            super(CreateListing, self).__init__(*args, **kwargs)

            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['autocomplete'] = "off"

    if not request.user.is_authenticated:
        messages.error(request, "Login First.")
        return redirect("login")

    if request.method == "POST":
        form = CreateListing(request.POST)
        if not form.is_valid():
            return render(request, "auctions/create_listings.html", {
                "form": form,
            })
        else:
            item = AuctionListings(
                user_id=request.user.id,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                starting_bid=form.cleaned_data["starting_bid"],
                url=form.cleaned_data["url"],
                category=form.cleaned_data["category"]
            )
            item.save()
            messages.success(request, "Your item has been put into auction!")
            return redirect("index")

    create_listing_form = CreateListing()
    return render(request, "auctions/create_listings.html", {
        "form": create_listing_form,
    })


def view_listing(request, item_id):
    class ListingBid(forms.Form):
        your_bid = forms.FloatField(min_value=0, label="",
                                    widget=forms.NumberInput({"placeholder": "Make a bid"}))
        action = forms.CharField(widget=forms.HiddenInput({"value": "bid"}), label="")

    class CommentBid(forms.Form):
        comment = forms.CharField(widget=forms.Textarea({"placeholder": "Comment here",
                                                         "class": "form-control", "rows": "5"}),
                                  max_length=2048, label="")
        action = forms.CharField(widget=forms.HiddenInput({"value": "comment"}), label="")

    if request.method == "GET":
        item = AuctionListings.objects.get(id=item_id)
        return render(request, "auctions/view_listings.html", {
            "item": item,
            "bid_form": ListingBid(),
            "comment_form": CommentBid()
        })
    else:
        match request.POST["action"]:

            case "bid":
                form = ListingBid(request.POST)
                if form.is_valid():
                    bid = Bids(
                        item_id=item_id,
                        bidder=request.user,
                        amount=form.cleaned_data["your_bid"]
                    )
                    try:
                        bid.save()
                    except ValidationError as e:
                        messages.error(request, e.message)
                        return redirect("view listing", item_id)
                    messages.success(request, "Your bid has been placed successfully!")
                    return redirect("view listing", item_id)
                else:
                    item = AuctionListings.objects.get(id=item_id)
                    return render(request, "auctions/view_listings.html", {
                        "item": item,
                        "bid_form": form,
                        "comment_form": CommentBid()
                    })

            case "close_list":
                item = AuctionListings.objects.get(id=item_id)
                item.active = False
                item.save()
                messages.success(request, "Item closed successfully!")
                return redirect("view listing", item_id)

            case "add_watchlist":
                item = AuctionListings.objects.get(id=item_id)
                item.watchlisted_by.add(request.user)
                messages.success(request, "Item was added to the watchlist!")
                return redirect("view listing", item_id)

            case "remove_watchlist":
                item = AuctionListings.objects.get(id=item_id)
                item.watchlisted_by.remove(request.user)
                messages.success(request, "Item was removed from watchlist!")
                return redirect("view listing", item_id)

            case "comment":
                form = CommentBid(request.POST)
                if form.is_valid():
                    comment = Comments(
                        item_id=item_id,
                        user=request.user,
                        comment=form.cleaned_data["comment"]
                    )
                    try:
                        comment.save()
                    except ValidationError as e:
                        messages.error(request, e.message)
                        return redirect("view listing", item_id)
                    messages.info(request, "Your comment was added successfully!")
                    return redirect("view listing", item_id)
                else:
                    item = AuctionListings.objects.get(id=item_id)
                    return render(request, "auctions/view_listings.html", {
                        "item": item,
                        "bid_form": ListingBid(),
                        "comment_form": form
                    })


def view_category_listing(request, name):
    items = AuctionListings.objects.filter(active=True, category=name).order_by("-datetime")
    return render(request, "auctions/index.html", {
        "items": items,
        "page": f"Category: {name}"
    })


def view_watchlist(request):
    if request.method == "POST":
        item = AuctionListings.objects.get(pk=request.POST["id"])
        request.user.watchlists.remove(item)
        messages.success(request, "Item removed from watchlist.")
        return render(request, "auctions/index.html", {
            "items": request.user.watchlists.all().order_by("-datetime"),
            "page": "Watchlist"
        })
    if request.user.is_authenticated:
        items = request.user.watchlists.all().order_by("-datetime")
        return render(request, "auctions/index.html", {
            "items": items,
            "page": "Watchlist"
         })
    else:
        messages.error("Login First.")
        return redirect("login")


def view_categories(request):
    return render(request, "auctions/index.html", {
        "categories": AuctionListings.objects.values_list("category", flat=True).distinct(),
        "page": "Categories"
    })

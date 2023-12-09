import json

from django.contrib.auth.decorators import login_required

from .util import *

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.views.decorators.http import require_http_methods

from .models import *


class CreatePost(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control", "placeholder": "write your post here"}
    ), label="What's on your mind?", max_length=5120)


def index(request):
    post = CreatePost()
    if request.method == "POST":
        post = CreatePost(request.POST) if request.user.is_authenticated else False
        if post.is_valid():
            Post.objects.create(content=post.cleaned_data["content"], user=request.user)
            messages.success(request, "Your post has been uploaded successfully.")
            post = CreatePost()
    posts = Post.objects.all().order_by("-datetime")
    page = request.GET.get("page", 1)
    return render(request, "network/index.html", {
        "posts": paging(posts, page),
        "prev": paging_has_prev(posts, page),
        "next": paging_has_next(posts, page),
        "page": page,
        "create_post": post
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            messages.success(request, "You are now logged in.")
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "network/login.html")
    else:
        return render(request, "network/login.html")


def logout_view(request):
    messages.info(request, "You have been logged out.")
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
            return render(request, "network/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "network/register.html")
        messages.success(request, "Account created successfully.")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    profile_user = User.objects.get(username=username)
    if not profile_user:
        messages.error(request, "User doesn't exist!")
        return redirect("index")
    posts = Post.objects.filter(user=profile_user).order_by("-datetime")
    page = request.GET.get("page", 1)
    return render(request, "network/index.html", {
        "posts": paging(posts, page),
        "prev": paging_has_prev(posts, page),
        "next": paging_has_next(posts, page),
        "page": page,
        "profile": True,
        "profile_user": profile_user,
    })


@require_http_methods(["POST"])
def follow(request):
    user = User.objects.get(id=json.loads(request.body).get("id"))
    if user != request.user and request.user.is_authenticated:
        request.user.following.add(user)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


@ require_http_methods(["POST"])
def unfollow(request):
    user = User.objects.get(id=json.loads(request.body).get("id"))
    if user != request.user and request.user.is_authenticated:
        request.user.following.remove(user)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


def follow_feed(request):
    if request.user.is_authenticated:
        posts = Post.objects.filter(user__in=request.user.following.all()).order_by("-datetime")
        page = request.GET.get("page", 1)
        return render(request, "network/index.html", {
            "posts": paging(posts, page),
            "prev": paging_has_prev(posts, page),
            "next": paging_has_next(posts, page),
            "page": page,
            "following": True
        })
    else:
        messages.error(request, "Login first.")
        return redirect("login")


def get_page(request, feed, page_num, profile_username=False):
    posts_obj = ""
    if feed == "all":
        posts_obj = Post.objects.all().order_by("-datetime")
    elif feed == "following":
        posts_obj = Post.objects.filter(user__in=request.user.following.all()).order_by("-datetime")
    elif feed == "profile":
        profile_user = User.objects.get(username=profile_username)
        posts_obj = Post.objects.filter(user=profile_user).order_by("-datetime")
    posts = paging(posts_obj, page_num)

    if not posts:
        return JsonResponse({
            'html': '<div style="text-align: center;color: rgb(128,128,128)">-- Invalid page number --</div>',
        })

    post_template = '''
    <div class="mb-3 p-4" style="border-style: groove" data-post-id={post_id}>
        <h4 style="display: flex">
            <a href="/profile/{username}" style="text-decoration: none;color: inherit">{username}</a>
            {post_owner}
        </h4>
        <hr>
        <pre>{content}</pre>
        <hr>
        <div class="d-flex justify-content-between">
            <span><span class="like-button" {liked}</span><span class="like-count">{likes}</span></span>
            <span class="blockquote-footer">{datetime}</span>
        </div>
    </div>
    '''

    rendered_posts = [
        post_template.format(username=post.user.username, content=post.content, likes=post.liked_by.count(),
                             datetime=post.datetime.strftime('%b. %d, %Y, %I:%M %p'),
                             post_owner='''<span onclick="edit(this)" style="margin-left: auto">✏️</span>'''
                             if post.user == request.user else "",
                             liked="onclick='unlike(this)'>♥"
                             if request.user in post.liked_by.all() else "onclick='like(this)'>︎♡",
                             post_id=post.id)
        for post in posts]
    return JsonResponse({
        'html': ''.join(rendered_posts),
        'prev': paging_has_prev(posts_obj, page_num),
        'next': paging_has_next(posts_obj, page_num)
    })


@login_required
@ require_http_methods(["POST"])
def ajax_post(request):
    post = CreatePost({"content": json.loads(request.body).get("content")})
    if post.is_valid():
        Post.objects.create(content=post.cleaned_data["content"], user=request.user)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@ require_http_methods(["PUT"])
def update_post(request):
    post = Post.objects.get(pk=json.loads(request.body).get("postId"))
    content = json.loads(request.body).get("content")
    if request.user == post.user and content:
        post.content = content
        post.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@ require_http_methods(["PUT"])
def like_post(request):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=json.loads(request.body).get("postId"))
        post.liked_by.add(request.user)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


@ require_http_methods(["PUT"])
def unlike_post(request):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=json.loads(request.body).get("postId"))
        post.liked_by.remove(request.user)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


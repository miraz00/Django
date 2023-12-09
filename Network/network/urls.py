
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("following", views.follow_feed, name="follow feed"),
    path("get_page/<str:feed>/<int:page_num>", views.get_page, name="get page"),
    path("get_page/<str:feed>/<int:page_num>/<str:profile_username>", views.get_page, name="get page"),
    path("ajax_post", views.ajax_post, name="ajax post"),
    path("update_post", views.update_post, name="update post"),
    path("like_post", views.like_post, name="like post"),
    path("unlike_post", views.unlike_post, name="unlike post"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create listing"),
    path("category", views.view_categories, name="view categories"),
    path("category/<str:name>", views.view_category_listing, name="view category listing"),
    path("watchlist", views.view_watchlist, name="view watchlist"),
    path("view_listing/<int:item_id>", views.view_listing, name="view listing"),
]

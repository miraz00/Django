from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/search", views.search_results, name="search results"),
    path("wiki/create", views.create_page, name="create page"),
    path("wiki/random", views.random_page, name="random page"),
    path("wiki/<str:name>", views.show_page, name="show page"),
    path("wiki/<str:name>/edit", views.edit_page, name="edit page"),
]

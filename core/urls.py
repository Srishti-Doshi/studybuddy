# core/urls.py
from django.urls import path
from . import views

urlpatterns = [

    # Resource delete (faculty / superuser only)
    path(
        "resource/<int:id>/delete/",
        views.delete_resource,
        name="delete_resource"
    ),
    path(
        "tutorial/delete/<int:tutorial_id>/",
        views.delete_tutorial,
        name="delete_tutorial"
    ),

    path("about/", views.about, name="about"),

    path("add_bookmark/<int:resource_id>/", views.add_bookmark, name="add_bookmark"),
    path("remove_bookmark/<int:resource_id>/", views.remove_bookmark, name="remove_bookmark"),

    path("bookmarks/", views.my_bookmarks, name="my_bookmarks"),

    path("bookmark/toggle/", views.toggle_bookmark_ajax, name="toggle_bookmark_ajax"),

    path("api/bookmarks/status/", views.bookmark_status_api, name="bookmark_status_api"),


]

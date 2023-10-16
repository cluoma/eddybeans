from django.urls import path

from . import views

app_name = 'view'
urlpatterns = [
    # ex: /view/
    path("", views.index, name="index"),
    path("<int:post_id>/", views.detail, name='detail'),
    path("submit/", views.submit_post, name='submit'),
    path("submit/new", views.submit_new_post, name='submit_new'),
    path("comment/new", views.submit_new_comment, name='comment_new'),
    path("post/like", views.like_post, name='like_post'),
    path("post/edit/<int:post_id>", views.edit_post, name="edit_post"),
    path("post/delete/<int:post_id>", views.delete_post, name="delete_post"),
    path("calendar/", views.calendar, name="calendar"),
    path("logout", views.logout_view, name="logout")
]
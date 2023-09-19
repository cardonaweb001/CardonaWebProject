from django.urls import path

from . import views

app_name = 'cardonalab'
urlpatterns = [
    path('bookmarks/', views.bookmarks_view, name='bookmarks')
]
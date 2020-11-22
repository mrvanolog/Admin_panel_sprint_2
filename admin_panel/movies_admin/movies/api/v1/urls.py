from django.urls import path
from . import views

urlpatterns = [
    path("movies/", views.Movies.as_view()),
    path("movies/<uuid:pk>/", views.MoviesDetail.as_view())
]

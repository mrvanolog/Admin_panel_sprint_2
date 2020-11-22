from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies_admin.movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return # Сформированный QuerySet

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class Movies(MoviesApiMixin, BaseListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            "results": list(self.get_queryset()),
        }


class MoviesDetail(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return  # Словарь с данными объекта

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import FilmWork


class Movies(BaseListView):
    model = FilmWork
    http_method_names = ['get']  # Список методов, которые реализует обработчик

    def get_queryset(self):
        values = ("id", "title", "description", "creation_date", "rating", "type")
        query = FilmWork.objects.values(*values).annotate(
            actors=ArrayAgg(
                "personfilmwork__person__full_name",
                filter=Q(personfilmwork__role="actor"),
                distinct=True
            ),
            directors=ArrayAgg(
                "personfilmwork__person__full_name",
                filter=Q(personfilmwork__role="director"),
                distinct=True
            ),
            writers=ArrayAgg(
                "personfilmwork__person__full_name",
                filter=Q(personfilmwork__role="writer"),
                distinct=True
            ),
            genres=ArrayAgg(
                "genres__name",
                distinct=True
            ),
        )
        return query

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }

        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

class MoviesDetail(BaseDetailView):
    pass

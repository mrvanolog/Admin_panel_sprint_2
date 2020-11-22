from django.http import JsonResponse
from django.views import View

class MoviesListApi(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # Получение и обработка данных
        return JsonResponse({})
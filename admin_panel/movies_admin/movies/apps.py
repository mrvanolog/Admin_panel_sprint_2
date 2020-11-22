from django.apps import AppConfig


class MoviesConfig(AppConfig):
    name = 'movies'


class AppsConfig():

    def ready(self):
        from . import signals

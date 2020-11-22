import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from model_utils.models import TimeStampedModel

CONTENT_SCHEMA = "content"


class Person(TimeStampedModel):
    id = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.TextField(_("полное имя"))
    birth_date = models.DateField(_("дата рождения"), null=True)

    class Meta:
        verbose_name = _("персона")
        verbose_name_plural = _("персоны")
        db_table = f'{CONTENT_SCHEMA}"."person'

    def __str__(self):
        return self.full_name


class Genre(TimeStampedModel):
    id = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_("название"))
    description = models.TextField(_("описание"), blank=True)

    class Meta:
        verbose_name = _("жанр")
        verbose_name_plural = _("жанры")
        db_table = f'{CONTENT_SCHEMA}"."genre'

    def __str__(self):
        return self.name


class FilmWorkType(models.TextChoices):
    MOVIE = "film", _("фильм")
    SERIES = "series", _("сериал")


class FilmWork(TimeStampedModel):
    id = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    creation_date = models.DateField(_("дата создания фильма"), null=True, blank=True)
    certificate = models.TextField(_("сертификат"), blank=True)
    file_path = models.FileField(_("файл"), upload_to="film_works/", null=True, blank=True)
    rating = models.FloatField(
        _("рейтинг"), validators=[MinValueValidator(0)], null=True, blank=True
    )
    type = models.TextField(_("тип"), choices=FilmWorkType.choices, blank=True)
    genres = models.ManyToManyField("movies.Genre", through="movies.GenreFilmWork")
    persons = models.ManyToManyField("movies.Person", through="movies.PersonFilmWork")

    class Meta:
        verbose_name = _("кинопроизведение")
        verbose_name_plural = _("кинопроизведения")
        db_table = f'{CONTENT_SCHEMA}"."film_work'

    def __str__(self):
        return self.title


class RoleType(models.TextChoices):
    ACTOR = "actor", _("актер")
    WRITER = "writer", _("сценарист")
    DIRECTOR = "director", _("режиссер")


class PersonFilmWork(models.Model):
    id = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey("movies.FilmWork", on_delete=models.CASCADE)
    person = models.ForeignKey("movies.Person", on_delete=models.CASCADE)
    role = models.TextField(_("роль"), choices=RoleType.choices)
    created = models.DateTimeField(_("дата создания"), auto_created=True, auto_now_add=True)

    class Meta:
        verbose_name = _("участник кинопроизведение")
        verbose_name_plural = _("участники кинопроизведения")
        db_table = f'{CONTENT_SCHEMA}"."person_film_work'
        unique_together = ("film_work", "person", "role")


class GenreFilmWork(models.Model):
    id = models.UUIDField(_("id"), primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey("movies.FilmWork", on_delete=models.CASCADE)
    genre = models.ForeignKey("movies.Genre", on_delete=models.CASCADE)
    created = models.DateTimeField(_("дата создания"), auto_created=True, auto_now_add=True)

    class Meta:
        verbose_name = _("жанр кинопроизведение")
        verbose_name_plural = _("жанры кинопроизведения")
        db_table = f'{CONTENT_SCHEMA}"."genre_film_work'
        unique_together = ("film_work", "genre")

from django.contrib import admin
from .models import FilmWork, Person, Genre


class PersonInLineAdmin(admin.TabularInline):
    model = FilmWork.persons.through
    extra = 0


class GenreInLineAdmin(admin.TabularInline):
    model = FilmWork.genres.through
    extra = 0


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ("title", "type", "creation_date", "rating")
    # порядок следования полей в форме создания/редактирования
    fields = (
        "title",
        "type",
        "description",
        "creation_date",
        "rating",
        "certificate",
        "file_path"
    )

    inlines = (PersonInLineAdmin, GenreInLineAdmin)

    # поиск по полям
    search_fields = ("title", "description", "type", "genres")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ("full_name", "birth_date")
    # порядок следования полей в форме создания/редактирования
    fields = (
        "full_name",
        "birth_date"
    )

    inlines = (PersonInLineAdmin, )

    # поиск по полям
    search_fields = ("full_name", "birth_date")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ("name", "description")
    # порядок следования полей в форме создания/редактирования
    fields = (
        "name",
        "description"
    )

    inlines = (GenreInLineAdmin, )

    # поиск по полям
    search_fields = ("name", "description")

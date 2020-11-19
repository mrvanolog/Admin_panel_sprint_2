import sqlite3
import json
from typing import List


class SQLiteLoader():
    """Загружает данные из SQLite, преобразовывает их и возвращает список словарей для
    последующей обработки в PostgresSaver.

    Parameters
    ----------
    connection : sqlite3.Connection
        Объект соединения с SQLite
    """

    SQL = """
    /* Используем CTE для читаемости. Здесь нет прироста
    производительности, поэтому можно поменять на subquery */
    WITH x as (
        -- Используем group_concat, чтобы собрать id и имена
        -- всех актёров в один список после join'а с таблицей actors
        -- Отметим, что порядок id и имён совпадает
        -- Не стоит забывать про many-to-many связь между
        -- таблицами фильмов и актёров
        SELECT m.id, group_concat(a.id) as actors_ids, group_concat(a.name) as actors_names
        FROM movies m
                 LEFT JOIN movie_actors ma on m.id = ma.movie_id
                 LEFT JOIN actors a on ma.actor_id = a.id
        GROUP BY m.id
    )
    -- Получаем список всех фильмов со сценаристами и актёрами
    SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
         /* Этот CASE решает проблему в дизайне таблицы:
        если сценарист всего один, то он записан простой строкой
        в столбце writer и id. В противном случае данные
        хранятся в столбце writers  и записаны в виде
        списка объектов JSON.
        Для исправления ситуации применяем хак:
        приводим одиночные записи сценаристов к списку
        из одного объекта JSON и кладём всё в поле writers */
           CASE
            WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
            ELSE m.writers
           END AS writers
    FROM movies m
    LEFT JOIN x ON m.id = x.id
    """

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = self.dict_factory

    @staticmethod
    def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
        """Так как в SQLite нет встроенной фабрики для строк в виде dict, делаем свою.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def load_writers_names(self) -> dict:
        """Получаем список всех сценаристов, так как нет возможности
        получить их в одном запросе.

        Returns
        -------
        dict
            Словарь всех сценаристов вида
            {
                "Writer": {"writer_id": "id", "writer_name": "name"},
                ...
            }
        """
        writers = {}
        # Используем DISTINCT, чтобы отсекать возможные дубли
        for writer in self.conn.execute("SELECT DISTINCT id, name FROM writers"):
            writers[writer["id"]] = writer
        return writers

    def _transform_row(self, row: dict, writers: dict) -> dict:
        """Основная логика преобразования данных из SQLite во внутреннее
        представление, которое дальше будет уходить в PostgreSQL.
        Решаемы проблемы:
        1) genre в БД указан в виде строки из одного или нескольких
        жанров, разделённых запятыми -> преобразовываем в список жанров.
        2) writers из запроса в БД приходит в виде списка словарей id'шников
        -> обогащаем именами из полученных заранее сценаристов
        и добавляем к каждому id ещё и имя
        3) actors формируем из двух полей запроса (actors_ids и actors_names)
        в список словарей, наподобие списка сценаристов.
        4) для полей imdb_rating, director и description меняем
        поля "N/A" на None.

        Parameters
        ----------
        row : dict
            Строка из БД
        writers : dict
            Текущие сценаристы

        Returns
        -------
        dict
            Подходящая строка для обработки
        """
        movie_writers = []
        writers_set = set()
        for writer in json.loads(row['writers']):
            writer_id = writer['id']
            if writers[writer_id]['name'] != 'N/A' and writer_id not in writers_set:
                movie_writers.append(writers[writer_id])
                writers_set.add(writer_id)

        actors_names = []
        if row['actors_ids'] is not None and row['actors_names'] is not None:
            actors_names = [x for x in row['actors_names'].split(',') if x != 'N/A']

        new_row = {
            "id": row['id'],
            "genre": row['genre'].replace(' ', '').split(','),
            "actors": actors_names,
            "writers": [x['name'] for x in movie_writers],
            "imdb_rating": float(row['imdb_rating']) if row['imdb_rating'] != 'N/A' else None,
            "title": row['title'],
            "director": [
                x.strip() for x in row['director'].split(',')
            ] if row['director'] != 'N/A' else None,
            "description": row['plot'] if row['plot'] != 'N/A' else None
        }

        return new_row

    def load_movies(self) -> List[dict]:
        """Основной метод для выгрузки данных из MySQL.

        Returns
        -------
        List[dict]
            Итоговые данные из БД
        """
        movies = []

        writers = self.load_writers_names()

        for row in self.conn.execute(self.SQL):
            transformed_row = self._transform_row(row, writers)
            movies.append(transformed_row)

        return movies

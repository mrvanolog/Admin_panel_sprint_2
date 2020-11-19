from psycopg2.extensions import connection as _connection
from uuid import uuid4
from datetime import datetime

from typing import List, Dict, Set
from typing import Any


class PostgresSaver():
    def __init__(self, connection: _connection):
        self.conn = connection

        # сеты, чтобы избежать дублирования данных
        self.person_set: Set[str] = set()
        self.genres_set: Set[str] = set()

        # списки, в которых хранятся таблицы для PostgreSQL
        self.film_work: List[dict] = []
        self.genre: List[dict] = []
        self.genre_film_work: List[dict] = []
        self.person: List[dict] = []
        self.person_film_work: List[dict] = []

        # название схемы в PostgreSQL
        self.schema = "content"

    def append_film_work(self, row: Dict[str, Any]) -> str:
        """Добавляет одну строку в локальную таблицу film_work и возвращает uuid фильма.
        """
        film_id = str(uuid4())
        new_row = {
            "id": film_id,
            "title": row["title"],
            "description": "" if row["description"] is None else row["description"],
            "creation_date": None,
            "certificate": "",
            "file_path": None,
            "rating": row["imdb_rating"],
            "type": "movie",
            "created": datetime.now().astimezone(),
            "modified": datetime.now().astimezone()
        }
        self.film_work.append(new_row)

        return film_id

    def _add_person(self, id_: str, name: str):
        """Добавляет один ряд в локальную таблицу person.
        """
        row = {
            "id": id_,
            "full_name": name,
            "birth_date": None,
            "created": datetime.now().astimezone(),
            "modified": datetime.now().astimezone()
        }
        self.person.append(row)

    def append_person(self, person_list: List[str]) -> List[str]:
        """Добавляет несколько строк в локальную таблицу person и возвращает uuid всех добавленных
        людей. Не добавляет строку, если человек уже есть в таблице.
        """
        if person_list is None:
            return []

        id_list = []
        for person in person_list:
            if person not in self.person_set:
                id_ = str(uuid4())
                self._add_person(id_, person)
                self.person_set.add(person)
            else:
                for p in self.person:
                    if p["full_name"] == person:
                        id_ = p["id"]
                        break

            id_list.append(id_)

        return id_list

    def _add_genre(self, id_: str, name: str):
        """Добавляет один ряд в локальную таблицу genre.
        """
        row = {
            "id": id_,
            "name": name,
            "description": "",
            "created": datetime.now().astimezone(),
            "modified": datetime.now().astimezone()
        }
        self.genre.append(row)

    def append_genre(self, genre_list: List[str]) -> List[str]:
        """Добавляет несколько строк в локальную таблицу genre и возвращает uuid всех добавленных
        жанров. Не добавляет строку, если жанр уже есть в таблице.
        """
        if genre_list is None:
            return []

        id_list = []
        for genre in genre_list:
            if genre not in self.genres_set:
                id_ = str(uuid4())
                self._add_genre(id_, genre)
                self.genres_set.add(genre)
            else:
                for g in self.genre:
                    if g["name"] == genre:
                        id_ = g["id"]
                        break

            id_list.append(id_)

        return id_list

    def append_person_film_work(self, film_id: str, person_id_list: List[str], role: str):
        """Добавляет несколько строк в локальную таблицу person_film_work.
        """
        for person_id in person_id_list:
            id_ = str(uuid4())
            row = {
                "id": id_,
                "film_work_id": film_id,
                "person_id": person_id,
                "role": role,
                "created": datetime.now().astimezone()
            }
            self.person_film_work.append(row)

    def append_genre_film_work(self, film_id: str, genre_id_list: List[str]):
        """Добавляет несколько строк в локальную таблицу genre_film_work.
        """
        for genre_id in genre_id_list:
            id_ = str(uuid4())
            row = {
                "id": id_,
                "film_work_id": film_id,
                "genre_id": genre_id,
                "created": datetime.now().astimezone()
            }
            self.genre_film_work.append(row)

    def insert_film_work(self):
        """Вставляет данные из локальной таблицы film_work в PostgreSQL.
        """
        with self.conn.cursor() as cursor:
            for row in self.film_work:
                line = tuple(val for val in row.values())
                cursor.execute("""INSERT INTO content.film_work (
                    id,
                    title,
                    description,
                    creation_date,
                    certificate,
                    file_path,
                    rating,
                    type,
                    created,
                    modified
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, line)

    def insert_genre(self):
        """Вставляет данные из локальной таблицы genre в PostgreSQL.
        """
        with self.conn.cursor() as cursor:
            for row in self.genre:
                line = tuple(val for val in row.values())
                cursor.execute("""
                INSERT INTO content.genre (
                    id,
                    name,
                    description,
                    created,
                    modified
                ) VALUES (%s, %s, %s, %s, %s)
                """, line)

    def insert_person(self):
        """Вставляет данные из локальной таблицы person в PostgreSQL.
        """
        with self.conn.cursor() as cursor:
            for row in self.person:
                line = tuple(val for val in row.values())
                cursor.execute("""
                INSERT INTO content.person (
                    id,
                    full_name,
                    birth_date,
                    created,
                    modified
                ) VALUES (%s, %s, %s, %s, %s)
                """, line)

    def insert_genre_film_work(self):
        """Вставляет данные из локальной таблицы genre_film_work в PostgreSQL.
        """
        with self.conn.cursor() as cursor:
            for row in self.genre_film_work:
                line = tuple(val for val in row.values())
                cursor.execute("""
                INSERT INTO content.genre_film_work (
                    id,
                    film_work_id,
                    genre_id,
                    created
                ) VALUES (%s, %s, %s, %s)
                """, line)

    def insert_person_film_work(self):
        """Вставляет данные из локальной таблицы person_film_work в PostgreSQL.
        """
        with self.conn.cursor() as cursor:
            for row in self.person_film_work:
                line = tuple(val for val in row.values())
                cursor.execute("""
                INSERT INTO content.person_film_work (
                    id,
                    film_work_id,
                    person_id,
                    role,
                    created
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (film_work_id, person_id, role) DO NOTHING
                """, line)

    def save_all_data(self, data: List[dict]):
        """Основной метод, который обрабатывает данные из MySQL и загружает их в PostgreSQL.
        """
        for row in data:
            film_id = self.append_film_work(row)

            actor_id_list = self.append_person(row["actors"])
            self.append_person_film_work(film_id, actor_id_list, "actor")

            writer_id_list = self.append_person(row["writers"])
            self.append_person_film_work(film_id, writer_id_list, "writer")

            director_id_list = self.append_person(row["director"])
            self.append_person_film_work(film_id, director_id_list, "director")

            genre_id_list = self.append_genre(row["genre"])
            self.append_genre_film_work(film_id, genre_id_list)

        self.insert_film_work()
        self.insert_genre()
        self.insert_person()
        self.insert_person_film_work()
        self.insert_genre_film_work()

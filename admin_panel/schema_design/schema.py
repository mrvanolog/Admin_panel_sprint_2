import psycopg2
import yaml
from pathlib import Path

if __name__ == "__main__":
    parent_dir = Path(__file__).parent
    path_dsn = parent_dir.joinpath("dsn.yaml")

    with path_dsn.open("r") as f:
        data = f.read()
        dsn = yaml.safe_load(data)

    sql_schema = """
    -- Создаем отдельную схему для нашего контента, чтобы не перемешалось с сущностями Django
    CREATE SCHEMA IF NOT EXISTS content;

    -- Жанры, которые могут быть у кинопроизведений
    CREATE TABLE IF NOT EXISTS content.genre (
        id uuid PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created timestamp with time zone,
        modified timestamp with time zone
    );

    -- Убраны актеры, жанры, режиссеры и сценаристы,
    -- так как они находятся в отношении m2m с этой таблицей
    CREATE TABLE IF NOT EXISTS content.film_work (
        id uuid PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        creation_date DATE,
        certificate TEXT,
        file_path TEXT,
        rating FLOAT,
        type TEXT not null,
        created timestamp with time zone,
        modified timestamp with time zone
    );

    -- Обобщение для актера, режиссера и сценариста
    CREATE TABLE IF NOT EXISTS content.person (
        id uuid PRIMARY KEY,
        full_name TEXT NOT NULL,
        birth_date DATE,
        created timestamp with time zone,
        modified timestamp with time zone
    );

    -- m2m таблица для связывания кинопроизведений с жанрами
    CREATE TABLE IF NOT EXISTS content.genre_film_work (
        id uuid PRIMARY KEY,
        film_work_id uuid NOT NULL,
        genre_id uuid NOT NULL,
        created timestamp with time zone
    );

    -- Обязательно проверяется уникальность жанра и кинопроизведения, чтобы не появлялось дублей
    CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

    -- m2m таблица для связывания кинопроизведений с участниками
    CREATE TABLE IF NOT EXISTS content.person_film_work (
        id uuid PRIMARY KEY,
        film_work_id uuid NOT NULL,
        person_id uuid NOT NULL,
        role TEXT NOT NULL,
        created timestamp with time zone
    );

    -- Обязательно проверяется уникальность кинопроизведения,
    -- человека и роли человека, чтобы не появлялось дублей
    -- Один человек может быть сразу в нескольких ролях (например, сценарист и режиссер)
    CREATE UNIQUE INDEX film_work_person_role
    ON content.person_film_work (film_work_id, person_id, role);
    """

    with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
        cursor.execute(sql_schema)

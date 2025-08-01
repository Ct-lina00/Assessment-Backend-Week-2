"""Functions that interact with the database."""

from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection


def get_db_connection(dbname,
                      password="postgres") -> connection:
    """Returns a DB connection."""

    return connect(dbname=dbname,
                   host="localhost",
                   port=5432,
                   password=password,
                   cursor_factory=RealDictCursor)


def get_subjects(conn: connection) -> list[dict]:
    """This function returns all subjects in the marine_experiments database."""
    with conn.cursor() as cursor:
        query = """
        SELECT
        s.date_of_birth, sp.species_name, s.subject_id, s.subject_name FROM subject s
        JOIN species sp
        ON sp.species_id = s.species_id
        ORDER BY s.date_of_birth DESC;"""
        cursor.execute(query)

        rows = cursor.fetchall()
    return rows


def get_experiments(conn: connection, type: str = None, score_over: int = None) -> list[dict]:
    """This function returns all subjects in the marine_experiments database."""
    with conn.cursor() as cursor:
        query = sql.SQL("""
            SELECT
            e.experiment_id, e.subject_id,
            e.experiment_date, sp.species_name as species, et.type_name as experiment_type,
            CONCAT(ROUND(e.score * (100/ et.max_score), 2), '%') AS Score
            FROM experiment e
            JOIN subject s
            USING (subject_id)
            JOIN species sp
            USING (species_id)
            JOIN experiment_type et
            ON et.experiment_type_id = e.experiment_type_id
            ORDER BY e.experiment_date DESC;""")

        cursor.execute(query)
        rows = cursor.fetchall()

    return rows


def delete_experiment(conn: connection, experiment_id: str):
    with conn.cursor() as cursor:
        query = """
        SELECT experiment_id, experiment_date
        FROM experiment
        WHERE experiment_id = %(experiment_id)s;"""
        cursor.execute(query, {"experiment_id": experiment_id})
        rows = cursor.fetchone()
        if rows:
            query2 = """
                    DELETE FROM experiment
                    WHERE experiment_id = %(experiment_id)s; """
            cursor.execute(query2, {"experiment_id": experiment_id})
            conn.commit()
            return rows, 200
        if not rows:
            return {"error": f"Unable to locate experiment with ID {experiment_id}."}, 404

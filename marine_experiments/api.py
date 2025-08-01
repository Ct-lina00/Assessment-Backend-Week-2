"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql

from database_functions import get_db_connection, get_subjects, get_experiments


app = Flask(__name__)

"""
For testing reasons; please ALWAYS use this connection.

- Do not make another connection in your code
- Do not close this connection

If you do not understand this instructions; as a coach to explain
"""
conn = get_db_connection("marine_experiments")


def validate_type(type):
    """Return if type valid for the request."""
    return type in {"intelligence", "obedience", "aggression"}


def validate_score_over(score_over):
    """Return if score is valid for the request."""
    return score_over in range[100]


@app.get("/")
def home():
    """Returns an informational message."""
    return jsonify({
        "designation": "Project Armada",
        "resource": "JSON-based API",
        "status": "Classified"
    })


@app.route("/subject", methods=["GET"])
def get_subject_endpoint():
    """Function executes the GET request returning list of subject objects. """
    subjects = get_subjects(conn)
    for s in subjects:
        s["date_of_birth"] = datetime.strftime(s["date_of_birth"], "%Y-%m-%d")
    if subjects == []:
        return subjects
    if not subjects:
        return {"error": "No subjects found"}, 404
    return subjects, 200


@app.route("/experiment", methods=["GET"])
def get_experiment_endpoint():
    """Function executes the GET request returning list of experiment objects. """
    if request.method == "GET":
        type = None
        score_over = None
        if "type" in request.args:
            type = request.args.get("type")
            if type is not None and not validate_type(type):
                return {"error": "Invalid value for type parameter"}, 400

        if "score_over" in request.args:
            score_over = request.args.get("score_over")
            try:
                score_over = int(score_over)
                if score_over is not None and not validate_score_over(score_over):
                    return {"error": "Invalid value for score_over parameter"}, 400
            except TypeError:
                return {"error": "Invalid type value for score_over parameter"}, 400

        experiments = get_experiments(conn, type, score_over)
        for s in experiments:
            s["experiment_date"] = datetime.strftime(
                s["experiment_date"], "%Y-%m-%d")

        if experiments == []:
            return experiments

        if not experiments:
            return {"error": "No experiments found"}, 404

        return experiments, 200


@app.route("/experiment/<id>", methods=["DELETE"])
def delete_experiment_endpoint():
    """Function executes the delete request. """

    success = delete_experiment(conn, experiment_id)

    if not success:
        return {"error": "Movie could not be deleted"}, 404

    return {"message": "Movie deleted"}


if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()

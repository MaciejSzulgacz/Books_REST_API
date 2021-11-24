import json
import sqlite3
from logging import getLogger

from flask import Flask, Response, abort, jsonify, request

from .data_functions import (
    get_book_by_author,
    get_book_by_published_date,
    get_list_of_books,
    sort_books_by_published_date,
)
from .db_functions import create_db_and_table, parse_db_body, sync_db_with_google

app = Flask(__name__)
logger = getLogger("FirstFlask")

BASE_URL = "https://www.googleapis.com/books/v1/volumes?{0}={1}"


@app.route("/", methods=["GET"])
def get_welcome_view() -> str:
    if request.method == "GET":
        return "<h1>Welcome on my BOOKS_REST_API application.<h1> <h2>Maciej Szulgacz<h2>"


@app.route("/db", methods=["POST"])
def post_db_sync():
    response = None
    if request.method == "POST":
        create_db_and_table()
        key, value = parse_db_body(request.data)
        google_resp = sync_db_with_google(key, value)
        response = app.response_class(
            response=json.dumps(f"{google_resp.get('items')[0].get('id')}"),
            status=200,
            mimetype="application/json",
        )
    else:
        abort(400)
    return response or abort(500)


@app.route("/books", methods=["GET"])
def get_books() -> Response or str:
    if request.method == "GET":
        try:
            con = sqlite3.connect("books_db.db")
            cur = con.cursor()
            published_date = request.args.get("published_date")
            date_to_sort = request.args.get("sort")
            authors_dict = request.args.to_dict(flat=False)
            if published_date:
                return get_book_by_published_date(cur, published_date)
            elif date_to_sort:
                return sort_books_by_published_date(cur, date_to_sort)
            elif authors_dict:
                try:
                    return get_book_by_author(cur, authors_dict)
                except KeyError:
                    abort(404)
            else:
                return get_list_of_books(cur)
        except sqlite3.OperationalError:
            return "<h1>Database is empty, send data to the database.<h1>"


@app.route("/books/<string:book_id>", methods=["GET"])
def get_book_by_id(book_id: str) -> Response or str:
    if request.method == "GET":
        try:
            con = sqlite3.connect("books_db.db")
            cur = con.cursor()
            cur.execute(
                """
                SELECT title, authors, published_date, categories, average_rating, ratings_count, thumbnail
                FROM my_books WHERE id = "{}";
            """.format(book_id))
            row_headers = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            return jsonify(json_data)
        except sqlite3.OperationalError:
            return "<h1>Database is empty, send data to the database.<h1>"

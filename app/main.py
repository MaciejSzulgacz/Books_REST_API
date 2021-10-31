import json
import sqlite3

from flask import Flask, request, abort, jsonify, Response
from logging import getLogger
from .data_functions import list_of_books, search_book_by_author, search_book_by_published_date,\
    sort_books_by_published_date
from .db_functions import parse_db_body, sync_db_with_google

app = Flask(__name__)
logger = getLogger("FirstFlask")

BASE_URL = "https://www.googleapis.com/books/v1/volumes?{0}={1}"


@app.route("/", methods=['GET'])
def create_db_and_table():
    if request.method == 'GET':
        con = sqlite3.connect('books_db.db')
        cur = con.cursor()
        create_books_table = """CREATE TABLE my_books(
            id text primary key,
            title text,
            authors text,
            published_date varchar(10),
            categories text,
            average_rating int,
            ratings_count int,
            thumbnail text);
        """
        cur.execute(create_books_table)
        con.commit()
        return None


@app.route("/db", methods=["POST"])
def init_db_sync():
    response = None
    if request.method == "POST":
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


@app.route("/books", methods=['GET'])
def get_books():
    if request.method == 'GET':
        con = sqlite3.connect('books_db.db')
        cur = con.cursor()
        published_date = request.args.get('published_date')
        date_to_sort = request.args.get('sort')
        authors_dict = request.args.to_dict(flat=False)
        if published_date:
            return search_book_by_published_date(cur, published_date)
        elif date_to_sort:
            return sort_books_by_published_date(cur, date_to_sort)
        elif authors_dict:
            try:
                return search_book_by_author(cur, authors_dict)
            except KeyError:
                pass
        else:
            return list_of_books(cur)


@app.route("/books/<string:book_id>", methods=['GET'])
def search_book_by_id(book_id: str) -> Response:
    if request.method == 'GET':
        con = sqlite3.connect('books_db.db')
        cur = con.cursor()
        cur.execute(f"SELECT title, authors, published_date, categories, average_rating, ratings_count, thumbnail "
                    f"FROM my_books WHERE id = '{book_id}'")
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return jsonify(json_data)

from flask import abort, jsonify, request, Response
from sqlite3 import Cursor


def get_list_of_books(cur: Cursor) -> Response:
    if request.method == 'GET':
        cur.execute("SELECT title, authors, published_date, categories, average_rating, ratings_count, thumbnail "
                    "FROM my_books")
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return jsonify(json_data)


def get_book_by_author(cur: Cursor, authors_dict: dict) -> Response:
    authors_string = ' '.join(map(str, authors_dict['author']))
    cur.execute(f"SELECT title, authors, published_date, categories, average_rating, ratings_count, thumbnail "
                f"FROM my_books WHERE authors LIKE '%{authors_string}%'")
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)


def get_book_by_published_date(cur: Cursor, published_date: str) -> Response:
    cur.execute(f"SELECT title, authors, published_date, categories, average_rating, ratings_count, thumbnail "
                f"FROM my_books WHERE published_date LIKE '%{published_date}%'")
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)


def sort_books_by_published_date(cur: Cursor, date_to_sort: str) -> Response:
    if date_to_sort:
        if date_to_sort[0] == "-":
            desc_or_asc = "DESC"
        else:
            desc_or_asc = "ASC"
    else:
        abort(404)
    cur.execute(f"SELECT title, authors, published_date, categories, average_rating, ratings_count, thumbnail "
                f"FROM my_books ORDER BY published_date {desc_or_asc}")
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)

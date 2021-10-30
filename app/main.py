import json
from sqlite3 import OperationalError


from flask import Flask, request, jsonify
import requests
from logging import getLogger

import sqlite3

app = Flask(__name__)
logger = getLogger("FirstFlask")

BASE_URL = "https://www.googleapis.com/books/v1/volumes?{0}={1}"


def create_db():
    url = BASE_URL.format("q", "Hobbit")
    google_response: requests.Response = requests.get(url)
    google_data: dict = json.loads(google_response.content.decode().strip())
    con = sqlite3.connect('test_2.db')
    cur = con.cursor()
    create_books_table = """CREATE TABLE my_books(
        id text primary key,
        title text,
        authors text,
        published_date varchar(10),
        categories text,
        average_rating int,
        rating_count int,
        thumbnail text);
    """
    try:
        cur.execute(create_books_table)
        con.commit()
        for book in google_data['items']:
            id_number = book['id']
            title = book['volumeInfo']['title']
            authors = ' '.join(map(str, book['volumeInfo']['authors']))
            published_date = book['volumeInfo']['publishedDate']
            if 'categories' in book['volumeInfo']:
                categories = ' '.join(map(str, book['volumeInfo']['categories']))
            else:
                categories = ""
            if 'averageRating' in book['volumeInfo']:
                average_rating = book['volumeInfo']['averageRating']
            else:
                average_rating = ""
            if 'ratingCount' in book['volumeInfo']:
                rating_count = book['volumeInfo']['ratingsCount']
            else:
                rating_count = ""
            if 'imageLinks' in book['volumeInfo']:
                thumbnail = book['volumeInfo']['imageLinks']['thumbnail']
            else:
                thumbnail = ""
            cur.execute("INSERT INTO my_books (id, title, authors, published_date, categories, average_rating, "
                        "rating_count, thumbnail) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id_number, title, authors,
                                                                                     published_date, categories,
                                                                                     average_rating,
                                                                                     rating_count, thumbnail))
            con.commit()
    except OperationalError:
        print("Table my_books already exists ")


def list_of_books(cur):
    if request.method == 'GET':
        cur.execute("SELECT * FROM my_books")
        row_headers = [x[0] for x in cur.description]  # this will extract row headers
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return jsonify(json_data)


def author_of_book(cur, authors_dict):
    authors_string = ' '.join(map(str, authors_dict['author']))
    cur.execute(f"SELECT * FROM my_books WHERE authors LIKE '%{authors_string}%'")
    row_headers = [x[0] for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)


def published_date_of_book(cur, published_date):
    if request.method == 'GET':
        cur.execute(f"SELECT * FROM my_books WHERE published_date LIKE '%{published_date}%'")
        row_headers = [x[0] for x in cur.description]  # this will extract row headers
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return jsonify(json_data)


def published_date_to_sort(cur, date_to_sort):
    if date_to_sort[0] == "-":
        desc_or_asc = "DESC"
    else:
        desc_or_asc = "ASC"
    cur.execute(f"SELECT * FROM my_books ORDER BY published_date {desc_or_asc}")
    row_headers = [x[0] for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)


@app.route("/books/<string:book_id>", methods=['GET'])
def id_of_book(book_id):
    if request.method == 'GET':
        con = sqlite3.connect('test_2.db')
        cur = con.cursor()
        create_db()
        print(book_id)
        cur.execute(f"SELECT * FROM my_books WHERE id = '{book_id}'")
        row_headers = [x[0] for x in cur.description]  # this will extract row headers
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return jsonify(json_data)


@app.route("/books", methods=['GET'])
def main_function():
    if request.method == 'GET':
        con = sqlite3.connect('test_2.db')
        cur = con.cursor()
        create_db()
        published_date = request.args.get('published_date')
        date_to_sort = request.args.get('sort')
        authors_dict = request.args.to_dict(flat=False)
        if published_date:
            return published_date_of_book(cur, published_date)
        elif date_to_sort:
            return published_date_to_sort(cur, date_to_sort)
        elif authors_dict:
            try:
                return author_of_book(cur, authors_dict)
            except KeyError:
                pass
        else:
            return list_of_books(cur)

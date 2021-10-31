import json
import requests
import sqlite3
from typing import Tuple, Dict, Any

BASE_URL = "https://www.googleapis.com/books/v1/volumes?{0}={1}"


def parse_db_body(input_data: bytes) -> Tuple[str, str]:
    data = json.loads(input_data.decode().strip())
    key = "q"
    value = data["q"]
    return key, value


def sync_db_with_google(key: str, value: str) -> Dict[str, Any]:
    url = BASE_URL.format(key, value)
    google_response: requests.Response = requests.get(url)
    google_data = json.loads(google_response.content.decode().strip())
    update_db(google_data)
    return google_data


def update_db(google_data: dict):
    con = sqlite3.connect('books_db.db')
    cur = con.cursor()
    list_of_inserts = []
    for book in google_data['items']:
        id_number = book['id']
        title = book['volumeInfo']['title']
        authors_dict = book['volumeInfo'].get('authors', None)
        if authors_dict:
            authors = ' '.join(map(str, authors_dict))
        else:
            authors = None
        published_date = book['volumeInfo']['publishedDate']
        categories_list = book['volumeInfo'].get('categories', None)
        if categories_list:
            categories = ' '.join(map(str, categories_list))
        else:
            categories = None
        average_rating = book['volumeInfo'].get("averageRating", None)
        ratings_count = book['volumeInfo'].get("ratingsCount", None)
        thumbnail_dict = book['volumeInfo'].get('imageLinks', None)
        if thumbnail_dict:
            thumbnail = thumbnail_dict.get('thumbnail', None)
        else:
            thumbnail = None
        new_insert = (f'{id_number}', f'{title}', f'{authors}', f'{published_date}', f'{categories}',
                      f'{average_rating}', f'{ratings_count}', f'{thumbnail}')
        list_of_inserts.append(new_insert)
    for insert in list_of_inserts:
        cur.execute(f"INSERT INTO my_books (id, title, authors, published_date, categories, average_rating, "
                    f"ratings_count, thumbnail) VALUES {insert}")
        con.commit()

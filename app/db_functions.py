import json
import sqlite3
from typing import Any, Dict, Tuple

import requests

BASE_URL = "https://www.googleapis.com/books/v1/volumes?{0}={1}"


def create_db_and_table() -> None:
    con = sqlite3.connect("books_db.db")
    cur = con.cursor()
    create_books_table = """CREATE TABLE IF NOT EXISTS my_books(
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


def update_db(google_data: dict) -> None:
    con = sqlite3.connect("books_db.db")
    cur = con.cursor()
    list_of_inserts = []
    for book in google_data["items"]:
        volume_info = book.get("volumeInfo")
        id_number = book.get("id", "")
        title = volume_info.get("title", "")
        authors = " ".join(map(str, volume_info.get("authors", "")))
        published_date = volume_info.get("publishedDate", "")
        categories = " ".join(map(str, volume_info.get("categories", "")))
        average_rating = volume_info.get("averageRating", "")
        ratings_count = volume_info.get("ratingsCount", "")
        if "imageLinks" in volume_info:
            thumbnail = volume_info["imageLinks"].get("thumbnail", "")
        else:
            thumbnail = ""
        new_insert = (
            f"{id_number}",
            f"{title}",
            f"{authors}",
            f"{published_date}",
            f"{categories}",
            f"{average_rating}",
            f"{ratings_count}",
            f"{thumbnail}",
        )
        list_of_inserts.append(new_insert)
    for insert in list_of_inserts:
        cur.execute("""
            INSERT OR REPLACE INTO my_books (id, title, authors, published_date, categories, average_rating,
            ratings_count, thumbnail) VALUES {};
        """.format(insert))
    con.commit()

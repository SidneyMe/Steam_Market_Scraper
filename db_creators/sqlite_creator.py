import sqlite3
import os

class SQLiteDatabaseCreator:
    """
    A class to create and manage an SQLite database for storing steam items.
    Attributes:
        DB_PATH (str): The path to the SQLite database file.
        items_list (list): A list of dictionaries containing item data.
        conn (sqlite3.Connection): The SQLite database connection object.
        cur (sqlite3.Cursor): The SQLite database cursor object.
    Methods:
        __enter__(): Opens the database connection and returns the instance.
        __exit__(exc_type, exc_val, exc_tb): Closes the database connection.
        open_connection(): Opens the SQLite database connection.
        close_connection(): Closes the SQLite database connection.
        sql_scripts(): Returns the SQL script to create the steam_items table.
        create_db(): Deletes the existing database, creates a new one, and inserts items.
        delete_db(): Deletes the SQLite database file if it exists.
        add_id(): Adds a unique ID to each item in the items_list.
    """
    DB_PATH = 'output/steam_items.db'

    def __init__(self, items_list):
        self.items_list = items_list
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def open_connection(self):
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cur = self.conn.cursor()

    def close_connection(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.cur = None
        self.conn = None

    def sql_scripts(self):
        return """CREATE TABLE IF NOT EXISTS steam_items(
            id INTEGER PRIMARY KEY,
            name TEXT, url TEXT,
            qty INTEGER,
            price TEXT,
            sales_w INTEGER,
            sales_m INTEGER,
            sales_y INTEGER
            )"""

    def create_db(self):
        self.delete_db()
        self.add_id()
        self.open_connection()
        try:
            self.cur.execute(self.sql_scripts())
            self.cur.executemany("""INSERT INTO steam_items(
                id, name, url, qty, price, sales_w, sales_m, sales_y
                ) VALUES (:id, :name, :url, :qty, :price, :sales_w, :sales_m, :sales_y)""", self.items_list)
            self.conn.commit()
        finally:
            self.close_connection()

    def delete_db(self):
        self.close_connection()
        if os.path.exists(self.DB_PATH):
            try:
                os.remove(self.DB_PATH)
                print(f"{self.DB_PATH} has been deleted.")
            except PermissionError:
                print(f"Unable to delete {self.DB_PATH}. It may be in use by another process.")
        else:
            print(f"{self.DB_PATH} does not exist.")

    def add_id(self):
        for i, item in enumerate(self.items_list):
            item['id'] = i
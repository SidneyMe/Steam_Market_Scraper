import sqlite3
import pandas as pd
from abc import ABC

class SQLiteDB(ABC):

    """Abstract method that creates connections with a db"""

    DB_PATH = 'output/steam_items.db'

    def __init__(self, steam_items_df: pd.DataFrame):
        self.steam_items_df = steam_items_df
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def open_connection(self):
        """Creates connection the the db"""
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cur = self.conn.cursor()

    def close_connection(self):
        """Closes connection with the db if the connection was established"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.cur = None
        self.conn = None


class SQLiteDatabaseCreator(SQLiteDB):

    """Creates a sqlite db and inserts items"""

    def sql_script(self) -> str:

        """Returns an sql scrip, which creates a table"""

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
        self.open_connection()
        try:
            self.steam_items_df.to_sql(name='steam_items', con=self.conn, index=False)

        finally:
            self.close_connection()


class SqliteMigration(SQLiteDB):

    """Allows to update generated db"""

    def make_migration(self):

        """Updates the existing db. Overwrites old data"""

        self.open_connection()

        try:
            self.steam_items_df.to_sql(name='steam_items', con=self.conn, if_exists='append', index=False)
            self.conn.commit()

        finally:
            self.close_connection()
        
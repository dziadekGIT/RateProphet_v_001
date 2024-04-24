"""
 App Model
"""

import sqlite3
from typing import Union
import pandas as pd
from datetime import datetime


class SQLiteModel:
    """
    Models for SQlite interaction
    """

    def __init__(self, db_name="config.db"):
        """
        Initializes the database connection and creates tables if they don't exist.
        Parameters:
            param db_name: Name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates database schema if there is none
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "Pairs" (
                "pair_id"    INTEGER,
                "name"    TEXT UNIQUE,
                "description"    TEXT,
                PRIMARY KEY("pair_id")
            );
            """
        )
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS "Values" (
            "timestamp"    DATETIME NOT NULL,
            "value"        REAL NOT NULL,
            "pair_id"      INTEGER,
            FOREIGN KEY("pair_id") REFERENCES "Pairs"("pair_id")
                ON DELETE CASCADE ON UPDATE NO ACTION,
            UNIQUE("pair_id", "timestamp")
        );
        """
        )
        self.conn.commit()

    def add_pair(self, name: str, description: str) -> bool:
        """
        Adds a new currency pair to the Pairs table.
        Parameters:
            param name: The name of the currency pair.
            param description: A description of the currency pair.
        Returns:
            True if the pair was added successfully, False otherwise.
        """
        try:
            self.cursor.execute(
                "INSERT INTO Pairs (name, description) VALUES (?, ?)",
                (name, description),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error updating pair: {e}")
            return False

    def get_pairs(self) -> pd.DataFrame:
        """
        Retrieves all currency pairs from the Pairs table.

        Returns:
            A pandas DataFrame containing all rows from the Pairs table.
        """
        query = "SELECT * FROM Pairs"
        return pd.read_sql_query(query, self.conn)

    def delete_pair(self, name: str) -> bool:
        """
        Deletes a currency pair from the Pairs table by name.
        Parameters:
            param name: The name of the currency pair to delete.
        Returns:
            return: True if the pair was deleted successfully, False otherwise.
        """
        try:
            self.cursor.execute("DELETE FROM Pairs WHERE name = ?", (name,))
            self.conn.commit()
            return True if self.cursor.rowcount > 0 else False
        except sqlite3.Error as e:
            print(f"Error updating pair: {e}")
            return False

    def update_pair(self, name: str, description: str) -> bool:
        """
        Updates the description of a currency pair in the Pairs table by name.
        Parameters:
            param name: The name of the currency pair.
            param description: The new description of the currency pair.
        Returns:
            return: True if the update was successful, False otherwise.
        """
        try:
            self.cursor.execute(
                "UPDATE Pairs SET description = ? WHERE name = ?", (description, name)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating pair: {e}")
            return False
        return True

    def add_values(self, pair_name: str, timeseries: pd.Series) -> bool:
        """
        Adds multiple values for a specific currency pair to the Values table using a Pandas Series.
        Asserts if timeseries is not an instance of pandas.Series.

        Parameters:
            - pair_name: The name of the currency pair.
            - timeseries: A pandas Series where the index represents timestamps and the values represent the currency values.

        Returns:
            - True if the values were added successfully, False otherwise.
        """
        assert isinstance(timeseries, pd.Series), "timeseries must be a pandas Series"
        try:
            self.cursor.execute(
                "SELECT pair_id FROM Pairs WHERE name = ?", (pair_name,)
            )
            pair_id = self.cursor.fetchone()
            if pair_id is None:
                raise ValueError("Pair not found")

            with self.conn:
                for timestamp, value in timeseries.items():
                    # Ensure timestamp is in the correct format for SQLite
                    formatted_timestamp = (
                        timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if isinstance(timestamp, (pd.Timestamp, datetime))
                        else timestamp
                    )
                    self.cursor.execute(
                        'INSERT INTO "Values" (timestamp, value, pair_id) VALUES (?, ?, ?)',
                        (formatted_timestamp, value, pair_id[0]),
                    )
            return True
        except (sqlite3.Error, ValueError) as e:
            print(f"Error adding values: {e}")
            return False

    def delete_values(
        self, pair_name: str, datetime_begin: datetime, datetime_end: datetime
    ) -> int:
        """
        Deletes values for a specific currency pair within a specified datetime range.

        Parameters:
        - pair_name: The name of the currency pair.
        - datetime_begin: The start of the datetime range (inclusive), as a datetime or Pandas Timestamp.
        - datetime_end: The end of the datetime range (inclusive), as a datetime or Pandas Timestamp.

        Returns:
        - The number of rows deleted.
        """
        # Convert datetime_begin and datetime_end to string in ISO 8601 format
        datetime_begin_str = datetime_begin.strftime("%Y-%m-%d %H:%M:%S")
        datetime_end_str = datetime_end.strftime("%Y-%m-%d %H:%M:%S")

        try:
            # First, get the pair_id for the given pair_name
            self.cursor.execute(
                "SELECT pair_id FROM Pairs WHERE name = ?", (pair_name,)
            )
            pair_id = self.cursor.fetchone()
            if pair_id is None:
                raise ValueError("Pair not found")

            # Then, delete values within the specified datetime range for this pair_id
            self.cursor.execute(
                "DELETE FROM 'Values' WHERE pair_id = ? AND timestamp >= ? AND timestamp <= ?",
                (pair_id[0], datetime_begin_str, datetime_end_str),
            )
            self.conn.commit()

            # Return the number of rows deleted
            return self.cursor.rowcount
        except (sqlite3.Error, ValueError) as e:
            print(f"Error deleting values: {e}")
            return 0

    def get_values(
        self, pair_name: str, datetime_begin: datetime, datetime_end: datetime
    ) -> pd.Series:
        """
        Retrieves values for a specific currency pair within a specified datetime range.

        Parameters:
        - pair_name: The name of the currency pair.
        - datetime_begin: The start of the datetime range (inclusive).
        - datetime_end: The end of the datetime range (inclusive).

        Returns:
        - A pandas Series containing the values with the datetime as the index.
        """
        # Convert datetime_begin and datetime_end to string in ISO 8601 format
        datetime_begin_str = datetime_begin.strftime("%Y-%m-%d %H:%M:%S")
        datetime_end_str = datetime_end.strftime("%Y-%m-%d %H:%M:%S")

        # First, get the pair_id for the given pair_name
        self.cursor.execute("SELECT pair_id FROM Pairs WHERE name = ?", (pair_name,))
        pair_id = self.cursor.fetchone()
        if pair_id is None:
            raise ValueError("Pair not found")

        # Then, query the database for values within the specified datetime range for this pair_id
        query = """
                SELECT timestamp, value FROM 'Values'
                WHERE pair_id = ? AND timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
                """
        self.cursor.execute(query, (pair_id[0], datetime_begin_str, datetime_end_str))
        rows = self.cursor.fetchall()

        # Convert the query results to a pandas Series
        if rows:
            timestamps, values = zip(
                *rows
            )  # This unpacks the row tuples into two lists
            series = pd.Series(data=values, index=pd.to_datetime(timestamps))
            return series
        else:
            return pd.Series()  # Return an empty Series if no data is found

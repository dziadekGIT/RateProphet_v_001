# tests/test_sqlite_model.py
import unittest
from rate_prophet.model_db import SQLiteModel
import os
import pandas as pd
from datetime import datetime, timedelta


class TestSQLiteModel(unittest.TestCase):
    test_db = "test_config.db"

    @classmethod
    def setUpClass(cls):
        cls.model = SQLiteModel(db_name=cls.test_db)
        cls.model.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.model.conn.close()
        os.remove(cls.test_db)

    def test_add_pair(self):
        """Test adding a new currency pair."""
        self.assertTrue(self.model.add_pair("EURUSD", "Euro to US Dollar"))
        # Test adding a duplicate pair, which should fail
        self.assertFalse(self.model.add_pair("EURUSD", "Euro to US Dollar"))

    def test_update_pair(self):
        """Test updating an existing currency pair's description."""
        self.model.add_pair("GBPUSD", "British Pound to US Dollar")
        self.assertTrue(self.model.update_pair("GBPUSD", "GBP to USD"))
        pair_df = self.model.get_pairs()
        self.assertTrue(
            pair_df[pair_df["name"] == "GBPUSD"].iloc[0]["description"] == "GBP to USD"
        )

    def test_add_values(self):
        """Test deleting values"""
        # Create a Pandas Series with datetime index
        dates = pd.date_range(start="2022-01-01", end="2022-01-05", freq="h")
        timeseries = pd.Series(1, index=dates)

        # Add values to the database
        self.model.add_pair("TESTPAIR", "Test description")
        result = self.model.add_values("TESTPAIR", timeseries)
        self.assertTrue(result, "Failed to add time series data to the database")

        # Verify the data was inserted correctly
        with self.model.conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM 'Values'")
            data_count = cursor.fetchone()[0]
            self.assertEqual(
                data_count, len(timeseries), "Incorrect number of rows inserted"
            )

    def test_delete_values(self):
        """Test that delete_values correctly deletes the specified rows."""
        # Define the datetime range to delete

        self.model.add_pair("EURUSD(D)", "Euro to US Dollar")
        # Assuming add_values accepts datetime objects or strings for the timestamp
        timeseries = pd.Series(
            [1.1, 1.2, 1.3],
            index=pd.date_range(start="2022-01-01", periods=3, freq="D"),
        )
        self.model.add_values("EURUSD(D)", timeseries)

        datetime_begin = datetime(2022, 1, 2)
        datetime_end = datetime(2022, 1, 3)

        # Call the delete function and get the number of deleted rows
        deleted_rows = self.model.delete_values(
            "EURUSD(D)", datetime_begin, datetime_end
        )

        # Assert that 2 rows were deleted
        self.assertEqual(deleted_rows, 2, "Incorrect number of rows deleted")

        # verify that the remaining values are as expected
        remaining_values = self.model.get_values(
            "EURUSD(D)", datetime(2022, 1, 1), datetime_end
        )
        self.assertEqual(
            len(remaining_values), 1, "Incorrect remaining values after deletion"
        )

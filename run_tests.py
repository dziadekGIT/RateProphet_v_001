# run_tests.py
import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)

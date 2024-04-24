"""
 App Controller
"""

import re
import pandas as pd
import streamlit as st
from rate_prophet.util_timeseries import create_timeseries
from datetime import datetime
from rate_prophet.view_ui_simple import (
    main_page_view,
    left_panel_view,
    header_view,
    currency_manager_view,
    footer_view,
)
from rate_prophet.model_db import SQLiteModel
from rate_prophet.config_utils import AppPage


# Controller
class RateProphetController:
    """
    A controller for the RateProphet application, handling the core logic,
    data manipulation, and interaction between the user interface and the database model.
    """

    def __init__(self):
        self.model: SQLiteModel = SQLiteModel()
        self.current_page: AppPage = None
        self.visualisation_type: str = None
        self.selected_currency_pair: str = None
        self.start_date: datetime = None
        self.end_date: datetime = None
        self.message: str = None
        self.initialise()

    def initialise(self):
        """
        Initializes the RateProphetController instance with initial values
        """
        self.current_page = AppPage.MAIN_PAGE
        self.visualisation_type = "LINE GRAPH"
        pairs_df = self.model.get_pairs()
        self.selected_currency_pair = pairs_df.iloc[0]["name"]
        self.end_date = datetime.now()
        self.start_date = self.end_date - pd.DateOffset(years=5)

    def add_predefied_pair(self):
        """
        Adds predefied currency pair with values to database.
        """
        datetime_begin = datetime(2022, 1, 2)
        datetime_end = datetime(2022, 1, 7)
        pts = create_timeseries(datetime_begin, datetime_end)
        self.model.add_pair("XYZ/FKE", "Predefied test pair")
        self.model.add_values("XYZ/FKE", pts)

    def add_new_pair_from_csv(self, file, name, description="") -> bool:
        """
        Adds provided currency pair with values to database.
        """
        if file and name:
            values = pd.read_csv(file)["value"]
            self.model.add_pair(name, description)  # TODO: no transaction!!!!
            self.model.add_values(name, values)
            return True
        return False

    def delete_selected_pair(self, selected_pair):
        """
        Deletes selected pair from database. Deletes all data.

        Parameters:
               selected_pair (str): The name of the currency pair.
        """
        start = datetime(1970, 1, 1)  # Unix Epoch
        end = datetime.now()
        self.model.delete_values(selected_pair, start, end)
        self.model.delete_pair(selected_pair)

    def draw_left_menu(self):
        """
        draws and manages left panel, reruns if any changes are made in the left panel.
        """
        modified = False
        all_pairs = self.model.get_pairs()
        left_panel_options = left_panel_view(
            pairs=all_pairs,
            selected_currency_pair=self.selected_currency_pair,
            selected_visualisation_type=self.visualisation_type,
            selected_start_date=self.start_date,
            selected_end_date=self.end_date,
            selected_page=self.current_page,
        )

        if self.selected_currency_pair != left_panel_options["selected_pair"]:
            self.selected_currency_pair = left_panel_options["selected_pair"]
            modified = True
        if self.visualisation_type != left_panel_options["visualisation_type"]:
            self.visualisation_type = left_panel_options["visualisation_type"]
            modified = True
        if self.start_date != left_panel_options["start_date"]:
            self.start_date = left_panel_options["start_date"]
            modified = True
        if self.end_date != left_panel_options["end_date"]:
            self.end_date = left_panel_options["end_date"]
            modified = True
        if left_panel_options["selected_page"] is not None:
            self.change_page(left_panel_options["selected_page"])

        if modified:  # this neat trick makes sure menu updates options
            st.rerun()

    def draw_currency_manager_page(self):
        """
        Draws the currency manager page.
        """
        all_pairs = self.model.get_pairs()
        manager_results = currency_manager_view(all_pairs)
        if manager_results is not None:

            if manager_results["uploaded_file"] is not None and re.match(
                r"^[A-Z]{3}/[A-Z]{3}$", manager_results["new_currency_name"]
            ):
                is_added = self.add_new_pair_from_csv(
                    manager_results["uploaded_file"],
                    manager_results["new_currency_name"],
                )
                self.message = "Pair added" if is_added else "Pair not added"
                st.rerun()
            else:
                self.message = "Data validation error"
                st.rerun()

    def change_page(self, page: AppPage):
        """
        Changes the current page of the RateProphet application.
        """
        if page in AppPage:
            self.current_page = page
            st.rerun()

    def start_ui(self):
        """
        Runs and manages UI.
        """
        # st.write((self.start_date, type(self.start_date)))
        header_view(self.message)
        self.draw_left_menu()

        if self.current_page == AppPage.MAIN_PAGE:
            all_pairs = self.model.get_pairs()
            current_pair_values = self.model.get_values(
                pair_name=self.selected_currency_pair,
                datetime_begin=self.start_date,
                datetime_end=self.end_date,
            )
            main_page_view(
                current_pair_values=current_pair_values,
                all_pairs=all_pairs,
                visualisation_type=self.visualisation_type,
            )
        elif self.current_page == AppPage.PAIR_MANAGER_PAGE:
            self.draw_currency_manager_page()

        footer_view()
        self.message = None

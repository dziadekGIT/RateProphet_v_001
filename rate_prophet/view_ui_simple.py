"""
 App UI
"""

from typing import Optional
import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from rate_prophet.config_utils import AppPage

# ------------------- UI Functions -------------------


def plot_data(values: pd.Series, visualisation_type: str):
    """
    Plots the data based on the selected visualization type.

    Parameters:
    - values: pandas DataFrame (Series)
    - visualisation_type: Type of visualization ("LINE GRAPH", "HISTOGRAM")

    """
    if values is None:
        st.write("No values in selected pair")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        if visualisation_type == "LINE GRAPH":
            ax.plot(values, marker="o", linestyle="-", color="b")
            ax.set_title("Timeseries data - line graph")
            ax.set_xlabel("Time")
            ax.set_ylabel("Values")
        elif visualisation_type == "HISTOGRAM":
            ax.hist(values, bins=len(values), color="g", alpha=0.7)
            ax.set_title("Histogram values")
            ax.set_xlabel("Values")
            ax.set_ylabel("Number of occurrences")

        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)


# -------------------- Views -------------------


def header_view(message: Optional[str] = None):
    """
    Renders the header view for the Rate Prophet application.
    """
    st.set_page_config(page_title="Rate Prophet", page_icon="assets/dollar.png")
    if message is not None:
        st.write("System message: " + message)


def footer_view():
    """
    Renders the header view for the Rate Prophet application.
    """
    st.markdown("---")
    st.markdown("Rate Prophet - a simple currency rate prediction tool")
    st.markdown("© 2021 - Data Science Lab")


def main_page_view(
    current_pair_values: pd.Series, all_pairs: list[str], visualisation_type: str
):
    """
    Renders the main page of the Rate Prophet application.

    This function displays the application's header, body, and left panel specific to the main page.
    It handles the main visualization and interaction with currency pair data.

    Parameters:
    - pages: Enum that contains pages available in the application for navigation.
    - values: A pandas DataFrame (Series) containing the values for the selected currency pair.
    - pairs: A pandas DataFrame (Series) containing information on all available currency pairs.
    - visualisation_type: The type of visualization to initialize, defaulting to "LINE GRAPH".

    Returns:
    None
    """
    # Parameter values used:
    st.write("MAIN PAGE")
    st.markdown("---")
    st.header(f"Data visualization of {current_pair_values.name}")

    # Plotting the data
    plot_data(current_pair_values, visualisation_type)


def left_panel_view(
    pairs: list[str],
    selected_currency_pair: str,
    selected_visualisation_type: str,
    selected_start_date: datetime,
    selected_end_date: datetime,
    selected_page: AppPage,
):
    """
    Renders the left panel for the main page.
    """
    with st.sidebar:
        st.title("CONTROL PANEL")
        st.markdown("---")

        st.header("CURRENCIES")
        currently_selected_pair = st.selectbox(
            "Select pair to show",
            pairs["name"].tolist(),
            index=(
                pairs["name"].tolist().index(selected_currency_pair)
                if selected_currency_pair
                else 0
            ),
        )
        st.markdown("---")

        start_date = st.date_input(
            "Start date",
            (
                selected_start_date
                if selected_start_date is not None
                else datetime.now() - pd.DateOffset(months=6)
            ),
        )
        end_date = st.date_input(
            "End date", selected_end_date if selected_end_date else datetime.now()
        )

        st.markdown("---")

        st.header("VISUALISATION TYPE")
        visualisation_types = ["LINE GRAPH", "HISTOGRAM"]
        visualisation_type = st.radio(
            "Select visualisation type",
            visualisation_types,
            index=(
                visualisation_types.index(selected_visualisation_type)
                if selected_visualisation_type
                else 0
            ),
        )

        new_page = None
        st.markdown("---")
        if selected_page == AppPage.MAIN_PAGE:
            if st.button("Edit Currency Pairs"):
                new_page = AppPage.PAIR_MANAGER_PAGE
        else:
            if st.button("Main page"):
                new_page = AppPage.MAIN_PAGE

        return {
            "selected_pair": currently_selected_pair,
            "start_date": start_date,
            "end_date": end_date,
            "visualisation_type": visualisation_type,
            "selected_page": new_page,
        }


def currency_manager_view(
    pairs: list[str],
) -> Optional[dict]:
    """
    Renders the currency manager
    """
    st.title("Currency Manager")

    with st.form("new_series_csv", clear_on_submit=True):
        new_currency_name = st.text_input("Add currency name in format ABC/DEF")
        if len(new_currency_name) > 0 and not re.match(
            r"^[A-Z]{3}/[A-Z]{3}$", new_currency_name
        ):
            st.error("Currency name must be in format ABC/DEF")
        uploaded_file = st.file_uploader(
            "Choose a CSV file", accept_multiple_files=False
        )
        submitted = st.form_submit_button("Upload new series")

    if submitted:
        return {"uploaded_file": uploaded_file, "new_currency_name": new_currency_name}
    else:
        return None

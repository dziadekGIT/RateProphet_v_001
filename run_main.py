from rate_prophet import RateProphetController
import streamlit as st


def run_controller():
    if 'engine' not in st.session_state:
        st.session_state['engine'] = RateProphetController()
    st.session_state['engine'].start_ui() 
    
# Main execution
if __name__ == "__main__":
    
    # streamlit run run_main.py
    run_controller()

    
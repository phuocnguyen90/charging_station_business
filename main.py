# main.py
import streamlit as st
from localization import UI_TEXTS
from components.sidebar import render_sidebar
from components.tab1 import render_tab1
from components.tab2 import render_tab2 
from components.tab3 import render_tab3
from components.tab4 import render_tab4 

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Load the tooltip CSS once at the start of your app.
local_css("tooltip.css")

def main_ui():
    # Language selection in sidebar.
    language = st.sidebar.selectbox("Select Language", options=["EN", "VI"])
    texts = UI_TEXTS[language]
    
    # Local currency settings.
    if language == "VI":
        local_exchange_rate = st.sidebar.number_input("Tỷ giá USD sang VND", value=25500.0)
        currency_symbol = "₫"
    else:
        local_exchange_rate = 1.0
        currency_symbol = "$"
    
    # Render the left sidebar and retrieve simulation parameters.
    params = render_sidebar(language)
    
    # Create Tabs for different reports.
    tab1, tab2, tab3, tab4 = st.tabs([
        texts["tabs"]["main_report"],
        texts["tabs"]["solar_report"],
        texts["tabs"]["roi_analysis"],
        texts["tabs"]["charging_cost"]
    ])
    
    with tab1:
        render_tab1(params, language, local_exchange_rate, currency_symbol)
    with tab2:
        render_tab2(params, language, local_exchange_rate, currency_symbol)
    with tab3:
        render_tab3(params, language, local_exchange_rate, currency_symbol)
    with tab4:
        render_tab4(params, language, local_exchange_rate, currency_symbol)

if __name__ == '__main__':
    main_ui()

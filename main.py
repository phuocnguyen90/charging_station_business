# main.py
import streamlit as st
from localization import UI_TEXTS
from components.sidebar import render_sidebar
from components.tab1 import render_tab1
from components.tab2 import render_tab2 
from components.tab3 import render_tab3
from components.tab4 import render_tab4 
from components.tab5 import render_tab5

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main_ui():
    # Load your custom CSS (optional, if you want to tweak further)
    local_css("styles.css")
    
    # Create a container at the top of the app.
    top_container = st.container()
    # For example, two columns: first takes 90% width, second takes 10%.
    col_left, col_right = top_container.columns([8, 2])
    
    # Leave the left column empty.
    with col_left:
        st.header("EV Charing Station Simulation")
    # In the right column, place our language selector and exchange rate input.
    with col_right:
        language = st.selectbox("Language", ["EN", "VI"], key="language_selector")
        if language == "VI":
            local_exchange_rate = st.number_input("Tỷ giá USD sang VND", value=25500.0, key="exchange_rate")
            currency_symbol = "₫"
        else:
            local_exchange_rate = 1.0
            currency_symbol = "$"
        # Save selections to session state.
        st.session_state["language"] = language
        st.session_state["local_exchange_rate"] = local_exchange_rate
        st.session_state["currency_symbol"] = currency_symbol
    
    # Retrieve values from session state with defaults.
    language = st.session_state.get("language", "EN")
    local_exchange_rate = st.session_state.get("local_exchange_rate", 1.0)
    currency_symbol = st.session_state.get("currency_symbol", "$")
    texts = UI_TEXTS[language]
    
    
    # Optionally, if you still want additional sidebar inputs, call render_sidebar:
    params = render_sidebar(language, local_exchange_rate, currency_symbol)
    
    # Create Tabs for different reports.
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        texts["tabs"]["main_report"],
        texts["tabs"]["solar_report"],
        texts["tabs"]["roi_analysis"],
        texts["tabs"]["charging_cost"],
        "Daily simulation"
    ])
    
    with tab1:
        render_tab1(params, language, local_exchange_rate, currency_symbol)
    with tab2:
        render_tab2(params, language, local_exchange_rate, currency_symbol)
    with tab3:
        render_tab3(params, language, local_exchange_rate, currency_symbol)
    with tab4:
        render_tab4(params, language, local_exchange_rate, currency_symbol)
    with tab5:
        render_tab5(params, language, local_exchange_rate, currency_symbol)

if __name__ == '__main__':
    main_ui()

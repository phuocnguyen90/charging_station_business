import streamlit as st
from localization import UI_TEXTS
import app_default

# Define wizard steps as functions
def wizard_step0():
    st.header("Step 1: General Settings")
    language = st.selectbox("Language", ["EN", "VI"], key="language_selector")
    st.session_state["language"] = language
    texts = UI_TEXTS[language]
    if language == "VI":
        local_exchange_rate = st.number_input("Tỷ giá USD sang VND", value=25500.0, key="exchange_rate")
        currency_symbol = "₫"
    else:
        local_exchange_rate = 1.0
        currency_symbol = "$"
    st.session_state["local_exchange_rate"] = local_exchange_rate
    st.session_state["currency_symbol"] = currency_symbol

    mode = st.selectbox("Mode", ["Basic", "Advanced"], key="mode_selector")
    user_type = st.radio("Are you a Homeowner or a Business?", ["Homeowner", "Business"])
    # Save selections to session state.
    st.session_state["mode"] = mode
    st.session_state["user_type"]= user_type

    col1, col2, col3 = st.columns(3)
    if col1.button("Close Wizard"):
        st.session_state["wizard_step"] = 0
        st.session_state["wizard_complete"]=True
        st.rerun()
    if col3.button("Next"):
        st.session_state["wizard_step"] = 1
        st.rerun()
    return texts

def wizard_step1(texts):    
    st.header(texts["sidebar"]["general_settings"])
    charging_sessions_per_day = st.slider(texts["sidebar"]["average_charging_sessions"], 0, 48, 12)
    num_stations = st.number_input("Number of Stations", min_value=1, value=1)
    charging_station_power = st.number_input("Charging Station Power (kW)", value=30)
    charging_price = st.number_input("Charging Price ($)", value=0.17)
    use_battery = st.checkbox("Use Battery", value=True)
                
    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.wizard_step = 0
    if col2.button("Next"):
        st.session_state.config["charging_sessions_per_day"] = charging_sessions_per_day
        st.session_state.config["num_stations"] = num_stations
        st.session_state.config["charging_station_power"] = charging_station_power
        st.session_state.config["charging_price"] = charging_price
        st.session_state.config["use_battery"] = use_battery
        st.session_state.wizard_step = 2
        st.rerun()

def wizard_step2(texts):
    st.header("Step 3: Solar Settings")
    solar_capacity = st.number_input("Solar Panel Capacity (kW)", value=20)

    # Display avanced settings
    if st.session_state.get("mode", "Basic") == "Advanced":
        solar_randomness = st.slider("Solar Variability", 0.0, 0.5, 0.1, step=0.01)


    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.wizard_step = 1
 
    if col2.button("Next"):
        st.session_state.config["solar_capacity"] = solar_capacity
        st.session_state.config["solar_randomness"] = solar_randomness if st.session_state.get("mode", "Basic") == "Advanced" else app_default.SOLAR_RANDOMNESS  

        st.session_state.wizard_step = 3
        st.rerun()

def wizard_step3(texts):
    st.header("Step 4: Battery Settings")
    use_battery = st.checkbox(
        texts["sidebar"]["use_battery"],
        value=True,
        help=texts["sidebar"]["use_battery_help"]
    )
    st.session_state.config["use_battery"]=use_battery
    # Only show battery configuration if batteries are used.
    if st.session_state.config.get("use_battery", True):
        
        battery_pack_Ah = st.number_input("Battery Pack Capacity (Ah)", value=100)
        
        battery_pack_price = st.number_input("Battery Pack Price ($)", value=1000)
        number_of_battery_packs = st.slider("Number of Battery Packs", 1, 20, 4)
        battery_pack_voltage = app_default.BATTERY_PACK_VOLTAGE
        # Display advanced settings
        if st.session_state.get("mode", "Basic") == "Advanced":
            battery_pack_voltage = st.number_input("Battery Pack Voltage (V)", value=51.2)
            initial_soc_fraction = st.slider("Initial Battery SoC", 0.0, 1.0, 0.5, step=0.01)
            battery_max_charge_rate = st.slider("Battery Max Charge Rate", 0.0, 1.0, 0.5)            
            battery_max_charge_power = battery_max_charge_rate * total_battery_capacity

        total_battery_capacity = number_of_battery_packs * battery_pack_Ah * battery_pack_voltage / 1000
        col1, col2 = st.columns(2)
        if col1.button("Back"):
            st.session_state.wizard_step = 2
        if col2.button("Next"):
            st.session_state.config["battery_pack_Ah"] = battery_pack_Ah
            st.session_state.config["battery_pack_voltage"] = battery_pack_voltage  if st.session_state.get("mode", "Basic") == "Advanced" else app_default.BATTERY_PACK_VOLTAGE  
            st.session_state.config["battery_pack_price"] = battery_pack_price
            st.session_state.config["number_of_battery_packs"] = 0
            st.session_state.config["initial_soc_fraction"] = initial_soc_fraction if st.session_state.get("mode", "Basic") == "Advanced" else app_default.BATTERY_INITIAL_CHARGE  
            st.session_state.config["battery_max_charge_power"] = battery_max_charge_power if st.session_state.get("mode", "Basic") == "Advanced" else app_default.BATTERY_MAX_CHARGE_RATE  
            st.session_state.wizard_step = 4
            st.rerun()
    else:
        st.session_state.wizard_step = 4
        st.rerun()

def wizard_step4(texts):
    # Only display this step in advanced mode
    if st.session_state.get("mode", "Basic") != "Advanced":
        st.session_state.wizard_step = 5
        st.rerun()
    else:
        st.header("Step 4: Battery & Inverter Performance")
        battery_efficiency = st.slider("Battery Round Trip Efficiency", 0.5, 1.0, 0.9, step=0.01)
        inverter_efficiency = st.slider("Inverter Efficiency", 0.5, 1.0, 0.95, step=0.01)
        battery_degradation_cost = st.number_input("Battery Degradation Cost ($/kWh)", value=0.05)
        battery_usage_threshold = st.number_input("Grid Price Threshold ($)", value=0.17)
        
        col1, col2 = st.columns(2)
        if col1.button("Back"):
            st.session_state.wizard_step = 3
        if col2.button("Next"):
            st.session_state.config["battery_efficiency"] = battery_efficiency
            st.session_state.config["inverter_efficiency"] = inverter_efficiency
            st.session_state.config["battery_degradation_cost"] = battery_degradation_cost
            st.session_state.config["battery_usage_threshold"] = battery_usage_threshold
            st.session_state.wizard_step = 5

def wizard_step5(texts):
    st.header("Step 5: Capital Costs & Lifetimes")
    charging_station_cost = st.number_input("Charging Station Cost ($)", value=7000)
    transformer_cost = st.number_input("Transformer Cost ($)", value=1000)
    solar_panel_cost = st.number_input("Solar Panel Cost ($)", value=2000)
    inverter_cost = st.number_input("Inverter Cost ($)", value=3000)
    installation_cost = st.number_input("Installation Cost ($)", value=1000)
    # Display advanced settings
    if st.session_state.get("mode", "Basic") == "Advanced":
        charging_station_lifetime = st.number_input("Charging Station Lifetime (years)", value=10)
        transformer_lifetime = st.number_input("Transformer Lifetime (years)", value=15)
        solar_panel_lifetime = st.number_input("Solar Panel Lifetime (years)", value=25)
        battery_lifetime = st.number_input("Battery Lifetime (years)", value=10)
        inverter_lifetime = st.number_input("Inverter Lifetime (years)", value=10)
        installation_lifetime = st.number_input("Installation Lifetime (years)", value=10)
    
    col1, col2 = st.columns(2)
    if col1.button("Back"):
        st.session_state.wizard_step = 3
    if col2.button("Next"):
        st.session_state.config["charging_station_cost"] = charging_station_cost
        st.session_state.config["transformer_cost"] = transformer_cost
        st.session_state.config["solar_panel_cost"] = solar_panel_cost
        st.session_state.config["inverter_cost"] = inverter_cost
        st.session_state.config["installation_cost"] = installation_cost
        st.session_state.config["charging_station_lifetime"] = charging_station_lifetime if st.session_state.get("mode", "Basic") == "Advanced" else app_default.AVERAGE_EQUIPMENT_LIFETIME    
        st.session_state.config["transformer_lifetime"] = transformer_lifetime if st.session_state.get("mode", "Basic") == "Advanced" else app_default.AVERAGE_EQUIPMENT_LIFETIME
        st.session_state.config["solar_panel_lifetime"] = solar_panel_lifetime if st.session_state.get("mode", "Basic") == "Advanced" else app_default.AVERAGE_SOLAR_PANEL_LIFETIME
        st.session_state.config["battery_lifetime"] = battery_lifetime if st.session_state.get("mode", "Basic") == "Advanced" else app_default.AVERAGE_EQUIPMENT_LIFETIME
        st.session_state.config["inverter_lifetime"] = inverter_lifetime if st.session_state.get("mode", "Basic") == "Advanced" else app_default.AVERAGE_EQUIPMENT_LIFETIME
        st.session_state.config["installation_lifetime"] = installation_lifetime if st.session_state.get("mode", "Basic") == "Advanced" else app_default.AVERAGE_EQUIPMENT_LIFETIME
        st.session_state.wizard_step = 6
        st.rerun()

def wizard_step6(texts):
    # Only display in advanced settings
    if st.session_state.get("mode", "Basic") != "Advanced":
        st.session_state.wizard_complete = True
        st.rerun()
    else:
        st.header("Step 6: Monte Carlo & Advanced Settings")
        monte_iterations = st.number_input("Monte Carlo Iterations", min_value=1, max_value=200, value=50)
        off_peak_rate = st.number_input("Off-Peak Electricity Rate ($/kWh)", value=0.06, step=0.01)
        normal_rate = st.number_input("Normal Electricity Rate ($/kWh)", value=0.108, step=0.01)
        peak_rate = st.number_input("Peak Electricity Rate ($/kWh)", value=0.188, step=0.01)
        peak_start_morning = st.number_input("Morning Peak Start (hour)", value=9.5, step=0.5)
        peak_end_morning = st.number_input("Morning Peak End (hour)", value=11.5, step=0.5)
        peak_start_evening = st.number_input("Evening Peak Start (hour)", value=17.0, step=0.5)
        peak_end_evening = st.number_input("Evening Peak End (hour)", value=20.0, step=0.5)
        custom_profile_str = st.text_area(
            "Custom Usage Profile (24 comma-separated values)",
            value="0.02,0.02,0.02,0.02,0.02,0.02,0.06,0.06,0.06,0.06,0.03,0.03,0.03,0.03,0.03,0.03,0.08,0.08,0.08,0.08,0.08,0.02,0.02,0.02"
        )
        
        col1, col2 = st.columns(2)
        if col1.button("Back"):
            st.session_state.wizard_step = 4
        if col2.button("Finish Wizard"):
            st.session_state.config["monte_iterations"] = monte_iterations
            st.session_state.config["off_peak_rate"] = off_peak_rate
            st.session_state.config["normal_rate"] = normal_rate
            st.session_state.config["peak_rate"] = peak_rate
            st.session_state.config["peak_start_morning"] = peak_start_morning
            st.session_state.config["peak_end_morning"] = peak_end_morning
            st.session_state.config["peak_start_evening"] = peak_start_evening
            st.session_state.config["peak_end_evening"] = peak_end_evening
            try:
                custom_profile = [float(x.strip()) for x in custom_profile_str.split(",")]
                if len(custom_profile) != 24:
                    st.error("Please enter exactly 24 values for the usage profile.")
                    return
                st.session_state.config["custom_profile"] = custom_profile
            except Exception as e:
                st.error("Invalid usage profile. Please ensure all values are numbers.")
                return
            st.session_state.wizard_complete = True

# Initialize session state variables if they do not exist
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 0
if "config" not in st.session_state:
    st.session_state.config = {}
if "wizard_complete" not in st.session_state:
    st.session_state.wizard_complete = False

# Render the wizard steps or main app content based on wizard completion
if not st.session_state.wizard_complete:
    current_language = st.session_state.get("language", "EN")
    texts = UI_TEXTS[current_language]
    if st.session_state.wizard_step == 0:
        texts = wizard_step0()
        texts=UI_TEXTS[st.session_state["language"]]
    elif st.session_state.wizard_step == 1:
        wizard_step1(texts)
    elif st.session_state.wizard_step == 2:
        wizard_step2(texts)
    elif st.session_state.wizard_step == 3:
        wizard_step3(texts)
    elif st.session_state.wizard_step == 4:
        wizard_step4(texts)
    elif st.session_state.wizard_step == 5:
        wizard_step5(texts)
    elif st.session_state.wizard_step == 6:
        wizard_step6(texts)
else:

    # Display main_UI if wizard is complete


    from main import main_ui
    main_ui()
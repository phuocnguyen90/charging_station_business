# sidebar.py
import streamlit as st
from localization import UI_TEXTS
from utils import format_currency


def render_sidebar(language: str,local_exchange_rate:int, currency_symbol:str ) -> dict:
    
    """Render the left sidebar as several collapsible sections and return a dictionary of parameters."""
    texts = UI_TEXTS[language]
    
    # Check if the language has changed, and update the local exchange rate accordingly.
    # Store the current language in session state.
    if "current_language" not in st.session_state or st.session_state["current_language"] != language:
        st.session_state["current_language"] = language
        if language == "VI":
            st.session_state["local_exchange_rate"] = 25500
        else:
            st.session_state["local_exchange_rate"] = 1.0
    local_rate = st.session_state["local_exchange_rate"]

    # Set default base cost values (in USD) if not already present.
    if "charging_price" not in st.session_state:
        st.session_state["charging_price"] = 0.17
    if "charging_station_cost" not in st.session_state:
        st.session_state["charging_station_cost"] = 7000
    if "transformer_cost" not in st.session_state:
        st.session_state["transformer_cost"] = 1000
    if "solar_panel_cost" not in st.session_state:
        st.session_state["solar_panel_cost"] = 2000
    if "inverter_cost" not in st.session_state:
        st.session_state["inverter_cost"] = 3000
    if "installation_cost" not in st.session_state:
        st.session_state["installation_cost"] = 1000
    if "other_operational_cost" not in st.session_state:
        st.session_state["other_operational_cost"] = 10

    # Simulation Settings
    with st.sidebar.expander(texts["sidebar"]["simulation_settings"], expanded=True):

        charging_sessions_per_day = st.slider(
            texts["sidebar"]["average_charging_sessions"],
            0, 48, 12,
            help=texts["sidebar"]["average_charging_sessions_help"]
        )
        num_stations = st.number_input(
            texts["sidebar"]["num_stations"],
            1, 20, 
            help=texts["sidebar"]["num_stations_help"]
        )
        charging_station_power = st.number_input(
            texts["sidebar"]["charging_station_power"],
            value=30,
            help=texts["sidebar"]["charging_station_power_help"]
        )
        # Slider works in base currency
        charging_price_local = st.slider(
            texts["sidebar"]["charging_price"],
            value=st.session_state["charging_price"] * local_rate,
            min_value=0.0,
            max_value=1.0*st.session_state["local_exchange_rate"],
            step=0.01*st.session_state["local_exchange_rate"],
            
            key="charging_price_local",
            help=texts["sidebar"]["charging_price_help"],
            format="%.2f"
        )

        # Display the local currency formatted value
        st.session_state["charging_price"] = charging_price_local / local_rate
        
        st.write("Formatted Price:", format_currency(charging_price_local, 1, currency_symbol))

        other_operational_cost_local=st.number_input(
            texts["sidebar"]["other_operational_cost"],
            value=st.session_state["other_operational_cost"] * local_rate,

            step=float(1*st.session_state["local_exchange_rate"]),
            key="other_operational_cost_local",
            help=texts["sidebar"]["other_operational_cost_help"]
        )
        st.session_state["other_operational_cost"] = other_operational_cost_local / local_rate


        # display use_battery checkbox
        use_battery = st.checkbox(
            texts["sidebar"]["use_battery"],
            value=True,
            help=texts["sidebar"]["use_battery_help"]
        )
        
    # Solar Settings
    with st.sidebar.expander("Solar Settings", expanded=False):
        solar_capacity = st.number_input(
            texts["sidebar"]["solar_panel_capacity"],
            value=20,
            help=texts["sidebar"]["solar_panel_capacity_help"]
        )
        solar_randomness = st.slider(
            texts["sidebar"]["solar_variability"],
            0.0, 0.5, 0.1, step=0.01,
            help=texts["sidebar"]["solar_variability_help"]
        )

    # Battery Pack Configuration (only if battery is used)
    if use_battery:
        with st.sidebar.expander(texts["sidebar"]["battery_pack_configuration"], expanded=False):
            battery_pack_Ah = st.number_input(
                texts["sidebar"]["battery_pack_capacity"],
                value=100,
                help=texts["sidebar"]["battery_pack_capacity_help"]
            )
            battery_pack_voltage = st.number_input(
                texts["sidebar"]["battery_pack_voltage"],
                value=51.2,
                help=texts["sidebar"]["battery_pack_voltage_help"]
            )
            battery_pack_price = st.number_input(
                texts["sidebar"]["battery_pack_price"],
                value=1000,
                help=texts["sidebar"]["battery_pack_price_help"]
            )
            number_of_battery_packs = st.slider(
                texts["sidebar"]["num_battery_packs"],
                1, 20, 4,
                help=texts["sidebar"]["num_battery_packs_help"]
            )
            initial_soc_fraction = st.slider(
                texts["sidebar"]["initial_battery_soc"],
                0.0, 1.0, 0.5,
                help=texts["sidebar"]["initial_battery_soc_help"]
            )
            # Calculate total battery capacity in kWh
            total_battery_capacity = number_of_battery_packs*battery_pack_Ah*battery_pack_voltage / 1000

            battery_max_charge_rate  = st.slider(
                texts["sidebar"]["battery_max_charge_rate"],
                0.0, 1.0, 0.5,
                help=texts["sidebar"]["battery_max_charge_rate_help"]
            )
            battery_max_charge_power = battery_max_charge_rate * total_battery_capacity
            
    else:
        battery_pack_Ah = battery_pack_voltage = battery_pack_price = number_of_battery_packs = 0
        initial_soc_fraction = 0.0
        battery_max_charge_power = 0.0

    # Battery & Inverter Performance
    with st.sidebar.expander(texts["sidebar"]["battery_inverter_performance"], expanded=False):
        battery_efficiency = st.slider(
            texts["sidebar"]["battery_round_trip_efficiency"],
            0.5, 1.0, 0.9, step=0.01,
            help=texts["sidebar"]["battery_round_trip_efficiency_help"]
        )
        inverter_efficiency = st.slider(
            texts["sidebar"]["inverter_efficiency"],
            0.5, 1.0, 0.95, step=0.01,
            help=texts["sidebar"]["inverter_efficiency_help"]
        )
        battery_degradation_cost = st.number_input(
            texts["sidebar"]["battery_degradation_cost"],
            value=0.05,
            help=texts["sidebar"]["battery_degradation_cost_help"]
        )
        battery_usage_threshold = st.number_input(
            texts["sidebar"]["grid_price_threshold"],
            value=0.17,
            help=texts["sidebar"]["grid_price_threshold_help"]
        )

    # Capital Costs & Lifetimes
    with st.sidebar.expander(texts["sidebar"]["capital_costs_lifetimes"], expanded=False):
 
        
        # Display inputs in local currency.
        charging_station_cost_local = st.number_input(
            texts["sidebar"]["charging_station_cost"],
            value=st.session_state["charging_station_cost"] * local_rate,
            key="charging_station_cost_local",
            help=texts["sidebar"]["charging_station_cost_help"]
        )
        st.session_state["charging_station_cost"] = charging_station_cost_local / local_rate
        
        transformer_cost_local = st.number_input(
            texts["sidebar"]["transformer_cost"],
            value=st.session_state["transformer_cost"] * local_rate,
            key="transformer_cost_local",
            help=texts["sidebar"]["transformer_cost_help"]
        )
        st.session_state["transformer_cost"] = transformer_cost_local / local_rate
        solar_panel_cost_local = st.number_input(
            texts["sidebar"]["solar_panel_cost"],
            value=st.session_state["solar_panel_cost"] * local_rate,
            key="solar_panel_cost_local",
            help=texts["sidebar"]["solar_panel_cost_help"]
        )
        st.session_state["solar_panel_cost"] = solar_panel_cost_local / local_rate
        inverter_cost_local = st.number_input(
            texts["sidebar"]["inverter_cost"],
            value=st.session_state["inverter_cost"] * local_rate,
            key="inverter_cost_local",
            help=texts["sidebar"]["inverter_cost_help"]
        )
        st.session_state["inverter_cost"] = inverter_cost_local / local_rate
        installation_cost_local = st.number_input(
            texts["sidebar"]["installation_cost"],
            value=st.session_state["installation_cost"] * local_rate,
            key="installation_cost_local",
            help=texts["sidebar"]["installation_cost_help"]
        )
        st.session_state["installation_cost"] = installation_cost_local / local_rate

        
        charging_station_lifetime = st.number_input(
            texts["sidebar"]["charging_station_lifetime"],
            value=10,
            help=texts["sidebar"]["charging_station_lifetime_help"]
        )
        transformer_lifetime = st.number_input(
            texts["sidebar"]["transformer_lifetime"],
            value=15,
            help=texts["sidebar"]["transformer_lifetime_help"]
        )
        solar_panel_lifetime = st.number_input(
            texts["sidebar"]["solar_panel_lifetime"],
            value=25,
            help=texts["sidebar"]["solar_panel_lifetime_help"]
        )
        battery_lifetime = st.number_input(
            texts["sidebar"]["battery_lifetime"],
            value=10,
            help=texts["sidebar"]["battery_lifetime_help"]
        )
        inverter_lifetime = st.number_input(
            texts["sidebar"]["inverter_lifetime"],
            value=10,
            help=texts["sidebar"]["inverter_lifetime_help"]
        )
        installation_lifetime = st.number_input(
            texts["sidebar"]["installation_lifetime"],
            value=10,
            help=texts["sidebar"]["installation_lifetime_help"]
        )
        # Convert local currency inputs back to USD and update session state.
        st.session_state["charging_station_cost"] = charging_station_cost_local / local_rate
        st.session_state["transformer_cost"] = transformer_cost_local / local_rate
        st.session_state["solar_panel_cost"] = solar_panel_cost_local / local_rate
        st.session_state["inverter_cost"] = inverter_cost_local / local_rate
        st.session_state["installation_cost"] = installation_cost_local / local_rate
        

    # Monte Carlo Simulation Settings
    with st.sidebar.expander(texts["sidebar"]["monte_carlo"], expanded=False):
        monte_iterations = st.number_input(
            texts["sidebar"]["monte_carlo_iterations"],
            1, 200, 50,
            help=texts["sidebar"]["monte_carlo_iterations_help"]
        )

    # Advanced Settings
    with st.sidebar.expander("Advanced Settings", expanded=False):
        # Set default base cost values (in USD) if not already present.
        if "off_peak_rate_local" not in st.session_state:
            st.session_state["off_peak_rate_local"] = 0.06
        if "normal_rate_local" not in st.session_state:
            st.session_state["normal_rate_local"] = 0.11
        if "peak_rate_local" not in st.session_state:
            st.session_state["peak_rate_local"] = 0.19
        if "selling_excess_price" not in st.session_state:
            st.session_state["selling_excess_price"] = 0.07
        # Selling excess settings
        st.subheader(texts["sidebar"]["selling_excess_checkbox"])
        selling_excess = st.checkbox(
            texts["sidebar"]["selling_excess_checkbox"],
            value=True,
            help=texts["sidebar"]["selling_excess_checkbox_help"]
        )
        if selling_excess:
            excess_price_local = st.number_input(
                texts["sidebar"]["selling_excess_price"],
                value=st.session_state["selling_excess_price"] * st.session_state["local_exchange_rate"],
                key="excess_price_local",
                help=texts["sidebar"]["selling_excess_price_help"]
            )
            st.session_state["excess_price"] = excess_price_local / local_rate
            selling_percentage= st.slider(
                texts["sidebar"]["selling_percentage"],
                0.0, 1.0, 0.5,
                help=texts["sidebar"]["selling_percentage_help"]
            )

        # Electricity Rate Settings
        st.subheader("Electricity Rate Settings")
        
        off_peak_rate_local = st.number_input(
            texts["sidebar"]["grid_import_tariff_offpeak"], 
            key="off_peak_rate_local",
            help=texts["sidebar"]["grid_import_tariff_offpeak_help"],
            value=st.session_state["off_peak_rate_local"] * st.session_state["local_exchange_rate"])
        normal_rate_local = st.number_input(
            texts["sidebar"]["grid_import_tariff_normal"],
            key="normal_rate_local",
            help=texts["sidebar"]["grid_import_tariff_normal_help"], 
            value=st.session_state["normal_rate_local"] * st.session_state["local_exchange_rate"])
        peak_rate_local = st.number_input(
            texts["sidebar"]["grid_import_tariff_peak"], 
            key="peak_rate_local",
            help=texts["sidebar"]["grid_import_tariff_peak"],
            value=st.session_state["peak_rate_local"] * st.session_state["local_exchange_rate"])
        peak_start_morning = st.number_input("Morning Peak Start (hour)", value=9.5, step=0.5)
        peak_end_morning = st.number_input("Morning Peak End (hour)", value=11.5, step=0.5)
        peak_start_evening = st.number_input("Evening Peak Start (hour)", value=17.0, step=0.5)
        peak_end_evening = st.number_input("Evening Peak End (hour)", value=20.0, step=0.5)
        st.session_state["off_peak_rate"] = off_peak_rate_local/ local_rate
        st.session_state["normal_rate"] = normal_rate_local/ local_rate
        st.session_state["peak_rate"] = peak_rate_local/ local_rate
        st.session_state["peak_start_morning"] = peak_start_morning
        st.session_state["peak_end_morning"] = peak_end_morning
        st.session_state["peak_start_evening"] = peak_start_evening
        st.session_state["peak_end_evening"] = peak_end_evening

        st.subheader("Usage Profile Settings")
        custom_profile_str = st.text_area(
            "Custom Usage Profile (24 comma-separated values)",
            value="0.02,0.02,0.02,0.02,0.02,0.02,0.06,0.06,0.06,0.06,0.03,0.03,0.03,0.03,0.03,0.03,0.08,0.08,0.08,0.08,0.08,0.02,0.02,0.02"
        )
        try:
            custom_profile = [float(x.strip()) for x in custom_profile_str.split(",")]
            if len(custom_profile) == 24:
                st.session_state.custom_profile = custom_profile
            else:
                st.warning("Please enter exactly 24 values.")
        except Exception as e:
            st.error("Invalid input for usage profile.")

    # Default values for when battery is not used.
    if not use_battery:
        battery_pack_Ah = 0
        battery_pack_voltage = 0
        battery_pack_price = 0
        number_of_battery_packs = 0
        initial_soc_fraction = 0.0
        battery_max_charge_power = 0.0

    return {
        "charging_sessions_per_day": charging_sessions_per_day,
        "charging_station_power": charging_station_power,
        "daily_ev_demand": charging_station_power * charging_sessions_per_day / 2,
        "num_stations": num_stations,
        "charging_price":  st.session_state["charging_price"],
        "solar_capacity": solar_capacity,
        "solar_randomness": solar_randomness,
        "use_battery": use_battery,
        "battery_pack_Ah": battery_pack_Ah,
        "battery_pack_voltage": battery_pack_voltage,
        "battery_pack_price": battery_pack_price,
        "battery_cost": battery_pack_price * number_of_battery_packs,
        "battery_max_charge_power": battery_max_charge_power,
        "number_of_battery_packs": number_of_battery_packs,
        "battery_capacity": battery_pack_Ah * number_of_battery_packs,
        "battery_initial_soc_fraction": initial_soc_fraction,
        "battery_efficiency": battery_efficiency,
        "inverter_efficiency": inverter_efficiency,
        "battery_degradation_cost": battery_degradation_cost,
        "battery_usage_threshold": battery_usage_threshold,
        "station_cost": st.session_state["charging_station_cost"],
        "transformer_cost": st.session_state["transformer_cost"],
        "solar_panel_cost": st.session_state["solar_panel_cost"],
        "inverter_cost": st.session_state["inverter_cost"],
        "installation_cost": st.session_state["installation_cost"],
        "other_operational_cost":st.session_state["other_operational_cost"],
        "charging_station_lifetime": charging_station_lifetime,
        "transformer_lifetime": transformer_lifetime,
        "solar_panel_lifetime": solar_panel_lifetime,
        "battery_lifetime": battery_lifetime,
        "inverter_lifetime": inverter_lifetime,
        "installation_lifetime": installation_lifetime,
        "monte_iterations": monte_iterations,
        "selling_excess": selling_excess,
        "selling_excess_price": st.session_state["excess_price"],
        "selling_percentage": selling_percentage,
        "peak_start_morning": peak_start_morning,
        "peak_end_morning": peak_end_morning,
        "peak_start_evening": peak_start_evening,
        "peak_end_evening": peak_end_evening,
        "custom_profile": custom_profile
    }

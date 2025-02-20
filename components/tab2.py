# tab2.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils import simulate_ev_station, annualize_results, format_currency, simulate_solar_system, simulate_grid_only
from localization import UI_TEXTS
import numpy as np


def render_tab2(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    """Render the content for Tab 21 (Solar production report) using the provided parameters."""
    texts = UI_TEXTS[language]
    st.header("Solar Production/Consumption Details")
    st.markdown("""
    This report provides detailed information on the solar power production for Buon Ma Thuot, Vietnam.
    It shows:
    - **Total Solar Production**
    - **Solar Energy Delivered Directly for EV Charging**
    - **Solar Energy Used for Battery Charging**
    - **Unused Solar Energy**
    """)
    sim_results = simulate_ev_station(params, seed=42)
    df_hourly = pd.DataFrame(sim_results["hourly_details"])

    # "solar_prod" is the key for total solar production
    total_solar = df_hourly["solar_prod"].sum()
    # "direct_solar" corresponds to solar energy used directly for EV charging
    solar_used_direct = df_hourly["direct_solar"].sum()
    # "battery_charged" includes energy used to charge the battery (from solar and grid),
    # so if you want only the solar-to-battery portion, you may need to adjust your simulation
    # or use an alternative calculation. For now, we'll use it directly.
    solar_to_batt = df_hourly["battery_charged"].sum()

    unused_solar = total_solar - (solar_used_direct + solar_to_batt)

    st.write(f"**Total Solar Production:** {total_solar:.2f} kWh")
    st.write(f"**Solar Energy Used Directly for EV Charging:** {solar_used_direct:.2f} kWh")
    st.write(f"**Solar Energy Used for Battery Charging:** {solar_to_batt:.2f} kWh")
    st.write(f"**Unused Solar Energy:** {unused_solar:.2f} kWh")
    fig3, ax3 = plt.subplots(figsize=(10,5))
    ax3.plot(sim_results["time"], sim_results["solar_total"], label="Total Solar Production", color="orange")
    ax3.plot(sim_results["time"], sim_results["solar_used"], label="Solar Used for EV Charging", color="green")
    ax3.plot(sim_results["time"], sim_results["solar_to_battery"], label="Solar to Battery", color="blue")
    ax3.set_xlabel("Time (hours)")
    ax3.set_ylabel("Energy (kWh)")
    ax3.legend()
    st.pyplot(fig3)
    labels = ['EV Charging', 'Battery Charging', 'Unused']
    fig4, ax4 = plt.subplots(figsize=(6,6))
    ax4.pie([solar_used_direct, solar_to_batt, unused_solar], labels=labels, autopct='%1.1f%%', startangle=90)
    ax4.axis('equal')
    st.pyplot(fig4)
    st.info("Solar Model Explanation: Solar irradiance is modeled with a sine function between 6:00 and 18:00. Production per step = Solar Capacity × I(t) × dt × RandomFactor.")

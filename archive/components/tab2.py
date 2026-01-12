import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils import simulate_ev_station
from localization import UI_TEXTS
import numpy as np

def render_tab2(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    """Render the Solar Production/Consumption report for one day."""
    texts = UI_TEXTS[language]
    st.header("Solar Production/Consumption Details")
    st.markdown("""
    This report provides detailed information on the solar power production.
    It shows:
    - **Total Solar Production**
    - **Solar Energy Delivered Directly for EV Charging**
    - **Solar Energy Used for Battery Charging (from solar)**
    - **Unused Solar Energy**
    """)
    
    # Run the one-day simulation.
    sim_results = simulate_ev_station(params, seed=42)
    
    # Create a DataFrame using the one-day arrays.
    df_hourly = pd.DataFrame({
        "time": sim_results["time_arr"],
        "ev_demand": sim_results["demand_arr"],
        "solar_total": sim_results["solar_total_arr"],
        "direct_solar": sim_results["solar_used_arr"],
        "solar_to_battery": sim_results["solar_to_battery_arr"],
        "grid_import": sim_results["grid_import_arr"],
        "battery_discharged": sim_results["battery_discharged_arr"],
        "solar_sold": sim_results["solar_sold_arr"]
    })
    
    # Aggregate solar values from the one-day simulation.
    total_solar = df_hourly["solar_total"].sum()
    solar_used_direct = df_hourly["direct_solar"].sum()
    solar_to_batt = df_hourly["solar_to_battery"].sum()
    unused_solar = total_solar - (solar_used_direct + solar_to_batt)
    
    st.write(f"**Total Solar Production:** {total_solar:.2f} kWh")
    st.write(f"**Solar Energy Used Directly for EV Charging:** {solar_used_direct:.2f} kWh")
    st.write(f"**Solar Energy Used for Battery Charging:** {solar_to_batt:.2f} kWh")
    st.write(f"**Unused Solar Energy:** {unused_solar:.2f} kWh")
    
    # Plot the solar production curves.
    fig3, ax3 = plt.subplots(figsize=(10,5))
    ax3.plot(sim_results["time_arr"], sim_results["solar_total_arr"], label="Total Solar Production", color="orange")
    ax3.plot(sim_results["time_arr"], sim_results["solar_used_arr"], label="Solar Used for EV Charging", color="green")
    ax3.plot(sim_results["time_arr"], sim_results["solar_to_battery_arr"], label="Solar to Battery", color="blue")
    ax3.set_xlabel("Time (hours)")
    ax3.set_ylabel("Energy (kWh)")
    ax3.legend()
    st.pyplot(fig3)
    
    # Create a pie chart of solar usage breakdown.
    labels = ['EV Charging', 'Battery Charging', 'Unused']
    fig4, ax4 = plt.subplots(figsize=(6,6))
    ax4.pie([solar_used_direct, solar_to_batt, unused_solar], labels=labels, autopct='%1.1f%%', startangle=90)
    ax4.axis('equal')
    st.pyplot(fig4)
    
    st.info("Solar Model Explanation: Solar irradiance is modeled with a sine function between 6:00 and 18:00. Production per step = Solar Capacity × I(t) × dt × RandomFactor.")

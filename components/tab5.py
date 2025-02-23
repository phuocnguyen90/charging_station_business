import streamlit as st
import pandas as pd
import plotly.express as px
from utils import run_simulation_system, ev_demand_half_hour
from localization import UI_TEXTS

def render_tab5(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    texts = UI_TEXTS[language]
    st.header("Typical Day Operational Detail")
    st.markdown("""
    This report shows a detailed breakdown of a typical day (0–24 hours) at 30‑minute resolution.  
    The simulation displays:
    - EV charging demand (indicating when a vehicle is charging)
    - Grid import for EV charging
    - Solar production available
    - Direct solar usage for EV charging
    - Battery charging from solar (and grid)
    - Battery state‐of‐charge (SoC)
    - Solar energy sold (if any)
    """)
    
    # Set simulation to 1 day using the deterministic half‑hour EV demand generator.
    params_day = params.copy()
    params_day["simulation_days"] = 1
    
    sim_data = run_simulation_system(params_day, ev_demand_half_hour)
    
    # Build a DataFrame from the half-hour arrays.
    df = pd.DataFrame({
         "Time (hr)": sim_data["time_arr"],  # 0 to 24 in 0.5 increments
         "EV Demand (kWh)": sim_data["demand_arr"],
         "Grid Import (kWh)": sim_data["grid_import_arr"],
         "Solar Production (kWh)": sim_data["solar_total_arr"],
         "Direct Solar (kWh)": sim_data["solar_used_arr"],
         "Battery Charging from Solar (kWh)": sim_data["solar_to_battery_arr"],
         "Battery Charging from Grid (kWh)": sim_data["grid_to_battery_arr"],
         "Battery SoC (kWh)": sim_data["battery_soc_arr"],
         "Solar Sold (kWh)": sim_data["solar_sold_arr"]
    })
    
    # For an hourly summary, group every two 30-minute rows (averaging)
    df["Hour"] = (df["Time (hr)"] // 1).astype(int)
    df_hourly = df.groupby("Hour").mean().reset_index()
    
    st.subheader("Detailed 30-Minute Data")
    st.dataframe(df)
    
    st.subheader("Aggregated Hourly Summary")
    st.dataframe(df_hourly)
    
    # Plot 1: Key energy flows over the day (half-hourly resolution)
    fig1 = px.line(df, x="Time (hr)", y=["EV Demand (kWh)", "Grid Import (kWh)", "Solar Production (kWh)", "Direct Solar (kWh)"],
                   title="Typical Day: Energy Flows (Half-Hourly)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Plot 2: Battery operations over the day
    fig2 = px.line(df, x="Time (hr)", y=["Battery Charging from Solar (kWh)", "Battery Charging from Grid (kWh)", "Battery SoC (kWh)"],
                   title="Typical Day: Battery Operations (Half-Hourly)")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.info("Note: The simulation is performed at 30-minute intervals to capture intraday variations. "
            "The hourly summary aggregates every two 30-minute intervals.")

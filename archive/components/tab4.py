# tab4.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils import annualize_results, format_currency, simulate_solar_only, simulate_grid_only, simulate_solar_storage, compute_infrastructure_cost, simulate_ev_station, get_hourly_details
from localization import UI_TEXTS
import numpy as np

def render_tab4(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    """Render the content for Tab 21 (Solar production report) using the provided parameters."""
    texts = UI_TEXTS[language]
    st.title("Charging Cost & Power Consumption Breakdown")
    st.markdown("""
    This simulation compares the effective charging cost (per kWh) and annual ROI for an EV charging station under three scenarios:
    
    1. **Grid Only:** All energy is purchased from the grid.
    2. **Solar Only:** A solar array is installed. EV demand is met by solar when available; shortfalls are purchased from the grid.
    3. **Solar + Storage:** A battery is used to store excess solar energy for later use.
    
    Energy and cost are calculated hourly over a typical day.
    """)
    
    # Using the common params, run simulation for scenario comparisons.
    scenarios = {
        "Grid Only": simulate_grid_only(params),
        "Solar Only": simulate_solar_only(params),
        "Solar + Storage": simulate_solar_storage(params)
    }
    results = {}
    for key, sim_res in scenarios.items():
        ann = annualize_results(sim_res, params)
        # Merge the annualized values with the simulation results.
        results[key] = {**sim_res, **ann}
    
    # Compute the total initial capital cost 

    total_capital_cost = compute_infrastructure_cost(params,False)

    # Build summary rows, now including ROI computed as net profit divided by total_capital_cost.
    summary = []
    for scenario, res in results.items():
        # Compute ROI here:
        roi = res["net_profit"] / total_capital_cost if total_capital_cost > 0 else float('nan')
        summary.append({
            "Scenario": scenario,
            "Daily Energy (kWh)": round(res["annual_energy"] / 365, 1),
            "Effective Cost ($/kWh)": round(res["effective_cost_per_kwh"], 3),
            "Annual Revenue ($)": round(res["annual_revenue"], 2),
            "Annual Operating Cost ($)": round(res["annual_operating_cost"], 2),
            "Annual Capital Cost ($)": round(res["annual_capital_cost"], 2),
            "Net Annual Profit ($)": round(res["net_profit"], 2),
            "ROI (%)": round(roi * 100, 1) if not np.isnan(roi) else "N/A"
        })
    df_summary = pd.DataFrame(summary)
    st.subheader("Scenario Summary")
    st.dataframe(df_summary)
    
    st.subheader("Detailed Hourly Data (Solar + Storage)")
    sim_data = simulate_ev_station(params, seed=42)
    if "Solar + Storage" in results:
        df_hourly = get_hourly_details(sim_data)
        st.dataframe(df_hourly)
    
    st.subheader("Visualizations")
    # Visualization 1: Line Chart for Cost per Hour with a Second Y-Axis Column Chart for Effective Cost ($/kWh)
    if "Solar + Storage" in results:
        
        
        # Ensure the 'cost' column exists. If not, create it from cost_grid + cost_battery.
        if "cost" not in df_hourly.columns:
            df_hourly["cost"] = df_hourly.get("cost_grid", 0) + df_hourly.get("cost_battery", 0)
        
        # Retrieve 'ev_demand' from the DataFrame. If missing, use zeros.
        ev_demand_data = df_hourly.get("ev_demand", np.zeros(len(df_hourly)))
        
        # Calculate effective cost per kWh for each hour (avoid division by zero).
        # Effective cost per kWh = cost / ev_demand
        effective_cost_per_kwh = np.where(ev_demand_data > 0, df_hourly["cost"] / ev_demand_data, np.nan)
        
        fig_cost, ax_cost = plt.subplots(figsize=(10, 4))
        
        # Primary y-axis: plot hourly cost as a red line.
        ax_cost.plot(df_hourly["hour"], df_hourly["cost"], marker='o', linestyle='-', color='red', label="Hourly Cost ($)")
        ax_cost.set_xlabel("Hour of Day")
        ax_cost.set_ylabel("Hourly Cost ($)", color='red')
        ax_cost.tick_params(axis='y', labelcolor='red')
        
        # Secondary y-axis: plot effective cost per kWh as a blue bar chart.
        ax2 = ax_cost.twinx()
        bar_width = 0.8
        ax2.bar(df_hourly["hour"], effective_cost_per_kwh, width=bar_width, color='blue', alpha=0.4, label="Effective Cost ($/kWh)")
        ax2.set_ylabel("Effective Cost ($/kWh)", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        # Combine legends from both axes
        from matplotlib.patches import Patch
        red_line = ax_cost.lines[0]
        blue_patch = Patch(facecolor='blue', alpha=0.4, label="Effective Cost ($/kWh)")
        ax_cost.legend([red_line, blue_patch], ["Hourly Cost ($)", "Effective Cost ($/kWh)"], loc="upper left")
        
        st.pyplot(fig_cost)

        
        # Visualization 2: Stacked Bar Chart for Energy Breakdown
        fig_energy, ax_energy = plt.subplots(figsize=(10, 4))
        width = 0.8
        # Make sure that your simulation function populates these keys ("direct_solar", "battery_discharged", "grid_used").
        p1 = ax_energy.bar(df_hourly["hour"], df_hourly["direct_solar"], width, label="Direct Solar")
        p2 = ax_energy.bar(df_hourly["hour"], df_hourly["battery_discharged"], width,
                        bottom=df_hourly["direct_solar"], label="Battery Discharge")
        bottom_stack = df_hourly["direct_solar"] + df_hourly["battery_discharged"]
        p3 = ax_energy.bar(df_hourly["hour"], df_hourly["grid_used"], width,
                        bottom=bottom_stack, label="Grid Energy")
        ax_energy.set_title("EV Charging Energy Breakdown (kWh per Hour)")
        ax_energy.set_xlabel("Hour of Day")
        ax_energy.set_ylabel("Energy (kWh)")
        ax_energy.legend()
        st.pyplot(fig_energy)
    
    st.info("Charging Cost Explanation: The cost per hour is the sum of the grid cost (energy used × tariff) and battery degradation cost (energy discharged × degradation cost). The stacked bar chart shows how EV demand is met by direct solar, battery discharge (ensuring battery does not drop below 20% SoC), and grid energy.")

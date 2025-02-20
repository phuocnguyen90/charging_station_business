# tab3.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils import simulate_ev_station, annualize_results, compute_roi
from localization import UI_TEXTS
from sklearn.linear_model import LinearRegression
import numpy as np


def render_tab3(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    """Render the content for Tab 21 (Solar production report) using the provided parameters."""
    texts = UI_TEXTS[language]
    st.header("ROI Analysis and Sensitivity")
    st.markdown("""
    This section runs a grid search over a discrete design space to compare ROI for different configurations.
    
    **Design Variables:**
    - Number of stations
    - Inverter type ('normal' means no battery; 'hybrid' means battery enabled)
    - Number of battery packs (for hybrid systems)
    - Solar capacity (kW)
    """)
    results_list = []
    for num_stations in [1, 2]:
        for inverter_type in ['normal', 'hybrid']:
            if inverter_type == 'normal':
                for solar_cap in range(2, 19, 2):
                    num_battery_packs = 0
                    roi, annual_profit, capital_cost = compute_roi(params)
                    results_list.append({
                        'num_stations': num_stations,
                        'inverter_type': 0,  # normal encoded as 0
                        'num_battery_packs': num_battery_packs,
                        'solar_capacity': solar_cap,
                        'roi': roi,
                        'annual_profit': annual_profit,
                        'capital_cost': capital_cost,
                    })
            else:
                for num_battery_packs in [1, 2, 3, 4]:
                    for solar_cap in range(2, 19, 2):
                        roi, annual_profit, capital_cost = compute_roi(params)
                        results_list.append({
                            'num_stations': num_stations,
                            'inverter_type': 1,  # hybrid encoded as 1
                            'num_battery_packs': num_battery_packs,
                            'solar_capacity': solar_cap,
                            'roi': roi,
                            'annual_profit': annual_profit,
                            'capital_cost': capital_cost,
                        })
    df_roi = pd.DataFrame(results_list)
    st.write("All configurations:")
    st.dataframe(df_roi)
    best_config = df_roi.loc[df_roi['roi'].idxmax()]
    st.markdown("**Best configuration based on ROI:**")
    st.write(best_config)
    # Regression sensitivity analysis
    X = df_roi[['num_stations', 'inverter_type', 'num_battery_packs', 'solar_capacity']]
    y = df_roi['roi']
    model = LinearRegression()
    model.fit(X, y)
    st.markdown("**Regression Model Coefficients:**")
    st.write(f"Intercept: {model.intercept_:.3f}")
    st.write(f"Coefficients: {model.coef_}")
    st.info("ROI Explanation: ROI = (Annual Profit) / (Total Capital Cost). Annual profit is computed from annualized energy and costs.")
    solar_caps = np.linspace(2, 40, 20)  # vary solar capacity from 2 to 40 kW
    battery_invest = range(0, 11)         # vary number of battery packs from 0 to 10
    results = []

    for solar in solar_caps:
        for batt in battery_invest:
            params["solar_capacity"] = solar
            if batt > 0:
                params["use_battery"] = True
                params["number_of_battery_packs"] = batt
            else:
                params["use_battery"] = False
                params["number_of_battery_packs"] = 0
            # Compute ROI or effective cost per kWh
            roi, annual_profit, capital_cost = compute_roi(params)
            ann_results = annualize_results(simulate_ev_station(params, seed=42), params)
            results.append({
                "solar_capacity": solar,
                "battery_packs": batt,
                "roi": roi,
                "effective_cost": ann_results["effective_cost_per_kwh"],
                "capital_cost": capital_cost
            })
    df_sens = pd.DataFrame(results)

    # Plot sensitivity curves:
    fig, ax = plt.subplots(figsize=(8, 4))
    for bp in sorted(df_sens["battery_packs"].unique()):
        sub = df_sens[df_sens["battery_packs"] == bp]
        ax.plot(sub["solar_capacity"], sub["roi"], label=f'{bp} Battery Packs')
    ax.set_xlabel("Solar Capacity (kW)")
    ax.set_ylabel("ROI")
    ax.set_title("ROI Sensitivity to Solar Investment")
    ax.legend()
    st.pyplot(fig)
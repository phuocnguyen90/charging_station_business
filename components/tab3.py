import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import simulate_ev_station, annualize_results, compute_roi, simulate_solar_storage
from localization import UI_TEXTS
from sklearn.linear_model import LinearRegression

def render_tab3(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    texts = UI_TEXTS[language]
    st.header("ROI Analysis and Sensitivity")
    st.markdown(
        "This section allows you to explore different configurations and analyze the sensitivity of ROI "
        "by adjusting key simulation parameters. You can change the ranges for solar capacity, battery packs, "
        "number of stations, the expected daily electricity charged, and the effective cost per kWh. "
        "The default values are imported from the sidebar, but all values are fully editable for scenario analysis."
    )

    # --- Simulation Parameters Input ---
    with st.expander("Simulation Parameters", expanded=False):
        solar_min = st.number_input("Minimum Solar Capacity (kW)", value=5, step=5)
        solar_max = st.number_input("Maximum Solar Capacity (kW)", value=40, step=5)
        solar_step = st.number_input("Solar Capacity Step (kW)", value=5, step=5)
        battery_min = st.number_input("Minimum Battery Packs", value=0, step=2)
        battery_max = st.number_input("Maximum Battery Packs", value=10, step=2)
        battery_step = st.number_input("Battery Pack Step", value=2, step=2)
        num_stations_str = st.text_input("Number of Stations (comma-separated)", value="1,2")
        inverter_types = st.multiselect("Select Inverter Types", options=["normal", "hybrid"], default=["normal", "hybrid"])
        expected_daily_charge = st.number_input(
            "Expected Electricity Charged per Day (kWh)",
            value=params.get("daily_ev_demand", 50),
            step=1.0  # Changed step to float to match value's type
        )
        effective_cost_input = st.number_input(
            "Effective Cost per kWh (Solar & Grid Balancing)",
            value=0.10,
            step=0.01
        )

    # Update params with the new simulation parameters
    params["expected_daily_charge"] = expected_daily_charge
    params["user_effective_cost"] = effective_cost_input

    # Process number of stations input
    try:
        num_stations_list = [int(x.strip()) for x in num_stations_str.split(",") if x.strip().isdigit()]
        if not num_stations_list:
            st.error("Please enter valid numbers for the number of stations.")
            return
    except Exception as e:
        st.error("Error processing the number of stations input.")
        return

    # --- Grid Search Simulation Loop ---
    results_list = []
    for num_station in num_stations_list:
        for inverter_type in inverter_types:
            if inverter_type == "normal":
                # For solar-only, use the dedicated solar simulation function.
                for solar_cap in range(int(solar_min), int(solar_max) + 1, int(solar_step)):
                    params["num_stations"] = num_station
                    params["solar_capacity"] = solar_cap
                    params["use_battery"] = False
                    params["number_of_battery_packs"] = 0
                    # Run the solar-only simulation (which includes solar production and revenue)
                    sim_results = simulate_solar_storage(params)
                    # Annualize results
                    ann_results = annualize_results(sim_results, params)
                    # Compute annual revenue from the simulation result
                    annual_revenue = sim_results.get("total_revenue", 0) * 365
                    # For capital cost, combine the various components
                    station_cost = params["station_cost"] * params["num_stations"]
                    transformer_cost = params["transformer_cost"]
                    solar_panel_cost = params["solar_panel_cost"]
                    inverter_cost = params["inverter_cost"] * params["num_stations"]
                    installation_cost = params["installation_cost"]
                    total_capital_cost = station_cost + transformer_cost + solar_panel_cost + inverter_cost + installation_cost
                    # Determine net profit from the simulation (here using the aggregated operating cost and depreciation)
                    annual_operating_cost = ann_results["annual_operating_cost"]
                    annual_capital_cost = ann_results["annual_capital_cost"]
                    annual_profit = annual_revenue - (annual_operating_cost + annual_capital_cost)
                    roi = annual_profit / total_capital_cost if total_capital_cost != 0 else np.nan

                    results_list.append({
                        "num_stations": num_station,
                        "inverter_type": 0,  # normal (solar-only) encoded as 0
                        "num_battery_packs": 0,
                        "solar_capacity": solar_cap,
                        "roi": roi,
                        "annual_profit": annual_profit,
                        "capital_cost": total_capital_cost,
                        "effective_cost": ann_results.get("effective_cost_per_kwh", None),
                        "expected_daily_charge": expected_daily_charge,
                        "user_effective_cost": effective_cost_input
                    })
            elif inverter_type == "hybrid":
                # For hybrid (solar + battery), keep your existing simulation.
                for solar_cap in range(int(solar_min), int(solar_max) + 1, int(solar_step)):
                    for battery_packs in range(int(battery_min), int(battery_max) + 1, int(battery_step)):
                        params["num_stations"] = num_station
                        params["solar_capacity"] = solar_cap
                        params["use_battery"] = True
                        params["number_of_battery_packs"] = battery_packs
                        roi, annual_profit, capital_cost = compute_roi(params)
                        sim_result = simulate_ev_station(params, seed=42)
                        ann_results = annualize_results(sim_result, params)
                        effective_cost = ann_results.get("effective_cost_per_kwh", None)
                        results_list.append({
                            "num_stations": num_station,
                            "inverter_type": 1,  # hybrid encoded as 1
                            "num_battery_packs": battery_packs,
                            "solar_capacity": solar_cap,
                            "roi": roi,
                            "annual_profit": annual_profit,
                            "capital_cost": capital_cost,
                            "effective_cost": effective_cost,
                            "expected_daily_charge": expected_daily_charge,
                            "user_effective_cost": effective_cost_input
                        })

    df_roi = pd.DataFrame(results_list)
    st.markdown("#### Simulation Results")
    st.dataframe(df_roi)

    if not df_roi.empty:
        best_config = df_roi.loc[df_roi["roi"].idxmax()]
        st.markdown("**Best Configuration Based on ROI:**")
        st.write(best_config)

        # --- Regression Sensitivity Analysis ---
        X = df_roi[["num_stations", "inverter_type", "num_battery_packs", "solar_capacity"]]
        y = df_roi["roi"]
        model = LinearRegression()
        model.fit(X, y)
        st.markdown("**Regression Model Coefficients:**")
        st.write(f"Intercept: {model.intercept_:.3f}")
        st.write(f"Coefficients: {model.coef_}")
        st.info("ROI Explanation: ROI = (Annual Profit) / (Total Capital Cost). Annual profit is computed from annualized energy and costs.")

        df_roi["Config"] = df_roi.apply(
            lambda row: "Normal (No Battery)" if row["inverter_type"] == 0 else f"Hybrid ({row['num_battery_packs']} Packs)", axis=1
        )

        # --- Interactive ROI Sensitivity Plot ---
        fig_roi = px.line(
            df_roi, x="solar_capacity", y="roi", color="Config", markers=True,
            title="ROI Sensitivity to Solar Capacity"
        )
        fig_roi.update_layout(xaxis_title="Solar Capacity (kW)", yaxis_title="ROI")
        st.plotly_chart(fig_roi)

        # --- Interactive Effective Cost Sensitivity Plot ---
        fig_cost = px.line(
            df_roi, x="solar_capacity", y="effective_cost", color="Config", markers=True,
            title="Effective Cost per kWh Sensitivity"
        )
        fig_cost.update_layout(xaxis_title="Solar Capacity (kW)", yaxis_title="Effective Cost per kWh")
        st.plotly_chart(fig_cost)
    else:
        st.warning("No simulation results available. Please check your input parameters.")

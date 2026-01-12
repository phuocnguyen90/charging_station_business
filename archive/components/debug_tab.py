import streamlit as st
from utils import simulate_ev_station, simulate_solar_only, simulate_grid_only, aggregate_results
from localization import UI_TEXTS

def render_debug_tab(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    st.header("Debug Tab: All Variables")

    st.subheader("Input Parameters")
    st.json(params)

    st.subheader("EV Station Simulation Results (simulate_ev_station)")
    sim_results = simulate_ev_station(params, seed=42)
    st.json(sim_results)

    st.subheader("Aggregated Results (annualize_results)")
    agg_results = aggregate_results(sim_results, 1)
    st.json(agg_results)

    st.subheader("Solar Simulation Results (simulate_solar_only)")
    solar_results = simulate_solar_only(params)
    st.json(solar_results)

    st.subheader("Grid-Only Simulation Results (simulate_grid_only)")
    grid_results = simulate_grid_only(params)
    st.json(grid_results)

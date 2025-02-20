# tab1.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils import simulate_ev_station, annualize_results, format_currency, simulate_solar_system, simulate_grid_only
from localization import UI_TEXTS


def render_tab1(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    """Render the content for Tab 1 (Main Report) using the provided parameters."""
    texts = UI_TEXTS[language]
    st.header(texts["tabs"]["main_report"])
        
    # Run simulation for the defined period (e.g., 30 days)
    sim_results = simulate_ev_station(params, seed=42)
    ann_results = annualize_results(sim_results, params)
    
    # ---------------------------------------------------------------------
    # Section 1: Annual Summary Metrics
    # ---------------------------------------------------------------------
    st.subheader(texts['tab1']["annual_summary_metrics"])
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{texts['tab1']['annual_energy']}:** {ann_results['annual_energy']:.2f} kWh")
        st.write(f"**{texts['tab1']['annual_revenue']}:** {format_currency(ann_results['annual_revenue'], local_exchange_rate, currency_symbol)}")
                
        st.markdown(
            f"""
            <div style="font-size:16px; margin-bottom: 1em;">
                <strong>{texts['tab1']['annual_operating_cost']}:</strong> {format_currency(ann_results['annual_operating_cost'], local_exchange_rate, currency_symbol)}
                <span class="tooltip">?
                <span class="tooltiptext">
                    <strong>{texts['tab1']['operating_cost_tooltip_title']}</strong>
                    <p>{texts['tab1']['operating_cost_tooltip']}</p>
                </span>
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:            
        st.write(f"**{texts['tab1']['effective_cost_per_kwh']}**: {format_currency(ann_results['effective_cost_per_kwh'], local_exchange_rate, currency_symbol)}")
        st.write(f"**{texts['tab1']['annual_capital_cost']}**: {format_currency(ann_results['annual_capital_cost'], local_exchange_rate, currency_symbol)}")
        st.write(f"**{texts['tab1']['net_annual_profit']}**: {format_currency(ann_results['net_profit'], local_exchange_rate, currency_symbol)}")
        
    # ---------------------------------------------------------------------
    # Section 2: Investment & Cash Flow Overview
    # ---------------------------------------------------------------------
    st.subheader("Investment & Cash Flow Overview")
    # Compute individual component costs
    num_stations = params.get("num_stations", 1)
    station_cost = params.get("station_cost", 7000) * num_stations
    inverter_cost = (3000 if params["use_battery"] else 2000) * num_stations
    battery_cost = (params["battery_pack_price"] * params["number_of_battery_packs"] * num_stations) if params["use_battery"] else 0
    solar_cost = (params["solar_capacity"] / 10) * 1000
    install_cost = (params["solar_capacity"] / 10) * 1000
    total_capital_cost = station_cost + inverter_cost + battery_cost + solar_cost + install_cost

    st.write(f"**Total Initial Capital Cost:** ${total_capital_cost:.2f}")
    
    annual_cash_flow = ann_results["annual_revenue"] - ann_results["annual_operating_cost"]
    st.write(f"**Annual Cash Flow (Revenue - Operating Cost):** ${annual_cash_flow:.2f}")
    
    # ---------------------------------------------------------------------
    # Section 3: Payback Analysis
    # ---------------------------------------------------------------------
    st.subheader("Payback Analysis")
    if annual_cash_flow <= 0:
        payback_years = float('inf')
        st.write("**Payback Period:** Not achievable (annual cash flow is non-positive)")
    else:
        years = 0
        cumulative = 0.0
        inflation_rate = 0.05
        while cumulative < total_capital_cost:
            years += 1
            cumulative += annual_cash_flow * ((1 + inflation_rate) ** (years - 1))
        payback_years = years
        st.write(f"**Minimum Payback Period:** {payback_years} years (with 5% annual inflation)")
    
    # ---------------------------------------------------------------------
    # Section 4: Component Contribution Analysis (Waterfall Chart)
    # ---------------------------------------------------------------------
    st.subheader("Component Contribution Analysis")
    # Compute effective cost for Grid Only scenario (baseline)
    grid_only = simulate_grid_only(params)
    grid_ann = annualize_results(grid_only, params)
    baseline_cost = grid_ann["effective_cost_per_kwh"]

    # Compute effective cost for Solar Only scenario
    solar_only = simulate_solar_system(params,False)
    solar_ann = annualize_results(solar_only, params)
    effective_cost_solar = solar_ann["effective_cost_per_kwh"]

    # Compute effective cost for Solar + Storage scenario (if battery is used)
    if params["use_battery"]:
        storage = simulate_solar_system(params, True)
        storage_ann = annualize_results(storage, params)
        effective_cost_storage = storage_ann["effective_cost_per_kwh"]
    else:
        effective_cost_storage = effective_cost_solar  # no change if battery isn't used

    # Calculate savings contributions
    solar_savings = baseline_cost - effective_cost_solar
    battery_savings = effective_cost_solar - effective_cost_storage



    # Build data for the waterfall chart.
    # The waterfall chart will show:
    # 1. The starting effective cost (baseline)
    # 2. The effective cost after adding solar: baseline minus solar savings.
    # 3. The effective cost after adding battery: (baseline minus solar savings) minus battery savings.
    values = [baseline_cost, effective_cost_solar, effective_cost_storage]
    components = ['Grid Only', 'Solar Only', 'Solar + Storage']

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(components, values, color=['gray', 'orange', 'blue'])
    ax.set_ylabel('Effective Cost ($/kWh)')
    ax.set_title('Waterfall Analysis: Component Contributions')

    # Optionally, annotate the bars with their values
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.4f}', 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
                    
    st.pyplot(fig)

    
    st.info(
        "Overview Explanation: The annual summary section shows energy production, revenue, operating and capital costs, and net profit. "
        "The investment and cash flow overview displays the total initial capital cost alongside annual cash flow, while the payback analysis "
        "calculates the period required to recoup the initial investment. Finally, the component contribution analysis (waterfall chart) "
        "visually illustrates the impact of solar and battery investments on lowering the effective cost per kWh."
    )


import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils import simulate_ev_station, annualize_results, format_currency, simulate_solar_only, simulate_grid_only, simulate_solar_storage, compute_infrastructure_cost
from localization import UI_TEXTS
import numpy as np

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the tooltip CSS once at the start of your app.
local_css("styles.css")

def render_tab1(params: dict, language: str, local_exchange_rate: float, currency_symbol: str):
    """Render the Main Report (Tab 1) using one-day simulation results aggregated to annual values."""
    texts = UI_TEXTS[language]
    st.header(texts["tabs"]["main_report"])
    
    # Ensure that we simulate one day by overriding any simulation_days setting.
    @st.cache_data(show_spinner=False)
    def run_simulation(params: dict):
        p = params.copy()
        p["simulation_days"] = 1  # Force one-day simulation
        sim_results = simulate_ev_station(p, seed=42)
        ann_results = annualize_results(sim_results, p)
        return sim_results, ann_results

    sim_results, ann_results = run_simulation(params)
        
    # ---------------------------------------------------------------------
    # Section 1: Annual Summary Metrics
    # ---------------------------------------------------------------------
    st.subheader(texts['tab1']["annual_summary_metrics"])
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{texts['tab1']['annual_energy']}:** {ann_results['annual_energy']:.2f} kWh")
        st.write(f"**{texts['tab1']['annual_revenue']}:** {format_currency(ann_results['annual_revenue'], local_exchange_rate, currency_symbol)}")
        tooltip_html = f"""
            <div style="font-size:16px; margin-bottom: 1em;">
            <strong>{texts['tab1']['annual_operating_cost']}:</strong> {format_currency(ann_results['annual_operating_cost'], local_exchange_rate, currency_symbol)}
            <span class="tooltip">?
                <span class="tooltiptext">
                <strong>{texts['tab1']['operating_cost_tooltip_title']}</strong>
                <p>
                {texts['tab1']['operating_cost_tooltip']}
                </span>
            </span>
            </div>
            """
        st.html(tooltip_html)
    with col2:            
        st.write(f"**{texts['tab1']['effective_cost_per_kwh']}**: {format_currency(ann_results['effective_cost_per_kwh'], local_exchange_rate, currency_symbol)}")
        st.write(f"**{texts['tab1']['annual_capital_cost']}**: {format_currency(ann_results['annual_capital_cost'], local_exchange_rate, currency_symbol)}")
        st.write(f"**{texts['tab1']['net_annual_profit']}**: {format_currency(ann_results['net_profit'], local_exchange_rate, currency_symbol)}")
        
    # ---------------------------------------------------------------------
    # Section 2: Investment & Cash Flow Overview
    # ---------------------------------------------------------------------
    st.subheader(texts['tab1']["investment_cash_flow_overview"])
    num_stations = params.get("num_stations", 1)

    total_capital_cost = compute_infrastructure_cost(params, use_roi_constants=False)

    st.write(f"**{texts['tab1']['total_initial_capital_cost']}**: {format_currency(total_capital_cost, local_exchange_rate, currency_symbol)}")
    
    annual_cash_flow = ann_results["annual_revenue"] - ann_results["annual_operating_cost"]
    st.write(f"**{texts['tab1']['annual_cash_flow']}**: {format_currency(annual_cash_flow, local_exchange_rate, currency_symbol)}")
    
    # ---------------------------------------------------------------------
    # Section 3: Payback Analysis
    # ---------------------------------------------------------------------
    st.subheader(texts['tab1']["payback_analysis"])
    if annual_cash_flow <= 0:
        st.write(f"**{texts['tab1']['payback_period']}**: {texts['tab1']['payback_not_achievable']}")
    else:
        cumulative = 0.0
        inflation_rate = 0.05
        years = 0
        previous_cumulative = 0.0

        # Loop until we exceed total_capital_cost, tracking the cumulative cash flow.
        while cumulative < total_capital_cost:
            previous_cumulative = cumulative
            current_year_cash_flow = annual_cash_flow * ((1 + inflation_rate) ** years)
            cumulative += current_year_cash_flow
            years += 1

        # Compute fractional year for precise payback.
        extra_needed = total_capital_cost - previous_cumulative
        fraction = extra_needed / current_year_cash_flow
        payback_years = (years - 1) + fraction

        st.write(f"**{texts['tab1']['minimum_payback_period']}**: {payback_years:.1f} {texts['tab1']['years_with_inflation']}")

    # ---------------------------------------------------------------------
    # Section 4: Component Contribution Analysis (Waterfall Chart)
    # ---------------------------------------------------------------------
    st.subheader(texts['tab1']["component_contribution_analysis"])
    grid_params = params.copy()
    grid_params["solar_capacity"] = 0 
    grid_params["use_battery"] = False


    # Baseline: Grid Only scenario
    grid_only = simulate_grid_only(grid_params)
    grid_ann = annualize_results(grid_only, grid_params)
    baseline_cost = grid_ann["effective_cost_per_kwh"]

    # Solar Only scenario
    solar_only = simulate_solar_only(params)
    solar_ann = annualize_results(solar_only, params)
    effective_cost_solar = solar_ann["effective_cost_per_kwh"]

    # Solar + Storage scenario:
    if params["use_battery"]:
        storage = simulate_solar_storage(params)
        storage_ann = annualize_results(storage, params)
        effective_cost_storage = storage_ann["effective_cost_per_kwh"]
    else:
        num_stations = params.get("num_stations", 1)
        if "battery_pack_price" in params and "number_of_battery_packs" in params:
            base_battery_cost = params["battery_pack_price"] * params["number_of_battery_packs"] * num_stations
        else:
            base_battery_cost = 5000 * num_stations  # fallback benchmark value
        installation_cost = params.get("installation_cost", 500) * num_stations
        hypothetical_battery_cost = base_battery_cost + installation_cost
        additional_annual_battery_cost = hypothetical_battery_cost / params["battery_lifetime"]
        operational_savings = 0
        if "battery_operational_savings_fraction" in params:
            operational_savings = solar_ann["annual_operating_cost"] * params["battery_operational_savings_fraction"]
        adjusted_operating_cost = solar_ann["annual_operating_cost"] - operational_savings
        hypothetical_annual_capital_cost = solar_ann["annual_capital_cost"] + additional_annual_battery_cost
        effective_cost_storage = (adjusted_operating_cost + hypothetical_annual_capital_cost) / solar_ann["annual_energy"]

    values = [baseline_cost, effective_cost_solar, effective_cost_storage]
    components = [texts['tab1']['grid_only'], texts['tab1']['grid_and_solar'], texts['tab1']['grid_and_solar_and_battery']]

    import matplotlib.ticker as mticker
    def currency_formatter(x, pos):
        if language == "VI":
            return f"{currency_symbol}{(x * local_exchange_rate):,.1f}"
        else:
            return f"{currency_symbol}{(x * local_exchange_rate):,.4f}"

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_colors = ['#66c2a5', '#fc8d62', '#8da0cb']
    bars = ax.bar(components, values, color=bar_colors, edgecolor='black', linewidth=0.5)
    ax.set_ylabel(texts['tab1']['effective_cost_per_kwh'], fontsize=12, fontweight='bold')
    ax.set_title(texts['tab1']['waterfall_chart_title'], fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(currency_formatter))
    ax.yaxis.set_tick_params(labelsize=10)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    for bar in bars:
        height = bar.get_height()
        if language == "VI":
            localized_value = f"{currency_symbol}{(height * local_exchange_rate):,.1f}/kWh"
        else:
            localized_value = f"{currency_symbol}{(height * local_exchange_rate):,.4f}/kWh"
        ax.annotate(localized_value,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)

    st.markdown(r"""
        **Hypothetical Battery Cost**

        If `use_battery` is false, we assume a default battery investment value of \$5000 per pack/charging station. 
        This means that the added battery cost is estimated to be roughly double the investment cost for the solar system 
        (which includes `solar_panel_cost`, `inverter_cost`, and `installation_cost`).

        Annualized over a battery lifetime \(L\):

        $$
        \text{Annualized Battery Cost} = \frac{\text{Hypothetical Battery Cost}}{L}
        $$

        This adjustment allows for a fair comparison of effective cost per kWh across different setups.
        """)

    st.info(texts['tab1']['overview_explanation'])

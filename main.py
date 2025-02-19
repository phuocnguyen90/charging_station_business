import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Import helper functions from utils.py
from utils import (
    simulate_ev_station, run_monte_carlo, 
    simulate_grid_only, simulate_solar_only, simulate_solar_with_storage,
    annualize_results, compute_roi, solar_irradiance, get_electricity_rate, solar_production
)

# Include the tooltip CSS (only needs to be added once per page)
tooltip_css = """
<style>
.tooltip {
  display: inline-block;
  position: relative;
  cursor: help;
  border: 1px solid #ccc;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  color: #555;
  margin-left: 6px;
  background-color: #f0f0f0;
}
.tooltip .tooltiptext {
  visibility: hidden;
  max-width: 60vw !important;  /* Force 30% of viewport width */
  min-width: 350px !important; /* Ensure a minimum width */
  white-space: normal;
  background-color: #f9f9f9;
  color: #333;
  text-align: left;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 10px;
  position: absolute;
  z-index: 1;
  top: 100%;
  left: 100%;
  margin: 0;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 13px;
  line-height: 1.4;
  display: block !important;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}
</style>
"""
st.markdown(tooltip_css, unsafe_allow_html=True)

def main_ui():
    st.title("EV Charging Station Cost, Solar & ROI Simulation")
    st.markdown("""
    This tool simulates the cost-effectiveness of an EV charging station under various configurations.
    
    **Features include:**
    - Detailed simulation with solar production, battery integration, and grid tariffs.
    - A Solar Report for Buon Ma Thuot, Vietnam.
    - ROI analysis across different design configurations.
    - Explanations of the underlying math and formulas via hover-help.
    """)

    # ---------------------------
    # Consolidated Sidebar Inputs
    # ---------------------------
    st.sidebar.header("Simulation Settings")
    simulation_days = st.sidebar.number_input(
        "Simulation Duration (Days) ", value=30,
        help="The number of days to simulate (affects depreciation and energy totals)."
    )
    charging_sessions_per_day = st.sidebar.slider(
        "Average Charging Sessions per Day ", 0, 48, 12,
        help="Each session delivers (Charging Power x 0.5 hr) kWh."
    )
    num_stations = st.sidebar.number_input(
        "Number of charging station:", 1, 1000,1,
        help="Number of charging stations or ports."
    )
    charging_station_power = st.sidebar.number_input(
        "Charging Station Power (kW) ", value=30,
        help="Rated power of each charging station."
    )
    
    charging_price = st.sidebar.number_input(
        "Charging Price ($/kWh) ", value=0.17,
        help="Price charged to EV customers per kWh."
    )

    use_battery = st.sidebar.checkbox(
        "Use Battery ", value=True,
        help="Enable battery integration for load management."
    )

    st.sidebar.header("Solar Settings")
    solar_capacity = st.sidebar.number_input(
        "Solar Panel Capacity (kW) ", value=20,
        help="Installed capacity of the solar panels."
    )
    solar_randomness = st.sidebar.slider(
        "Solar Variability (Fraction) ", 0.0, 0.5, 0.1, step=0.01,
        help="Represents variability in solar output (e.g., due to clouds)."
    )

    if use_battery:
        st.sidebar.subheader("Battery Pack Configuration")
        battery_pack_Ah = st.sidebar.number_input(
            "Battery Pack Capacity (Ah) ", value=100,
            help="Capacity of one battery pack in Ampere-hours."
        )
        battery_pack_voltage = st.sidebar.number_input(
            "Battery Pack Voltage (V) ", value=51.2,
            help="Voltage of one battery pack."
        )
        battery_pack_price = st.sidebar.number_input(
            "Battery Pack Price ($) ", value=1000,
            help="Cost per battery pack."
        )
        number_of_battery_packs = st.sidebar.slider(
            "Number of Battery Packs Installed ", 1, 20, 4,
            help="Total number of battery packs installed."
        )
        initial_soc_fraction = st.sidebar.slider(
            "Initial Battery SoC (Fraction) ", 0.0, 1.0, 0.5,
            help="Initial state-of-charge as a fraction of total battery capacity."
        )
        battery_max_charge_power = st.sidebar.slider(
            "Battery Max Charge/Discharge Rate (C) ", 0.0, 1.0, 0.5,
            help="Maximum charging rate as a fraction of battery capacity (e.g., 0.5 means the battery can be charged/discharged at 50% of its capacity per hour)."
        )


    else:
        battery_pack_Ah = battery_pack_voltage = battery_pack_price = number_of_battery_packs = 0
        initial_soc_fraction = 0.0

    st.sidebar.header("Battery & Inverter Performance")
    battery_efficiency = st.sidebar.slider(
        "Battery Round-Trip Efficiency ", 0.5, 1.0, 0.9, step=0.01,
        help="Efficiency during a full charge/discharge cycle."
    )
    inverter_efficiency = st.sidebar.slider(
        "Inverter Efficiency ", 0.5, 1.0, 0.95, step=0.01,
        help="Efficiency of converting DC (solar) to AC when charging the battery."
    )
    battery_degradation_cost = st.sidebar.number_input(
        "Battery Degradation Cost ($/kWh discharged) ", value=0.05,
        help="Cost associated with battery wear per kWh discharged."
    )
    battery_usage_threshold = st.sidebar.number_input(
        "Grid Price Threshold for Battery Use ($/kWh) ", value=0.17,
        help="If the grid tariff exceeds this value, battery discharge is used."
    )

    st.sidebar.header("Capital Costs & Lifetimes")
    initial_costs = {
        "charging_station": st.sidebar.number_input(
            "Charging Station Cost ($) ", value=7000,
            help="Capital cost for the charging station."
        ),
        "transformer": st.sidebar.number_input(
            "Transformer Cost ($) ", value=1000,
            help="Cost of any required transformer."
        ),
        "solar_panel": st.sidebar.number_input(
            "Solar Panel Cost ($) ", value=2000,
            help="Cost for solar panel installation."
        ),
        "inverter": st.sidebar.number_input(
            "Inverter Cost ($) ", value=3000,
            help="Cost of the inverter (use lower cost if battery not used)."
        ),
        "installation": st.sidebar.number_input(
            "Installation & Other Costs ($) ", value=1000,
            help="Other installation-related costs."
        )
    }
    component_lifetime_years = {
        "charging_station": st.sidebar.number_input(
            "Charging Station Lifetime (Years) ", value=10,
            help="Expected lifetime of the charging station."
        ),
        "transformer": st.sidebar.number_input(
            "Transformer Lifetime (Years) ", value=15,
            help="Expected lifetime of the transformer."
        ),
        "solar_panel": st.sidebar.number_input(
            "Solar Panel Lifetime (Years) ", value=25,
            help="Expected lifetime of the solar panels."
        ),
        "battery": st.sidebar.number_input(
            "Battery Lifetime (Years) ", value=10,
            help="Expected lifetime of the battery system."
        ),
        "inverter": st.sidebar.number_input(
            "Inverter Lifetime (Years) ", value=10,
            help="Expected lifetime of the inverter."
        ),
        "installation": st.sidebar.number_input(
            "Installation Lifetime (Years) ", value=10,
            help="Lifetime over which installation costs are amortized."
        )
    }
    st.sidebar.header("Monte Carlo Simulation")
    monte_iterations = st.sidebar.number_input(
        "Monte Carlo Iterations ", 1, 200, 50,
        help="Number of iterations for Monte Carlo simulation."
    )
    if not use_battery:
        battery_pack_Ah = 0
        battery_pack_voltage = 0
        battery_pack_price = 0
        number_of_battery_packs = 0
        initial_soc_fraction = 0.0
        battery_max_charge_power=0.0

    # Consolidate all inputs into a single dictionary used across all tabs.
    params = {
        "simulation_days": simulation_days,
        "charging_sessions_per_day": charging_sessions_per_day,
        "charging_station_power": charging_station_power,
        "daily_ev_demand": charging_station_power*charging_sessions_per_day/2,
        "num_stations":num_stations,
        "charging_price": charging_price,
        "solar_capacity": solar_capacity,
        "solar_randomness": solar_randomness,
        "use_battery": use_battery,
        "battery_pack_Ah": battery_pack_Ah,
        "battery_pack_voltage": battery_pack_voltage,
        "battery_pack_price": battery_pack_price,
        "battery_cost": battery_pack_price*number_of_battery_packs,
        "battery_max_charge_power": battery_max_charge_power,
        "number_of_battery_packs": number_of_battery_packs,
        "battery_capacity": battery_pack_Ah*number_of_battery_packs,
        "battery_initial_soc_fraction": initial_soc_fraction,
        "battery_efficiency": battery_efficiency,
        "inverter_efficiency": inverter_efficiency,
        "battery_degradation_cost": battery_degradation_cost,
        "battery_usage_threshold": battery_usage_threshold,
        "initial_costs": initial_costs,
        "component_lifetime_years": component_lifetime_years,
        "capital_lifetime_years": st.sidebar.number_input(
            "Capital Investment Lifetime (Years) ", value=25,
            help="Used for amortizing capital costs."
        ),
        "solar_cost_per_kw": st.sidebar.number_input(
            "Solar Cost ($/kW) ", value=2000.0,
            help="Cost per kW of solar capacity."
        )
    }

    # -------------------------
    # Create Tabs (all use the same 'params')
    # -------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["Main Report", "Solar Report", "ROI Analysis", "Charging Cost"])
    
    ### TAB 1: Main Report (Overview)
    with tab1:
        st.header("Overview – Annual Expected Returns, Costs, and Payback Period")
        
        # Run simulation for the defined period (e.g., 30 days)
        sim_results = simulate_ev_station(params, seed=42)
        ann_results = annualize_results(sim_results, params)
        
        # ---------------------------------------------------------------------
        # Section 1: Annual Summary Metrics
        # ---------------------------------------------------------------------
        st.subheader("Annual Summary Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Annual Energy Delivered:** {ann_results['annual_energy']:.2f} kWh")
            st.write(f"**Annual Revenue:** ${ann_results['annual_revenue']:.2f}")
            
            st.markdown(
                f"""
                <div style="font-size:16px; margin-bottom: 1em;">
                <strong>Annual Operating Cost:</strong> ${ann_results['annual_operating_cost']:.2f}
                <span class="tooltip">?
                    <span class="tooltiptext">
                    <strong>Calculation Details:</strong>
                    <p>
                        The Annual Operating Cost is calculated by annualizing the total operational cost incurred during the simulation period. This cost includes:
                    </p>
                    <ul>
                        <li>Grid Import Charges (based on time-of-use tariffs)</li>
                        <li>Battery Degradation Costs (if applicable)</li>
                    </ul>
                    <p>
                        The cost is scaled to an annual value using the formula:
                    </p>
                    <code>Total Operational Cost × (365 / Simulation Days)</code>
                    </span>
                </span>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col2:
            st.write(f"**Effective Cost per kWh:** ${ann_results['effective_cost_per_kwh']:.3f}")
            st.write(f"**Annual Capital Cost:** ${ann_results['annual_capital_cost']:.2f}")
            st.write(f"**Net Annual Profit:** ${ann_results['net_profit']:.2f}")
        
        # ---------------------------------------------------------------------
        # Section 2: Investment & Cash Flow Overview
        # ---------------------------------------------------------------------
        st.subheader("Investment & Cash Flow Overview")
        # Compute individual component costs
        num_stations = params.get("num_stations", 1)
        station_cost = params["initial_costs"].get("charging_station", 7000) * num_stations
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
        solar_only = simulate_solar_only(params)
        solar_ann = annualize_results(solar_only, params)
        effective_cost_solar = solar_ann["effective_cost_per_kwh"]

        # Compute effective cost for Solar + Storage scenario (if battery is used)
        if params["use_battery"]:
            storage = simulate_solar_with_storage(params)
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


    ### TAB 2: Solar Report
    with tab2:
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

    ### TAB 3: ROI Analysis
    with tab3:
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

    
    ### TAB 4: Charging Cost

    with tab4:
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
            "Solar + Storage": simulate_solar_with_storage(params)
        }
        results = {}
        for key, sim_res in scenarios.items():
            ann = annualize_results(sim_res, params)
            # Merge the annualized values with the simulation results.
            results[key] = {**sim_res, **ann}
        
        # Compute the total initial capital cost (using the same formula used elsewhere)
        num_stations = params.get("num_stations", 1)  # default to 1 if not provided
        station_cost = 7000 * num_stations
        inverter_cost = (3000 if params["use_battery"] else 2000) * num_stations
        battery_cost = (params["battery_pack_price"] * params["number_of_battery_packs"] * num_stations) if params["use_battery"] else 0
        solar_cost = (params["solar_capacity"] / 10) * 1000
        install_cost = (params["solar_capacity"] / 10) * 1000
        total_capital_cost = station_cost + inverter_cost + battery_cost + solar_cost + install_cost

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
        if "Solar + Storage" in results:
            df_hourly = pd.DataFrame(results["Solar + Storage"]["hourly_details"])
            st.dataframe(df_hourly)
        
        st.subheader("Visualizations")
        # Visualization 1: Line Chart for Cost per Hour with a Second Y-Axis Column Chart for Effective Cost ($/kWh)
        if "Solar + Storage" in results:
            df_hourly = pd.DataFrame(results["Solar + Storage"]["hourly_details"])
            
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

    
if __name__ == '__main__':
    main_ui()

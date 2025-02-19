import streamlit as st
import numpy as np
import pandas as pd

# ----------------------------------------------
# Helper Functions
# ----------------------------------------------

def get_grid_rate(hour, day_of_week=1):
    """
    Returns an approximate grid tariff ($/kWh) for a given hour.
    Using a simplified hourly version of the tariff schedule (assumed for a weekday, e.g. Tuesday):
      - Hours 0-3: off-peak = $0.06
      - Hour 4-8: normal = $0.108
      - Hour 9: transitional = $0.148  (approximation around 09:30)
      - Hour 10: peak = $0.188
      - Hour 11: transitional = $0.148  (around 11:30)
      - Hours 12-16: normal = $0.108
      - Hours 17-19: peak = $0.188
      - Hours 20-21: normal = $0.108
      - Hours 22-23: off-peak = $0.06
    """
    rates = [0.06, 0.06, 0.06, 0.06, 
             0.108, 0.108, 0.108, 0.108, 0.108,
             0.148, 0.188, 0.148,
             0.108, 0.108, 0.108, 0.108, 0.108,
             0.188, 0.188, 0.188,
             0.108, 0.108, 0.06, 0.06]
    return rates[hour]

def solar_production(hour, solar_capacity):
    """
    A simplified solar production model.
    For hours between 6 and 18, production is given by:
      production (kWh) = solar_capacity (kW) * sin(pi*(hour-6)/12)
    Otherwise, production is zero.
    """
    if 6 <= hour < 18:
        return solar_capacity * np.sin(np.pi * (hour - 6) / 12)
    else:
        return 0.0

def usage_profile():
    """
    Returns a list of 24 values (one per hour) that sum to 1,
    representing the fraction of daily EV demand in each hour.
    
    (Example profile: low demand during night, moderate in morning,
     highest in early evening, then low at night.)
    """
    profile = [0.02]*6   # Hours 0-5: 0.02 each  -> total 0.12
    profile += [0.06]*4  # Hours 6-9: 0.06 each  -> total 0.24
    profile += [0.03]*6  # Hours 10-15: 0.03 each -> total 0.18
    profile += [0.08]*5  # Hours 16-20: 0.08 each -> total 0.40
    profile += [0.02]*3  # Hours 21-23: 0.02 each -> total 0.06
    return profile  # Sums to 1.0

# ----------------------------------------------
# Simulation Functions for Each Scenario
# ----------------------------------------------

def simulate_grid_only(params):
    """
    In the Grid Only scenario, all EV charging energy is drawn from the grid.
    """
    daily_ev_demand = params["daily_ev_demand"]  # kWh per day
    profile = usage_profile()
    
    total_grid_cost = 0.0
    total_energy = 0.0
    hourly_details = []
    for hour in range(24):
        # EV demand for this hour:
        ev_demand = daily_ev_demand * profile[hour]
        grid_rate = get_grid_rate(hour)
        cost = ev_demand * grid_rate
        total_grid_cost += cost
        total_energy += ev_demand
        hourly_details.append({
            "hour": hour,
            "ev_demand": ev_demand,
            "grid_rate": grid_rate,
            "grid_energy": ev_demand,
            "cost": cost,
            "solar_used": 0.0,
            "battery_discharge": 0.0,
            "grid_used": ev_demand
        })
        
    # No additional capital cost beyond the basic charging station (which we ignore here)
    capital_cost = 7000.0
    
    results = {
        "scenario": "Grid Only",
        "daily_energy": total_energy,
        "daily_operational_cost": total_grid_cost,
        "capital_cost": capital_cost,
        "hourly_details": hourly_details
    }
    return results

def simulate_solar_only(params):
    """
    In the Solar Only scenario, a solar array is installed.
    EV charging uses solar energy when available; any shortfall is met by the grid.
    Excess solar (if produced) is wasted.
    """
    daily_ev_demand = params["daily_ev_demand"]
    solar_capacity = params["solar_capacity"]  # kW
    profile = usage_profile()
    
    total_grid_cost = 0.0
    total_energy = 0.0
    total_solar_used = 0.0
    hourly_details = []
    for hour in range(24):
        ev_demand = daily_ev_demand * profile[hour]
        grid_rate = get_grid_rate(hour)
        solar_prod = solar_production(hour, solar_capacity)
        # Use solar to cover demand as much as possible:
        solar_used = min(ev_demand, solar_prod)
        grid_needed = max(ev_demand - solar_prod, 0.0)
        cost = grid_needed * grid_rate
        total_grid_cost += cost
        total_energy += ev_demand
        total_solar_used += solar_used
        hourly_details.append({
            "hour": hour,
            "ev_demand": ev_demand,
            "grid_rate": grid_rate,
            "solar_production": solar_prod,
            "solar_used": solar_used,
            "grid_used": grid_needed,
            "cost": cost,
            "battery_discharge": 0.0
        })
    
    # Capital cost for solar:
    capital_cost = params["solar_cost_per_kw"] * solar_capacity
    
    results = {
        "scenario": "Solar Only",
        "daily_energy": total_energy,
        "daily_operational_cost": total_grid_cost,
        "capital_cost": capital_cost,
        "total_solar_used": total_solar_used,
        "hourly_details": hourly_details
    }
    return results

def simulate_solar_with_storage(params):
    """
    In the Solar + Storage scenario, a battery is added so that excess solar energy is stored
    and later discharged to serve EV demand.
    
    Battery simulation (hourly):
      - Battery parameters: capacity (kWh), max charge power (kW), max discharge power (kW)
      - Battery state-of-charge (SoC) is updated each hour.
      - In each hour:
          * EV demand is first met by direct solar.
          * If excess solar is available, battery is charged (up to available capacity and max charge limit).
          * If EV demand is not fully met by direct solar, battery discharges (up to its SoC and max discharge limit).
          * Remaining demand is met by the grid.
    """
    daily_ev_demand = params["daily_ev_demand"]
    solar_capacity = params["solar_capacity"]
    battery_capacity = params["battery_capacity"]  # kWh
    max_charge_power = params["battery_max_charge_power"]  # kW
    max_discharge_power = params["battery_max_discharge_power"]  # kW
    profile = usage_profile()
    
    # Initialize battery state-of-charge (assume 50% at start)
    soc = 0.5 * battery_capacity
    battery_history = [soc]
    
    total_grid_cost = 0.0
    total_energy = 0.0
    total_solar_used = 0.0
    total_battery_discharge = 0.0
    hourly_details = []
    
    for hour in range(24):
        ev_demand = daily_ev_demand * profile[hour]
        grid_rate = get_grid_rate(hour)
        solar_prod = solar_production(hour, solar_capacity)
        
        # Direct solar usage for EV charging:
        direct_solar = min(ev_demand, solar_prod)
        remaining_demand = ev_demand - direct_solar
        excess_solar = max(solar_prod - ev_demand, 0.0)
        
        # Use excess solar to charge the battery:
        charge_possible = min(excess_solar, max_charge_power, battery_capacity - soc)
        soc += charge_possible
        
        # If demand remains, try to discharge the battery:
        discharge_possible = min(remaining_demand, soc, max_discharge_power)
        soc -= discharge_possible
        remaining_demand -= discharge_possible
        
        grid_needed = remaining_demand
        cost = grid_needed * grid_rate
        
        total_grid_cost += cost
        total_energy += ev_demand
        total_solar_used += direct_solar
        total_battery_discharge += discharge_possible
        
        hourly_details.append({
            "hour": hour,
            "ev_demand": ev_demand,
            "grid_rate": grid_rate,
            "solar_production": solar_prod,
            "direct_solar": direct_solar,
            "excess_solar": excess_solar,
            "battery_charged": charge_possible,
            "battery_discharged": discharge_possible,
            "grid_used": grid_needed,
            "cost": cost,
            "soc": soc
        })
        battery_history.append(soc)
    
    # Capital cost for solar + battery:
    capital_cost = params["solar_cost_per_kw"] * solar_capacity + params["battery_cost"]
    
    results = {
        "scenario": "Solar + Storage",
        "daily_energy": total_energy,
        "daily_operational_cost": total_grid_cost,
        "capital_cost": capital_cost,
        "total_solar_used": total_solar_used,
        "total_battery_discharged": total_battery_discharge,
        "hourly_details": hourly_details,
        "battery_history": battery_history
    }
    return results

# ----------------------------------------------
# Annualization and ROI Calculation
# ----------------------------------------------

def annualize_results(daily_results, params):
    """
    Given daily simulation results and parameters, compute annualized values and effective cost per kWh.
    Also compute annual revenue and ROI.
    
    For capital cost, we amortize using the provided lifetime (years) for the solar or battery system.
    (For grid-only, capital cost is assumed 0.)
    """
    annual_energy = daily_results["daily_energy"] * 365  # kWh per year
    annual_operating_cost = daily_results["daily_operational_cost"] * 365  # $/year
    
    # Capital cost amortization:
    lifetime = params["capital_lifetime_years"]  # assumed lifetime for solar/battery investment
    annual_capital_cost = daily_results["capital_cost"] / lifetime if lifetime > 0 else 0.0
    
    effective_cost_per_kwh = (annual_operating_cost + annual_capital_cost) / annual_energy if annual_energy > 0 else np.nan
    
    # Annual revenue (assume EV charging price in $/kWh):
    annual_revenue = annual_energy * params["charging_price"]
    
    # Net profit = annual revenue - (annual operating cost + annual capital cost)
    net_profit = annual_revenue - (annual_operating_cost + annual_capital_cost)
    
    # ROI per $ invested (only applies if there is a capital cost):
    roi = net_profit / daily_results["capital_cost"] if daily_results["capital_cost"] > 0 else np.nan
    
    return {
        "annual_energy": annual_energy,
        "annual_operating_cost": annual_operating_cost,
        "annual_capital_cost": annual_capital_cost,
        "effective_cost_per_kwh": effective_cost_per_kwh,
        "annual_revenue": annual_revenue,
        "net_profit": net_profit,
        "ROI": roi
    }

# ----------------------------------------------
# Streamlit Dashboard
# ----------------------------------------------

def main():
    st.title("Charging Cost & ROI Comparison Simulation")
    st.markdown("""
    This simulation compares the effective charging cost (per kWh) and annual ROI for an EV charging station under three scenarios:
    
    1. **Grid Only:** All energy is purchased from the grid.
    2. **Solar Only:** A solar array is installed. EV demand is met by solar when available; any shortfall is purchased from the grid.
    3. **Solar + Storage:** In addition to solar, a battery is installed to store excess solar energy for later use.
    
    The simulation uses a daily EV energy demand distributed over 24 hours (via a fixed usage profile), a simplified solar production model, and a grid tariff schedule.
    Capital costs for solar and battery investments are amortized over an assumed lifetime to estimate the effective cost per kWh and ROI.
    """)
    
    st.sidebar.header("General Inputs")
    daily_ev_demand = st.sidebar.number_input("Daily EV Energy Demand (kWh/day)", value=100.0)
    charging_price = st.sidebar.number_input("Charging Price ($/kWh charged to EVs)", value=0.17)
    capital_lifetime_years = st.sidebar.number_input("Capital Investment Lifetime (years)", value=25)
    
    st.sidebar.header("Grid Tariff")
    st.sidebar.write("Using an approximate hourly tariff schedule for a weekday (see code).")
    
    st.sidebar.header("Solar System")
    solar_capacity = st.sidebar.number_input("Solar Array Capacity (kW)", value=20.0)
    solar_cost_per_kw = st.sidebar.number_input("Solar Cost ($/kW)", value=300.0)
    
    st.sidebar.header("Battery System (for Solar + Storage)")
    battery_capacity = st.sidebar.number_input("Battery Capacity (kWh)", value=20.0)
    battery_max_charge_power = st.sidebar.number_input("Max Battery Charge Power (kW)", value=10.0)
    battery_max_discharge_power = st.sidebar.number_input("Max Battery Discharge Power (kW)", value=16.0)
    battery_cost = st.sidebar.number_input("Battery System Cost ($ total)", value=5000.0)
    
    # Pack parameters into a dictionary:
    params = {
        "daily_ev_demand": daily_ev_demand,
        "charging_price": charging_price,
        "capital_lifetime_years": capital_lifetime_years,
        "solar_capacity": solar_capacity,
        "solar_cost_per_kw": solar_cost_per_kw,
        "battery_capacity": battery_capacity,
        "battery_max_charge_power": battery_max_charge_power,
        "battery_max_discharge_power": battery_max_discharge_power,
        "battery_cost": battery_cost,
    }
    
    st.header("Scenario Comparison")
    scenarios = {
        "Grid Only": simulate_grid_only(params),
        "Solar Only": simulate_solar_only(params),
        "Solar + Storage": simulate_solar_with_storage(params)
    }
    
    results = {}
    for key, sim_res in scenarios.items():
        ann = annualize_results(sim_res, params)
        results[key] = {**sim_res, **ann}
    
    # Display a summary table:
    summary = []
    for scenario, res in results.items():
        summary.append({
            "Scenario": scenario,
            "Daily Energy (kWh)": round(res["daily_energy"], 1),
            "Effective Cost ($/kWh)": round(res["effective_cost_per_kwh"], 3),
            "Annual Revenue ($)": round(res["annual_revenue"], 2),
            "Annual Operating Cost ($)": round(res["annual_operating_cost"], 2),
            "Annual Capital Cost ($)": round(res["annual_capital_cost"], 2),
            "Net Annual Profit ($)": round(res["net_profit"], 2),
            "ROI": round(res["ROI"] * 100, 1) if not np.isnan(res["ROI"]) else "N/A"
        })
    df_summary = pd.DataFrame(summary)
    st.dataframe(df_summary)
    
    st.markdown("""
    **Interpretation:**
    
    - *Effective Cost ($/kWh):* Annualized total cost (operating + capital) divided by annual energy delivered.
    - *ROI:* Annual net profit (annual revenue minus annual costs) divided by total capital investment (as a percentage).
      (For the Grid Only scenario, no capital is invested, so ROI is not applicable.)
    """)
    
    st.header("Detailed Hourly Data (for Solar + Storage)")
    if "Solar + Storage" in results:
        df_hourly = pd.DataFrame(results["Solar + Storage"]["hourly_details"])
        st.dataframe(df_hourly)

if __name__ == '__main__':
    main()

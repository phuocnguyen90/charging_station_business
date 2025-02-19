import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# --------------------------------------
# Helper Functions & Grid Pricing
# --------------------------------------

def get_electricity_rate(time_in_day, day_of_week):
    """
    Returns the grid electricity cost ($/kWh) for a given time of day and day of week.
    
    Schedule:
      - Mon–Sat:
          Off-peak: 22:00–04:00 → $0.06
          Normal:   04:00–09:30, 11:30–17:00, 20:00–22:00 → $0.108
          Peak:     09:30–11:30, 17:00–20:00 → $0.188
      - Sunday: All day normal ($0.108)
      
    Note: time_in_day is in hours (can be fractional, e.g. 9.5 means 09:30).
    """
    if day_of_week == 6:
        return 0.108
    if time_in_day < 4 or time_in_day >= 22:
        return 0.06
    if (9.5 <= time_in_day < 11.5) or (17 <= time_in_day < 20):
        return 0.188
    else:
        return 0.108

def solar_irradiance(time_in_day):
    """
    Simplified solar irradiance model using a sine curve between 6:00 and 18:00.
    Outside that window, irradiance is 0.
    """
    if 6 <= time_in_day <= 18:
        return np.sin(np.pi * (time_in_day - 6) / 12)
    else:
        return 0.0
    
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

# --------------------------------------
# EV Station Simulation (Half-hour Time Steps)
# --------------------------------------

def simulate_ev_station(params, seed=None):
    """
    Simulate one run of the EV charging station over a chosen number of days
    using half-hour time steps, returning both an hourly DataFrame and aggregate totals.
    """
    if seed is not None:
        np.random.seed(seed)
        
    dt = 0.5  # time step in hours
    total_steps = int(params["simulation_days"] * 24 / dt)
    
    # Basic parameters
    charging_station_power = params["charging_station_power"]  # kW
    charging_sessions_per_day = params["charging_sessions_per_day"]
    solar_capacity = params["solar_capacity"]  # kW
    battery_max_charge_power = params["battery_max_charge_power"]  # in C (fraction of capacity)
    
    # Battery parameters (if enabled)
    use_battery = params.get("use_battery", True)
    if use_battery:
        battery_pack_Ah = params["battery_pack_Ah"]
        battery_pack_voltage = params["battery_pack_voltage"]
        number_of_battery_packs = params["number_of_battery_packs"]
        battery_capacity = number_of_battery_packs * (battery_pack_Ah * battery_pack_voltage / 1000)  # kWh
        battery_initial_soc = params["battery_initial_soc_fraction"] * battery_capacity
    else:
        battery_capacity = 0.0
        battery_initial_soc = 0.0
    
    battery_eff = params["battery_efficiency"]
    inverter_eff = params["inverter_efficiency"]
    battery_deg_cost = params["battery_degradation_cost"]
    battery_usage_threshold = params["battery_usage_threshold"]
    charging_price = params["charging_price"]
    
    # Capital costs & depreciation
    initial_costs = params["initial_costs"].copy()
    if use_battery:
        initial_costs["battery"] = params["battery_pack_price"] * params["number_of_battery_packs"]
    else:
        initial_costs["battery"] = 0.0
    component_lifetime_years = params["component_lifetime_years"]
    sim_years = params["simulation_days"] / 365.0
    depreciation = {}
    for comp in initial_costs:
        lifetime = component_lifetime_years.get(comp, 10)
        depreciation[comp] = initial_costs[comp] * (sim_years / lifetime)
    total_depreciation = sum(depreciation.values())
    
    # Arrays to record per-time-step data
    time_arr = np.zeros(total_steps)
    battery_soc_arr = np.zeros(total_steps)
    grid_import_arr = np.zeros(total_steps)     # EV demand met by grid
    solar_used_arr = np.zeros(total_steps)      # solar used directly for EV
    battery_discharged_arr = np.zeros(total_steps)
    cost_grid_arr = np.zeros(total_steps)
    cost_battery_arr = np.zeros(total_steps)
    demand_arr = np.zeros(total_steps)
    revenue_arr = np.zeros(total_steps)
    solar_total_arr = np.zeros(total_steps)
    solar_to_battery_arr = np.zeros(total_steps)
    grid_to_battery_arr = np.zeros(total_steps)
    
    battery_soc = battery_initial_soc
    prob_session = charging_sessions_per_day / (24 / dt)
    
    total_ev_energy = 0.0  # sum of all EV demands
    # We'll compute total_operational_cost after the loop by summing cost_grid_arr + cost_battery_arr
    
    for step in range(total_steps):
        current_time = step * dt  # simulation time in hours
        day_of_week = int(current_time // 24) % 7  # 0=Mon,...,6=Sun
        time_in_day = current_time % 24
        
        grid_rate = get_electricity_rate(time_in_day, day_of_week)
        
        # Solar production (kWh) with variability
        irr = solar_irradiance(time_in_day)
        raw_solar_gen = solar_capacity * irr * np.random.uniform(1 - params["solar_randomness"], 1) * dt
        solar_total_arr[step] = raw_solar_gen
        solar_gen = raw_solar_gen
        
        # Generate EV charging demand for this time step
        if np.random.rand() < prob_session:
            demand = charging_station_power * dt  # kWh demand in this step
        else:
            demand = 0.0
        demand_arr[step] = demand
        
        # Step 1: Use available solar energy for EV charging
        energy_from_solar = min(solar_gen, demand)
        solar_used_arr[step] = energy_from_solar
        demand_remaining = demand - energy_from_solar
        solar_gen -= energy_from_solar
        
        # Step 2: Discharge battery if grid_rate >= threshold (but keep SoC above 20%)
        if use_battery and demand_remaining > 0 and grid_rate >= battery_usage_threshold:
            available_for_discharge = max(battery_soc - 0.2 * battery_capacity, 0)
            max_discharge_energy = (battery_max_charge_power * battery_capacity) * dt
            energy_from_battery = min(available_for_discharge, demand_remaining, max_discharge_energy)
            battery_discharged_arr[step] = energy_from_battery
            demand_remaining -= energy_from_battery
            battery_soc -= energy_from_battery
            cost_battery_arr[step] = energy_from_battery * battery_deg_cost
        
        # Step 3: Remaining demand from grid
        energy_from_grid = demand_remaining
        grid_import_arr[step] = energy_from_grid
        cost_grid_arr[step] = energy_from_grid * grid_rate
        
        # Record revenue
        revenue_arr[step] = demand * charging_price
        total_ev_energy += demand
        
        # Step 4a: Use extra solar to charge battery (if any left)
        if use_battery and solar_gen > 0 and battery_soc < battery_capacity:
            available_space = battery_capacity - battery_soc
            energy_to_charge = min(solar_gen * inverter_eff, available_space)
            battery_soc += energy_to_charge
            solar_to_battery_arr[step] = energy_to_charge
        
        # Step 4b: Off-peak grid charging (22:00–04:00)
        if use_battery and (time_in_day < 4 or time_in_day >= 22) and battery_soc < battery_capacity:
            max_grid_charge_energy = (battery_max_charge_power * battery_capacity) * dt
            available_space = battery_capacity - battery_soc
            grid_charge_energy = min(max_grid_charge_energy, available_space)
            battery_soc += grid_charge_energy
            grid_to_battery_arr[step] = grid_charge_energy
            cost_grid_batt = grid_charge_energy * grid_rate
            cost_grid_arr[step] += cost_grid_batt
        
        # Step 4c: Pre-peak charging (16:00–17:00 on Mon–Sat, if SoC < 50%)
        if use_battery and day_of_week < 6 and (16.0 <= time_in_day < 17.0) and battery_soc < 0.5 * battery_capacity:
            max_prepeak_charge = (battery_max_charge_power * battery_capacity) * dt
            available_space = battery_capacity - battery_soc
            prepeak_charge_energy = min(max_prepeak_charge, available_space)
            battery_soc += prepeak_charge_energy
            grid_to_battery_arr[step] += prepeak_charge_energy
            cost_grid_prepeak = prepeak_charge_energy * grid_rate
            cost_grid_arr[step] += cost_grid_prepeak
        
        # Record battery SoC and time
        battery_soc_arr[step] = battery_soc
        time_arr[step] = current_time
    
    # Summaries
    total_operational_cost = cost_grid_arr.sum() + cost_battery_arr.sum()
    total_revenue = revenue_arr.sum()
    grand_total_cost = total_operational_cost + total_depreciation
    net_profit = total_revenue - grand_total_cost
    
    if use_battery and battery_capacity > 0:
        rev_per_batt_kwh = total_revenue / battery_capacity
        battery_cost_per_kwh = (params["battery_pack_price"] * params["number_of_battery_packs"]) / battery_capacity
    else:
        rev_per_batt_kwh = np.nan
        battery_cost_per_kwh = np.nan
    
    # Build a DataFrame for hourly details
    df_hourly = pd.DataFrame({
        "hour": np.arange(total_steps),
        "time_in_day": time_arr,   # in hours
        "ev_demand": demand_arr,
        "cost_grid": cost_grid_arr,
        "cost_battery": cost_battery_arr,
        "cost": cost_grid_arr + cost_battery_arr,  # total cost this step
        "solar_prod": solar_total_arr,
        "direct_solar": solar_used_arr,
        "battery_discharge": battery_discharged_arr,
        "grid_used": grid_import_arr,
        "battery_charged": solar_to_battery_arr + grid_to_battery_arr,
        "soc": battery_soc_arr
    })
    
    results = {
        # The DataFrame for per-hour data
        "hourly_details": df_hourly.to_dict("records"),
        "time": time_arr, 
        # Aggregates
        "solar_total": solar_total_arr, 
        "solar_used": solar_used_arr, 
        "solar_to_battery": solar_to_battery_arr,
        "total_ev_energy": total_ev_energy,

        "total_operational_cost": total_operational_cost,
        "total_depreciation": total_depreciation,
        "grand_total_cost": grand_total_cost,
        "total_revenue": total_revenue,
        "net_profit": net_profit,
        
        "rev_per_batt_kwh": rev_per_batt_kwh,
        "battery_cost_per_kwh": battery_cost_per_kwh,
    }
    return results


# --------------------------------------
# Monte Carlo Simulation
# --------------------------------------

def run_monte_carlo(params, iterations=50):
    net_profits = []
    for i in range(iterations):
        sim = simulate_ev_station(params, seed=i)
        net_profits.append(sim["net_profit"])
    df = pd.DataFrame({"net_profit": net_profits})
    return df

# --------------------------------------
# Grid-Only, Solar-Only, Solar+Storage Scenario Simulations
# --------------------------------------

def simulate_grid_only(params):
    """
    In the Grid Only scenario, all EV charging energy is drawn from the grid.
    """
    daily_ev_demand = params["daily_ev_demand"]
    profile = usage_profile()
    
    total_grid_cost = 0.0
    total_energy = 0.0
    hourly_details = []
    for hour in range(24):
        ev_demand = daily_ev_demand * profile[hour]
        grid_rate = get_electricity_rate(hour, day_of_week=1)
        cost = ev_demand * grid_rate
        total_grid_cost += cost
        total_energy += ev_demand
        hourly_details.append({
            "hour": hour,
            "ev_demand": ev_demand,
            "grid_rate": grid_rate,
            "grid_used": ev_demand,
            "cost": cost,
            "solar_used": 0.0,
            "battery_discharge": 0.0
        })
    capital_cost = params.get("installation_cost", 7000.0)
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
    EV demand is met by solar when available; shortfalls are met by the grid.
    Excess solar is wasted.
    """
    daily_ev_demand = params["daily_ev_demand"]
    solar_capacity = params["solar_capacity"]
    profile = usage_profile()
    
    total_grid_cost = 0.0
    total_energy = 0.0
    total_solar_used = 0.0
    hourly_details = []
    for hour in range(24):
        ev_demand = daily_ev_demand * profile[hour]
        grid_rate = get_electricity_rate(hour, day_of_week=1)
        solar_prod = solar_production(hour, solar_capacity)
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
    In the Solar + Storage scenario, a battery is added.
    Excess solar is stored and later discharged to serve EV demand.
    """
    daily_ev_demand = params["daily_ev_demand"]
    solar_capacity = params["solar_capacity"]
    battery_capacity = params["battery_capacity"]
    max_charge_power = params["battery_max_charge_power"]
    max_discharge_power = params["battery_max_charge_power"]
    profile = usage_profile()
    
    soc = 0.5 * battery_capacity
    battery_history = [soc]
    
    total_grid_cost = 0.0
    total_energy = 0.0
    total_solar_used = 0.0
    total_battery_discharge = 0.0
    hourly_details = []
    
    for hour in range(24):
        ev_demand = daily_ev_demand * profile[hour]
        grid_rate = get_electricity_rate(hour, day_of_week=1)
        solar_prod = solar_production(hour, solar_capacity)
        
        direct_solar = min(ev_demand, solar_prod)
        remaining_demand = ev_demand - direct_solar
        excess_solar = max(solar_prod - ev_demand, 0.0)
        
        charge_possible = min(excess_solar, max_charge_power, battery_capacity - soc)
        soc += charge_possible
        
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

# --------------------------------------
# Annualization and ROI Calculation
# --------------------------------------

def annualize_results(sim_results, params):
    """
    Given simulation results and parameters, compute annualized values and effective cost per kWh,
    as well as annual revenue and net profit.
    
    This function supports simulation results that come from either a multi-day simulation 
    (with a "total_ev_energy" key) or a one-day simulation (with a "daily_energy" key).
    """
    simulation_days = params["simulation_days"]
    
    # Compute total EV energy delivered.
    if "total_ev_energy" in sim_results:
        total_ev_energy = sim_results["total_ev_energy"]
    elif "daily_energy" in sim_results:
        # If only daily_energy is provided, multiply by the number of simulation days
        total_ev_energy = sim_results["daily_energy"] * simulation_days
    else:
        total_ev_energy = np.sum(sim_results.get("demand", []))
    
    # Daily energy (kWh/day) and annual energy (kWh/year)
    daily_energy = total_ev_energy / simulation_days
    annual_energy = daily_energy * 365
    
    # Compute total operational cost.
    if "total_operational_cost" in sim_results:
        total_operational_cost = sim_results["total_operational_cost"]
    elif "daily_operational_cost" in sim_results:
        total_operational_cost = sim_results["daily_operational_cost"] * simulation_days
    else:
        total_operational_cost = (np.sum(sim_results.get("cost_grid", [])) +
                                  np.sum(sim_results.get("cost_battery", [])))
    
    # Annualize operating cost.
    annual_operating_cost = total_operational_cost * (365 / simulation_days)
    
    # Retrieve or compute the total capital cost.
    if "capital_cost" in sim_results and sim_results["capital_cost"] > 0:
        total_capital_cost = sim_results["capital_cost"]
    else:
        station_cost = params["initial_costs"].get("charging_station", 7000) * params["num_stations"]
        inverter_cost = (3000 if params["use_battery"] else 2000) * params["num_stations"]
        battery_cost = (params["battery_pack_price"] * params["number_of_battery_packs"] * params["num_stations"]) if params["use_battery"] else 0
        solar_cost = (params["solar_capacity"] / 10) * 1000
        install_cost = (params["solar_capacity"] / 10) * 1000
        total_capital_cost = station_cost + inverter_cost + battery_cost + solar_cost + install_cost
    
    lifetime = params["capital_lifetime_years"]
    annual_capital_cost = total_capital_cost / lifetime if lifetime > 0 else 0.0
    
    # Effective cost per kWh is the sum of annual operating cost and capital cost divided by annual energy
    effective_cost_per_kwh = (annual_operating_cost + annual_capital_cost) / annual_energy if annual_energy > 0 else float('nan')
    
    annual_revenue = annual_energy * params["charging_price"]
    net_profit = annual_revenue - (annual_operating_cost + annual_capital_cost)
    
    return {
        "annual_energy": annual_energy,
        "annual_operating_cost": annual_operating_cost,
        "annual_capital_cost": annual_capital_cost,
        "effective_cost_per_kwh": effective_cost_per_kwh,
        "annual_revenue": annual_revenue,
        "net_profit": net_profit
    }




# --------------------------------------
# ROI & Sensitivity: Compute ROI for a Configuration
# --------------------------------------

def compute_roi(params):
    """
    Compute ROI using the provided parameters dictionary.
    
    Expected keys in params:
      - "simulation_days": Simulation period in days (should be 30 for this ROI analysis)
      - "charging_sessions_per_day": e.g. 16 (assumed usage)
      - "charging_station_power": e.g. 30 (kW)
      - "charging_price": e.g. 0.5 ($/kWh)
      - "solar_capacity": in kW (must be <= 18)
      - "solar_randomness": e.g. 0.1
      - "use_battery": Boolean (True for hybrid inverter, False for normal)
      - "battery_pack_Ah", "battery_pack_voltage", "battery_pack_price"
      - "number_of_battery_packs": (only for hybrid; 0 if not used)
      - "battery_initial_soc_fraction": e.g. 0.5
      - "battery_efficiency": e.g. 0.9
      - "inverter_efficiency": e.g. 0.95
      - "battery_degradation_cost": e.g. 0.05
      - "battery_usage_threshold": e.g. 0.20
      - "initial_costs": a dict of capital costs (e.g., "charging_station", "solar_panel", "inverter", etc.)
      - "component_lifetime_years": a dict with lifetimes for each component.
      - "num_stations": Number of stations to scale the result.
      - "inverter_type": 'normal' or 'hybrid'
      - (Other keys as needed by simulate_ev_station)
      
    The function runs a 30-day simulation for one station (using simulate_ev_station),
    scales net profit by the number of stations, annualizes it, and computes ROI.
    """
     # Infer inverter_type based on use_battery flag.
    inverter_type = "hybrid" if params.get("use_battery", False) else "normal"
    
    # Run simulation for one station over 30 days.
    sim_result = simulate_ev_station(params, seed=42)
    
    # Retrieve required configuration values from params.
    num_stations = params["num_stations"]
    solar_capacity = params["solar_capacity"]
    if inverter_type == "hybrid":
        num_battery_packs = params["number_of_battery_packs"]
    else:
        num_battery_packs = 0
    
    # Scale net profit by the number of stations and annualize (30-day simulation).
    net_profit = sim_result["net_profit"] * num_stations
    annual_net_profit = net_profit * (365 / 30)
    
    # Compute capital cost for the station:
    station_cost = 7000 * num_stations
    inverter_cost = (3000 if inverter_type == "hybrid" else 2000) * num_stations
    battery_cost = (1000 * num_battery_packs * num_stations) if inverter_type == "hybrid" else 0
    # Assume solar and installation costs: $1000 per 10 kW installed.
    solar_cost = (solar_capacity / 10) * 1000
    install_cost = (solar_capacity / 10) * 1000
    total_capital_cost = station_cost + inverter_cost + battery_cost + solar_cost + install_cost
    
    # Compute ROI as (annual net profit)/(total capital cost)
    roi = annual_net_profit / total_capital_cost
    return roi, annual_net_profit, total_capital_cost

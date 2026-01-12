import numpy as np
import pandas as pd
from app_default import CHARGING_STATION_PRICE, TRANSFORMER_PRICE, SOLAR_PANEL_PRICE, INVERTER_PRICE, INSTALLATION_PRICE, BATTERY_PACK_PRICE
import locale
locale.setlocale(locale.LC_ALL, '')  # set to system default locale

# --------------------------------------
# Helper Functions & Grid Pricing
# --------------------------------------

def format_currency(amount, exchange_rate, symbol):
    # Multiply by the exchange rate
    local_value = amount * exchange_rate
    # Format with grouping for thousands, using system locale
    formatted_value = locale.format_string("%.2f", local_value, grouping=True)
    return f"{symbol}{formatted_value}"

def compute_infrastructure_cost(params, use_roi_constants=False):
    """
    Compute the total infrastructure (capital) cost based on the provided parameters.
    
    If use_roi_constants is True, then use the constant prices from constants.py.
    Otherwise, use the cost values stored in params.
    
    This function assumes that all cost values in params are in USD (i.e. they have been converted
    from local currency already, if applicable).
    """
    num_stations = params.get("num_stations", 1)
    
    if use_roi_constants:
        from app_default import CHARGING_STATION_PRICE, INVERTER_PRICE, BATTERY_PACK_PRICE, SOLAR_PANEL_PRICE, INSTALLATION_PRICE
        station_cost = CHARGING_STATION_PRICE * num_stations
        transformer_cost = TRANSFORMER_PRICE
        inverter_cost = (INVERTER_PRICE if params.get("use_battery", False) else 2000) * num_stations
        battery_cost = (BATTERY_PACK_PRICE * params.get("number_of_battery_packs", 0) * num_stations) if params.get("use_battery", False) else 0
        solar_cost = (params.get("solar_capacity", 0) / 10) * SOLAR_PANEL_PRICE 
        install_cost = (params.get("solar_capacity", 0) / 10) * INSTALLATION_PRICE
    else:
        station_cost = params.get("station_cost", 7000) * num_stations
        transformer_cost = params.get("transformer_cost", 1000) 
        inverter_cost = (params.get("inverter_cost", 3000) if params.get("use_battery", False) else 2000) * num_stations
        battery_cost = (params.get("battery_pack_price", 1000) * params.get("number_of_battery_packs", 0) * num_stations) if params.get("use_battery", False) else 0
        solar_cost = (params.get("solar_capacity", 0) / 10) * 1000 
        install_cost = (params.get("solar_capacity", 0) / 10) * 1000 

    total_capital_cost = station_cost + transformer_cost + solar_cost + inverter_cost + install_cost + battery_cost
    return total_capital_cost


def get_electricity_rate(time_in_day, day_of_week):
    """
    Returns the grid electricity cost ($/kWh) for a given time of day and day of week,
    adjusted for advanced settings including selling excess solar energy.    
     
    Schedule:
      - Sunday (day_of_week == 6): All day uses normal_rate.
      - Mon–Sat:
          Off-peak: time < 4 or time >= 22 → off_peak_rate.
          Peak:     during morning or evening peak periods → peak_rate.
          Otherwise: normal_rate.
          
    If selling excess is enabled, the effective rate is reduced by:
          selling_percentage * excess_price.
    """
    import streamlit as st

    # Retrieve grid tariffs and peak boundaries from session_state
    off_peak_rate = st.session_state.get("off_peak_rate", 0.06)
    normal_rate = st.session_state.get("normal_rate", 0.108)
    peak_rate = st.session_state.get("peak_rate", 0.188)
    peak_start_morning = st.session_state.get("peak_start_morning", 9.5)
    peak_end_morning = st.session_state.get("peak_end_morning", 11.5)
    peak_start_evening = st.session_state.get("peak_start_evening", 17.0)
    peak_end_evening = st.session_state.get("peak_end_evening", 20.0)
    
    # Determine the base rate based on the schedule.
    if day_of_week == 6:
        base_rate = normal_rate
    elif time_in_day < 4 or time_in_day >= 22:
        base_rate = off_peak_rate
    elif (peak_start_morning <= time_in_day < peak_end_morning) or (peak_start_evening <= time_in_day < peak_end_evening):
        base_rate = peak_rate
    else:
        base_rate = normal_rate

    # Adjust for selling excess solar energy if enabled.
    # selling_excess = st.session_state.get("selling_excess", False)
    # if selling_excess:
    #     excess_price = st.session_state.get("excess_price", 0.07)
    #     selling_percentage = st.session_state.get("selling_percentage", 0.0)
    #     # The effective rate is reduced by the revenue from selling a fraction of the solar output.
    #     effective_rate = base_rate - (selling_percentage * excess_price)
    #     return effective_rate
    # else:
    return base_rate


def solar_irradiance(time_in_day):
    """
    Simplified solar irradiance model using a sine curve between 6:00 and 18:00.
    Outside that window, irradiance is 0.
    """
    if 6 <= time_in_day <= 18:
        return np.sin(np.pi * (time_in_day - 6) / 12)
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
    return profile  # Must sums to 1.0


def ev_demand_profile(current_time, dt, params):
    """EV demand generator for simulate_solar_system: deterministic demand based on usage profile."""
    # Assume dt is 1.0 hour and simulation runs for 24 hours.
    profile = usage_profile()  # using the common usage_profile() function
    hour = int(current_time % 24)
    return params["daily_ev_demand"] * profile[hour]


# --- Battery & Energy Flow Helpers for EV Station Simulation ---

def discharge_battery_ev(demand_remaining, battery_soc, battery_capacity, battery_max_charge_power, dt, battery_deg_cost):
    """
    Discharge the battery during an EV charging step in the EV station simulation.
    The function now always attempts to supply battery energy (if available above 20% SOC)
    without checking the grid rate, and uses battery_max_charge_power (in kW) directly.
    """
    if demand_remaining > 0:
        available_for_discharge = max(battery_soc - 0.2 * battery_capacity, 0)
        max_discharge_energy = battery_max_charge_power * dt  # Maximum discharge energy in kWh
        energy_from_battery = min(available_for_discharge, demand_remaining, max_discharge_energy)
        battery_soc -= energy_from_battery
        cost_battery = energy_from_battery * battery_deg_cost
        return energy_from_battery, battery_soc, cost_battery
    return 0.0, battery_soc, 0.0

def offpeak_grid_charge_ev(battery_soc, battery_capacity, battery_max_charge_power, dt, grid_rate):
    """
    Charge the battery from the grid during off-peak hours.
    The max energy per time step is now battery_max_charge_power * dt.
    """
    max_grid_charge_energy = battery_max_charge_power * dt
    available_space = battery_capacity - battery_soc
    grid_charge_energy = min(max_grid_charge_energy, available_space)
    battery_soc += grid_charge_energy
    cost = grid_charge_energy * grid_rate
    return grid_charge_energy, battery_soc, cost

def prepeak_charge_ev(battery_soc, battery_capacity, battery_max_charge_power, dt, grid_rate):
    """
    Charge the battery during the pre-peak period.
    The max energy per time step is now battery_max_charge_power * dt.
    """
    max_prepeak_charge = battery_max_charge_power * dt
    available_space = battery_capacity - battery_soc
    prepeak_charge_energy = min(max_prepeak_charge, available_space)
    battery_soc += prepeak_charge_energy
    cost = prepeak_charge_energy * grid_rate
    return prepeak_charge_energy, battery_soc, cost

def charge_battery_with_energy(energy_available, battery_soc, battery_capacity, inverter_eff):
    """
    Charge the battery with available energy (from solar or grid),
    applying inverter efficiency.
    """
    available_space = battery_capacity - battery_soc
    energy_to_charge = min(energy_available * inverter_eff, available_space)
    battery_soc += energy_to_charge
    return energy_to_charge, battery_soc


def decide_battery_action(time_in_day, battery_soc, battery_capacity, ev_demand, solar_available, grid_rate, dt, params):
    """
    Decide on a battery action for a single time step.
    
    Returns a tuple: (action, energy, cost)
    - action: one of "discharge", "grid_supply", "charge_solar", "charge_grid", or "idle"
    - energy: the amount (in kWh) to discharge or charge
    - cost: the cost associated with that action (if any)
    
    The logic enforces that:
      1. During offpeak (22:00–04:00) and prepeak (04:00–06:00), if the battery is below the target,
         EV demand is met from grid (not discharging the battery) until battery SoC reaches a minimum (80%).
      2. Otherwise, if EV demand exists and battery is available, discharge the battery (up to its limit).
      3. If no EV demand exists, charge the battery from solar first, then (if in offpeak/prepeak and below target)
         charge from the grid.
    """
    # Define time windows (using hours as float)
    offpeak_start = 22.0
    offpeak_end = 4.0      # note: times <4 are offpeak
    prepeak_end = 6.0      # by 6:00 we aim to be 100% charged

    # Target SoC thresholds (in kWh)
    target_normal = 0.8 * battery_capacity  # at least 80% before normal hours
    target_peak = battery_capacity          # 100% before peak hours

    # Maximum energy that can be charged/discharged this time step.
    max_energy = params["battery_max_charge_power"] * dt  # computed from C-rate × capacity

    # Initialize defaults.
    action = "idle"
    energy = 0.0
    cost = 0.0

    # CASE 1: EV demand exists.
    if ev_demand > 0:
        # If we are in offpeak or prepeak, and battery is below target, do not use battery.
        if (time_in_day >= offpeak_start or time_in_day < offpeak_end) or (time_in_day >= offpeak_end and time_in_day < prepeak_end):
            if battery_soc < target_normal:
                # Do not discharge battery; supply EV demand from grid.
                action = "grid_supply"
                energy = ev_demand
                cost = energy * grid_rate
            else:
                # If battery is sufficiently charged, you can discharge.
                available_to_discharge = max(battery_soc - 0.2 * battery_capacity, 0)
                energy = min(ev_demand, max_energy, available_to_discharge)
                action = "discharge"
                cost = energy * params["battery_degradation_cost"]
        else:
            # In normal hours, allow battery discharge if available.
            available_to_discharge = max(battery_soc - 0.2 * battery_capacity, 0)
            energy = min(ev_demand, max_energy, available_to_discharge)
            if energy > 0:
                action = "discharge"
                cost = energy * params["battery_degradation_cost"]
            else:
                action = "grid_supply"
                energy = ev_demand
                cost = energy * grid_rate

    # CASE 2: No EV demand.
    else:
        # First, use available solar to charge battery if not full.
        if solar_available > 0 and battery_soc < battery_capacity:
            energy = min(solar_available, max_energy, battery_capacity - battery_soc)
            action = "charge_solar"
            cost = 0.0  # solar energy is free.
        # If still offpeak/prepeak and battery below target, charge from grid.
        elif ((time_in_day >= offpeak_start or time_in_day < offpeak_end) or (time_in_day >= offpeak_end and time_in_day < prepeak_end)) and battery_soc < target_normal:
            energy = min(max_energy, battery_capacity - battery_soc)
            action = "charge_grid"
            cost = energy * grid_rate
        else:
            action = "idle"
            energy = 0.0
            cost = 0.0

    return action, energy, cost

# -- Shared simulation calculation helper functions

def generate_ev_demand_schedule(params, dt=0.5):
    """
    Generate the EV demand schedule for one day (48 half‑hour steps).
    For each day, randomly select 'charging_sessions_per_day' half‑hour slots 
    and assign full charging demand (charging_station_power * dt, e.g., 
    for a 30 kW port with dt=0.5, that is 15 kWh). All other slots are 0.
    """
    steps_per_day = int(24 / dt)  # should be 48 for dt = 0.5
    ev_demand_schedule = np.zeros(steps_per_day)
    charging_station_power = params["charging_station_power"]
    charging_sessions_per_day = params["charging_sessions_per_day"]
    # Randomly choose distinct half‑hour slots for charging events
    selected = np.random.choice(np.arange(steps_per_day), size=charging_sessions_per_day, replace=False)
    ev_demand_schedule[selected] = charging_station_power * dt
    return ev_demand_schedule

def ev_demand_half_hour(current_time, dt, params):
    """
    Returns the EV demand for the current time step.
    The one-day schedule is computed once and stored in params.
    """
    steps_per_day = int(24 / dt)  # 48 steps
    step = int(current_time / dt)
    if "ev_demand_schedule" not in params:
        ev_demand_schedule = generate_ev_demand_schedule(params, dt)
        params["ev_demand_schedule"] = ev_demand_schedule
    else:
        ev_demand_schedule = params["ev_demand_schedule"]
    return ev_demand_schedule[step]

 

def run_simulation_system(params, ev_demand_generator):
    dt = 0.5  # half-hour time step
    total_steps = int(24 / dt)  # 48 steps for one day

    # Initialize arrays.
    time_arr = np.zeros(total_steps)
    battery_soc_arr = np.zeros(total_steps)
    grid_import_arr = np.zeros(total_steps)
    solar_used_arr = np.zeros(total_steps)
    battery_discharged_arr = np.zeros(total_steps)
    cost_grid_arr = np.zeros(total_steps)
    cost_battery_arr = np.zeros(total_steps)
    demand_arr = np.zeros(total_steps)
    revenue_arr = np.zeros(total_steps)
    solar_total_arr = np.zeros(total_steps)
    solar_to_battery_arr = np.zeros(total_steps)
    grid_to_battery_arr = np.zeros(total_steps)
    solar_sold_arr = np.zeros(total_steps)

    # Set up battery initial conditions.
    if params.get("use_battery", False):
        battery_capacity = params["number_of_battery_packs"] * (params["battery_pack_Ah"] * params["battery_pack_voltage"] / 1000)
        battery_soc = params["battery_initial_soc_fraction"] * battery_capacity
    else:
        battery_capacity = 0.0
        battery_soc = 0.0

    # For daily selling limits.
    daily_total_solar = 0.0
    daily_sold = 0.0
    selling_limit_fraction = params.get("selling_percentage", 0.0)

    # Generate one-day EV demand schedule.
    ev_demand_schedule = generate_ev_demand_schedule(params, dt)

    for step in range(total_steps):
        current_time = step * dt
        time_in_day = current_time % 24

        # Get grid tariff.
        day_of_week = int(current_time // 24) % 7
        grid_rate = get_electricity_rate(time_in_day, day_of_week)

        # Solar production.
        irr = solar_irradiance(time_in_day)
        raw_solar = params["solar_capacity"] * irr * np.random.uniform(1 - params["solar_randomness"], 1) * dt
        solar_total_arr[step] = raw_solar
        solar_available = raw_solar
        daily_total_solar += raw_solar

        # EV demand.
        demand = ev_demand_schedule[step]
        demand_arr[step] = demand

        # Use available solar to directly meet EV demand.
        energy_direct = min(solar_available, demand)
        solar_used_arr[step] = energy_direct
        remaining_demand = demand - energy_direct
        solar_available -= energy_direct

        # Decide on battery action for EV demand.

        if remaining_demand > 0:
            action, energy, action_cost = decide_battery_action(time_in_day, battery_soc, battery_capacity, remaining_demand, 0.0, grid_rate, dt, params)
            if action == "discharge":
                battery_discharged_arr[step] = energy
                battery_soc -= energy
                cost_battery_arr[step] = action_cost
                remaining_demand -= energy
            else:
                # For "grid_supply", we simply supply from the grid.
                grid_import_arr[step] = remaining_demand
                cost_grid_arr[step] = remaining_demand * grid_rate
                revenue_arr[step] = demand * params["charging_price"]
                remaining_demand = 0.0
        else:
            # If EV demand is fully met by solar, then revenue is from solar-supplied charging.
            revenue_arr[step] = demand * params["charging_price"]

        # Now, if no EV demand exists, or after EV demand is met, decide on battery charging.
        if remaining_demand == 0 and params.get("use_battery", False):
            # Decide on charging action using available solar first.
            if solar_available > 0 and battery_soc < battery_capacity:
                charge_amount = min(solar_available, params["battery_max_charge_power"] * dt, battery_capacity - battery_soc)
                battery_soc += charge_amount
                solar_to_battery_arr[step] = charge_amount
                solar_available -= charge_amount
            # If in offpeak or prepeak and battery is below target, consider grid charging.
            action_charge, energy_charge, charge_cost = decide_battery_action(time_in_day, battery_soc, battery_capacity, 0, 0.0, grid_rate, dt, params)
            if action_charge == "charge_grid" and battery_soc < battery_capacity:
                # Do not double-charge: ensure we only charge from one source per time step.
                battery_soc += energy_charge
                grid_to_battery_arr[step] += energy_charge
                cost_grid_arr[step] += energy_charge * grid_rate

        # (Optional) Sell any excess solar if enabled.
        if params.get("sell_excess", False) and demand == 0 and solar_available > 0:
            max_daily_sale = selling_limit_fraction * daily_total_solar
            remaining_sale = max(0.0, max_daily_sale - daily_sold)
            sold = min(solar_available, remaining_sale)
            daily_sold += sold
            revenue_arr[step] += sold * params.get("selling_excess_price", 0.0)
            solar_sold_arr[step] = sold
            solar_available -= sold

        battery_soc_arr[step] = battery_soc
        time_arr[step] = current_time



    total_ev_energy = np.sum(demand_arr) 
    

    return {
        "time_arr": time_arr,
        "battery_soc_arr": battery_soc_arr,
        "grid_import_arr": grid_import_arr,
        "solar_used_arr": solar_used_arr,
        "battery_discharged_arr": battery_discharged_arr,
        "cost_grid_arr": cost_grid_arr,
        "cost_battery_arr": cost_battery_arr,
        "demand_arr": demand_arr,
        "revenue_arr": revenue_arr,
        "solar_total_arr": solar_total_arr,
        "solar_to_battery_arr": solar_to_battery_arr,
        "grid_to_battery_arr": grid_to_battery_arr,
        "solar_sold_arr": solar_sold_arr,
        "total_ev_energy": total_ev_energy
    }

def get_hourly_details(sim_data):
    """
    Convert the simulation result dictionary into a Pandas DataFrame
    that contains hourly details for visualization.
    """
    df = pd.DataFrame({
        "hour": sim_data["time_arr"] % 24,
        "ev_demand_rate": sim_data["demand_arr"],
        "grid_import_rate": sim_data["grid_import_arr"],
        "solar_produced": sim_data["solar_total_arr"],
        "direct_solar": sim_data["solar_used_arr"],
        "battery_discharged": sim_data["battery_discharged_arr"],
        "battery_soc": sim_data["battery_soc_arr"],
        "solar_to_battery": sim_data["solar_to_battery_arr"],
        "solar_sold": sim_data["solar_sold_arr"],
        "cost_grid": sim_data["cost_grid_arr"],
        "grid_used":sim_data["grid_import_arr"],
        "cost_battery": sim_data["cost_battery_arr"],
        "revenue": sim_data["revenue_arr"]
    })
    # Aggregate total cost from grid and battery:
    df["cost"] = df["cost_grid"] + df["cost_battery"]
    return df



def aggregate_results(sim_data, simulation_days):
    """
    Compute daily aggregates from the half-hourly simulation data and then derive monthly and yearly values.
    """
    total_solar = sim_data["solar_total_arr"].sum()
    total_direct = sim_data["solar_used_arr"].sum()
    total_to_battery = sim_data["solar_to_battery_arr"].sum() + sim_data["grid_to_battery_arr"].sum()
    total_sold = sim_data["solar_sold_arr"].sum()
    total_used = total_direct + total_to_battery
    total_wasted = total_solar - (total_used + total_sold)
    
    daily = {
        "daily_solar_produced": total_solar / simulation_days,
        "daily_grid_import": sim_data["grid_import_arr"].sum() / simulation_days,
        "daily_grid_export": total_sold / simulation_days,
        "daily_solar_used": (total_used + total_sold) / simulation_days,
        "daily_solar_wasted": total_wasted / simulation_days
    }
    monthly = { key: value * 30 for key, value in daily.items() }
    yearly = { key: value * 365 for key, value in daily.items() }
    return {"daily": daily, "monthly": monthly, "yearly": yearly}


# --------------------------------------
# EV Station Simulation (Half-hour Time Steps)
# --------------------------------------

def simulate_station(params, seed=None):
    """
    Core simulation engine for one station over one day (48 half-hour steps).
    Returns a dictionary with time series arrays for energy flows, costs, revenue, and aggregated totals.
    """
    if seed is not None:
        np.random.seed(seed)
    dt = 0.5
    steps = int(24 / dt)
    time_arr = np.zeros(steps)
    battery_soc_arr = np.zeros(steps)
    grid_import_arr = np.zeros(steps)
    solar_used_arr = np.zeros(steps)
    battery_discharged_arr = np.zeros(steps)
    cost_grid_arr = np.zeros(steps)
    cost_battery_arr = np.zeros(steps)
    demand_arr = np.zeros(steps)
    revenue_arr = np.zeros(steps)
    solar_total_arr = np.zeros(steps)
    solar_to_battery_arr = np.zeros(steps)
    solar_sold_arr = np.zeros(steps)
    
    # Battery parameters per station.
    if params.get("use_battery", False):
        Ah = params["battery_pack_Ah"]
        voltage = params["battery_pack_voltage"]
        num_packs = params["number_of_battery_packs"]
        battery_capacity = num_packs * (Ah * voltage / 1000)  # in kWh
        battery_soc = params["battery_initial_soc_fraction"] * battery_capacity
    else:
        battery_capacity = 0.0
        battery_soc = 0.0

    # EV demand per station.
    ev_demand = generate_ev_demand_schedule(params, dt)
    
    for i in range(steps):
        current_time = i * dt
        time_arr[i] = current_time
        time_in_day = current_time % 24
        day_of_week = int(current_time // 24) % 7
        grid_rate = get_electricity_rate(time_in_day, day_of_week)
        
        # Solar production per station.
        irr = solar_irradiance(time_in_day)
        solar_prod = params["solar_capacity"] * irr * np.random.uniform(1 - params["solar_randomness"], 1) * dt
        solar_total_arr[i] = solar_prod
        
        # EV demand.
        demand = ev_demand[i]
        demand_arr[i] = demand
        
        # Use solar directly.
        solar_used = min(solar_prod, demand)
        solar_used_arr[i] = solar_used
        remaining = demand - solar_used
        leftover_solar = solar_prod - solar_used
        
        # If demand remains, try to discharge battery (if enabled).
        if remaining > 0 and params.get("use_battery", False):
            discharged, battery_soc, cost_batt = discharge_battery_ev(remaining, battery_soc, battery_capacity, params["battery_max_charge_power"], dt, params["battery_degradation_cost"])
            battery_discharged_arr[i] = discharged
            cost_battery_arr[i] = cost_batt
            remaining -= discharged
        
        # Any remaining demand is met from grid.
        grid_import_arr[i] = remaining
        cost_grid_arr[i] = remaining * grid_rate
        revenue_arr[i] = demand * params["charging_price"]
        
        # Use leftover solar to charge battery (if not full).
        if params.get("use_battery", False) and leftover_solar > 0 and battery_soc < battery_capacity:
            charged, battery_soc = charge_battery_with_energy(leftover_solar, battery_soc, battery_capacity, params["inverter_efficiency"])
            solar_to_battery_arr[i] = charged
            leftover_solar -= charged
        
        # Sell any excess solar if enabled.
        if params.get("sell_excess", False) and leftover_solar > 0:
            sold = leftover_solar * params.get("selling_percentage", 1.0)
            solar_sold_arr[i] = sold
            revenue_arr[i] += sold * params.get("selling_excess_price", 0)
            leftover_solar -= sold
        
        battery_soc_arr[i] = battery_soc

    total_ev_energy = np.sum(demand_arr)
    sim_data = {
        "time_arr": time_arr,
        "battery_soc_arr": battery_soc_arr,
        "grid_import_arr": grid_import_arr,
        "solar_used_arr": solar_used_arr,
        "battery_discharged_arr": battery_discharged_arr,
        "cost_grid_arr": cost_grid_arr,
        "cost_battery_arr": cost_battery_arr,
        "demand_arr": demand_arr,
        "revenue_arr": revenue_arr,
        "solar_total_arr": solar_total_arr,
        "solar_to_battery_arr": solar_to_battery_arr,
        "solar_sold_arr": solar_sold_arr,
        "total_ev_energy": total_ev_energy
    }
    return sim_data
##############################################
# Scaling Simulation to Multiple Stations
##############################################

def scale_simulation_results(sim_data, num_stations):
    """
    Multiply key aggregated values and arrays by the number of stations.
    """
    sim_data["demand_arr"] *= num_stations
    sim_data["revenue_arr"] *= num_stations
    sim_data["grid_import_arr"] *= num_stations
    sim_data["battery_discharged_arr"] *= num_stations
    sim_data["solar_used_arr"] *= num_stations
    sim_data["solar_total_arr"] *= num_stations
    sim_data["solar_to_battery_arr"] *= num_stations
    sim_data["solar_sold_arr"] *= num_stations
    sim_data["total_ev_energy"] *= num_stations
    sim_data["cost_grid_arr"] *= num_stations  
    sim_data["cost_battery_arr"] *= num_stations  
    return sim_data

def simulate_ev_station(params, seed=None):
    """
    Simulate the EV station for ALL stations.
    Run simulation for one station and then scale the results.
    """
    sim_data = simulate_station(params, seed)
    n = params.get("num_stations", 1)
    sim_data = scale_simulation_results(sim_data, n)
    return sim_data

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

##############################################
# Scenario Wrappers
##############################################

def simulate_grid_only(params):
    grid_params = params.copy()
    grid_params["solar_capacity"] = 0
    grid_params["use_battery"] = False
    return simulate_ev_station(grid_params)

def simulate_solar_only(params):
    solar_params = params.copy()
    solar_params["use_battery"] = False
    return simulate_ev_station(solar_params)

def simulate_solar_storage(params):
    return simulate_ev_station(params)

##############################################
# Aggregation and Annualization
##############################################

def aggregate_results(sim_data, simulation_days):
    total_solar = sim_data["solar_total_arr"].sum()
    total_direct = sim_data["solar_used_arr"].sum()
    total_to_battery = sim_data["solar_to_battery_arr"].sum()
    total_sold = sim_data["solar_sold_arr"].sum()
    total_used = total_direct + total_to_battery
    total_wasted = total_solar - (total_used + total_sold)
    
    daily = {
        "daily_solar_produced": total_solar / simulation_days,
        "daily_grid_import": sim_data["grid_import_arr"].sum() / simulation_days,
        "daily_solar_used": total_used / simulation_days,
        "daily_solar_wasted": total_wasted / simulation_days
    }
    monthly = { key: value * 30 for key, value in daily.items() }
    yearly = { key: value * 365 for key, value in daily.items() }
    return {"daily": daily, "monthly": monthly, "yearly": yearly}

def annualize_results(sim_results, params):
    total_ev_energy = np.sum(sim_results["demand_arr"])

    other_operational_cost = params.get("other_operational_cost", 0)  # $ per month
    daily_other_cost = other_operational_cost / 30  # convert to per day

    daily_operating_cost = (
        np.sum(sim_results["cost_grid_arr"]) * params.get("num_stations")
        + np.sum(sim_results["cost_battery_arr"]) * params.get("num_stations")
        + daily_other_cost
    )        
    annual_energy = total_ev_energy * 365

    
    annual_operating_cost = daily_operating_cost * 365

    total_capital_cost = compute_infrastructure_cost(params)
    combined_lifetime = 10.0  # assumed lifetime in years
    annual_capital_cost = total_capital_cost / combined_lifetime

    effective_cost_per_kwh = ((annual_operating_cost + annual_capital_cost) / annual_energy
                              if annual_energy > 0 else float('nan'))

    total_revenue = np.sum(sim_results.get("revenue_arr", []))
    annual_revenue = total_revenue * 365

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

def compute_profit(params, seed=42):
    """
    Compute the annual net profit for a configuration using detailed simulation outputs.
    
    This method runs the simulation (scaled for all stations), calculates the daily profit
    as (daily revenue - daily operating cost), annualizes it, and then subtracts the annualized
    depreciation of the infrastructure.
    """
    # Run the simulation (already scaled by num_stations)
    sim_results = simulate_ev_station(params, seed)
    
    # Calculate daily revenue and operating cost from simulation arrays.
    daily_revenue = np.sum(sim_results["revenue_arr"])
    # Retrieve the additional operational cost (defaulting to 0 if not provided)
    other_operational_cost = params.get("other_operational_cost", 0)  # $ per month
    daily_other_cost = other_operational_cost / 30  # convert to per day

    daily_operating_cost = (
        np.sum(sim_results["cost_grid_arr"]) * params.get("num_stations")
        + np.sum(sim_results["cost_battery_arr"]) * params.get("num_stations")
        + daily_other_cost
    )    
    # Daily profit is revenue minus operating cost.
    daily_profit = daily_revenue - daily_operating_cost
    
    # Annualize profit.
    annual_profit = daily_profit * 365
    
    # Compute total infrastructure cost for all stations.
    total_capital_cost = compute_infrastructure_cost(params)
    
    # Assume a combined lifetime for depreciation (e.g., 10 years).
    annual_depreciation = total_capital_cost / 10.0
    
    # Net profit is annual profit minus annual depreciation.
    net_profit = annual_profit - annual_depreciation
    
    return net_profit


def compute_roi(params):
    sim_result = simulate_ev_station(params, seed=42)
    net_profit = compute_profit(params)
    annual_net_profit = net_profit * 365
    total_capital_cost = compute_infrastructure_cost(params, use_roi_constants=True)
    roi = annual_net_profit / total_capital_cost
    return roi, annual_net_profit, total_capital_cost
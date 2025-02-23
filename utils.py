import numpy as np
import pandas as pd
from constants import CHARGING_STATION_PRICE, TRANSFORMER_PRICE, SOLAR_PANEL_PRICE, INVERTER_PRICE, INSTALLATION_PRICE, BATTERY_PACK_PRICE
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


def get_electricity_rate(time_in_day, day_of_week):
    """
    Returns the grid electricity cost ($/kWh) for a given time of day and day of week,
    adjusted for advanced settings including selling excess solar energy.
    
    Advanced Settings (read from st.session_state):
      - off_peak_rate: Off-peak tariff rate ($/kWh).
      - normal_rate:   Normal tariff rate ($/kWh).
      - peak_rate:     Peak tariff rate ($/kWh).
      - peak_start_morning, peak_end_morning: Morning peak period.
      - peak_start_evening, peak_end_evening: Evening peak period.
      - selling_excess (bool): If True, selling excess solar energy is enabled.
      - excess_price: Expected selling price ($/kWh) for excess solar energy.
      - selling_percentage: Fraction of solar output sold (0.0 to 1.0).
      
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
    return profile  # Sums to 1.0


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
    """
    Runs the simulation for one day at 30-minute resolution (48 time steps).
    For each step, it computes:
      - Solar production (with randomness)
      - EV demand (via the given ev_demand_generator)
      - Direct solar usage to meet EV demand
      - Battery discharge to cover any remaining demand
      - Grid import for any unmet demand
      - Battery charging from leftover solar and from grid (if conditions allow)
      - Selling of excess solar energy (if enabled)
    Returns a dictionary containing arrays (of length 48) for each variable.
    """
    dt = 0.5  # half-hour time step
    total_steps = int(24 / dt)  # 48 steps for one day

    # Initialize arrays.
    time_arr = np.zeros(total_steps)
    battery_soc_arr = np.zeros(total_steps)
    grid_import_arr = np.zeros(total_steps)
    solar_used_arr = np.zeros(total_steps)      # direct solar used for EV charging
    battery_discharged_arr = np.zeros(total_steps)
    cost_grid_arr = np.zeros(total_steps)
    cost_battery_arr = np.zeros(total_steps)
    demand_arr = np.zeros(total_steps)
    revenue_arr = np.zeros(total_steps)
    solar_total_arr = np.zeros(total_steps)       # total solar produced
    solar_to_battery_arr = np.zeros(total_steps)    # solar used to charge battery
    grid_to_battery_arr = np.zeros(total_steps)     # grid energy used for battery charging
    solar_sold_arr = np.zeros(total_steps)          # solar energy sold

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
    selling_limit_fraction = params.get("selling_percentage", 0.0)  # e.g., 0.20 for 20%

    # Generate the one-day EV demand schedule.
    ev_demand_schedule = generate_ev_demand_schedule(params, dt)

    for step in range(total_steps):
        current_time = step * dt
        time_in_day = current_time % 24  # will be between 0 and 24

        # Determine grid tariff.
        day_of_week = int(current_time // 24) % 7  # In a one-day simulation this may always be 0
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

        # Step 1: Direct use of solar for EV charging.
        energy_direct = min(solar_available, demand)
        solar_used_arr[step] = energy_direct
        remaining_demand = demand - energy_direct
        solar_available -= energy_direct

        # Step 2: Use battery to meet remaining demand.
        energy_batt, battery_soc, batt_cost = discharge_battery_ev(
            remaining_demand, battery_soc, battery_capacity, params["battery_max_charge_power"], dt, params["battery_degradation_cost"]
        )
        battery_discharged_arr[step] = energy_batt
        remaining_demand -= energy_batt
        cost_battery_arr[step] = batt_cost

        # Step 3: Use grid to cover any remaining EV demand.
        grid_import_arr[step] = remaining_demand
        cost_grid_arr[step] = remaining_demand * grid_rate
        revenue_arr[step] = demand * params["charging_price"]

        # Step 4a: Use any leftover solar to charge the battery.
        if params.get("use_battery", False) and solar_available > 0 and battery_soc < battery_capacity:
            charged, battery_soc = charge_battery_with_energy(solar_available, battery_soc, battery_capacity, params["inverter_efficiency"])
            solar_to_battery_arr[step] = charged
            solar_available -= charged

        # Step 4b: Off-peak grid battery charging (e.g., before 4:00 or after 22:00).
        if params.get("use_battery", False) and (time_in_day < 4 or time_in_day >= 22) and battery_soc < battery_capacity:
            grid_charged, battery_soc, grid_batt_cost = offpeak_grid_charge_ev(
                battery_soc, battery_capacity, params["battery_max_charge_power"], dt, grid_rate
            )
            grid_to_battery_arr[step] += grid_charged
            cost_grid_arr[step] += grid_batt_cost

        # Step 4c: (Optional) Pre-peak grid charging between 4:00–6:00 if battery SOC is low.
        if params.get("use_battery", False) and (4 <= time_in_day < 6) and battery_soc < params.get("battery_target_soc", 0.5) * battery_capacity:
            grid_charged, battery_soc, grid_batt_cost = offpeak_grid_charge_ev(
                battery_soc, battery_capacity, params["battery_max_charge_power"], dt, grid_rate
            )
            grid_to_battery_arr[step] += grid_charged
            cost_grid_arr[step] += grid_batt_cost

        # Step 4d: Sell excess solar if enabled and if there is surplus.
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
def simulate_ev_station(params, seed=None):
    """
    Simulate EV station operations for one day (48 half-hour steps).
    Returns a dictionary with hourly details and key aggregate results.
    """
    if seed is not None:
        np.random.seed(seed)
    dt = 0.5
    total_steps = int(24 / dt)  # 48 steps

    # Basic parameters.
    charging_station_power = params["charging_station_power"]
    # 'charging_sessions_per_day' is the number of 30-minute charging events in one day.
    solar_capacity = params["solar_capacity"]
    battery_max_charge_power = params["battery_max_charge_power"]

    # Battery parameters.
    if params.get("use_battery", False):
        battery_pack_Ah = params["battery_pack_Ah"]
        battery_pack_voltage = params["battery_pack_voltage"]
        number_of_battery_packs = params["number_of_battery_packs"]
        battery_capacity = number_of_battery_packs * (battery_pack_Ah * battery_pack_voltage / 1000)
        battery_initial_soc = params["battery_initial_soc_fraction"] * battery_capacity
    else:
        battery_capacity = 0.0
        battery_initial_soc = 0.0

    battery_deg_cost = params["battery_degradation_cost"]
    charging_price = params["charging_price"]

    # Capital cost components & depreciation remain unchanged.
    cost_components = {
        "charging_station": params["station_cost"] * params["num_stations"],
        "transformer": params["transformer_cost"],
        "solar_panel": params["solar_panel_cost"],
        "inverter": params["inverter_cost"] * params["num_stations"],
        "installation": params["installation_cost"],
        "battery": params["battery_cost"] if params.get("use_battery", False) else 0.0
    }
    lifetimes = {
        "charging_station": params["charging_station_lifetime"],
        "transformer": params["transformer_lifetime"],
        "solar_panel": params["solar_panel_lifetime"],
        "inverter": params["inverter_lifetime"],
        "installation": params["installation_lifetime"],
        "battery": params["battery_lifetime"]
    }
    # For a one-day simulation, set sim_years to 1/365.
    sim_years = 1 / 365.0
    depreciation = {comp: cost * (sim_years / lifetimes.get(comp, 10))
                    for comp, cost in cost_components.items()}
    total_depreciation = sum(depreciation.values())

    # Generate the one-day EV demand schedule.
    ev_demand_schedule = generate_ev_demand_schedule(params, dt)

    # Initialize arrays (similar to run_simulation_system).
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

    battery_soc = battery_initial_soc
    total_ev_energy = 0.0

    for step in range(total_steps):
        current_time = step * dt
        day_of_week = int(current_time // 24) % 7
        time_in_day = current_time % 24

        grid_rate = get_electricity_rate(time_in_day, day_of_week)
        irr = solar_irradiance(time_in_day)
        raw_solar_gen = solar_capacity * irr * np.random.uniform(1 - params["solar_randomness"], 1) * dt
        solar_total_arr[step] = raw_solar_gen
        solar_gen = raw_solar_gen

        # EV demand from schedule.
        demand = ev_demand_schedule[step]
        demand_arr[step] = demand

        # Use solar directly.
        energy_from_solar = min(solar_gen, demand)
        solar_used_arr[step] = energy_from_solar
        remaining_demand = demand - energy_from_solar
        solar_gen -= energy_from_solar

        # Battery discharge.
        energy_from_battery, battery_soc, batt_cost = discharge_battery_ev(
            remaining_demand, battery_soc, battery_capacity, battery_max_charge_power, dt, battery_deg_cost
        )
        battery_discharged_arr[step] = energy_from_battery
        remaining_demand -= energy_from_battery
        cost_battery_arr[step] = batt_cost

        # Grid import.
        grid_import_arr[step] = remaining_demand
        cost_grid_arr[step] = remaining_demand * grid_rate

        revenue_arr[step] = demand * charging_price
        total_ev_energy += demand

        # Battery charging from leftover solar.
        if params.get("use_battery", False) and solar_gen > 0 and battery_soc < battery_capacity:
            charged, battery_soc = charge_battery_with_energy(solar_gen, battery_soc, battery_capacity, params["inverter_efficiency"])
            solar_to_battery_arr[step] = charged
            solar_gen -= charged

        # Sell excess solar if enabled.
        if params.get("sell_excess", False) and solar_gen > 0:
            sold = solar_gen * params.get("selling_percentage", 1.0)
            solar_sold_arr[step] = sold
            revenue_arr[step] += sold * params.get("selling_excess_price", 0)
            solar_gen -= sold
        else:
            solar_sold_arr[step] = 0.0

        # Off-peak grid battery charging.
        if params.get("use_battery", False) and (time_in_day < 4 or time_in_day >= 22) and battery_soc < battery_capacity:
            grid_charge, battery_soc, grid_batt_cost = offpeak_grid_charge_ev(
                battery_soc, battery_capacity, battery_max_charge_power, dt, grid_rate
            )
            grid_to_battery_arr[step] += grid_charge
            cost_grid_arr[step] += grid_batt_cost

        # Pre-peak battery charging on Mon–Sat if SoC < 50%.
        if params.get("use_battery", False) and day_of_week < 6 and (16.0 <= time_in_day < 17.0) and battery_soc < 0.5 * battery_capacity:
            prepeak_charge, battery_soc, prepeak_cost = prepeak_charge_ev(
                battery_soc, battery_capacity, battery_max_charge_power, dt, grid_rate
            )
            grid_to_battery_arr[step] += prepeak_charge
            cost_grid_arr[step] += prepeak_cost

        battery_soc_arr[step] = battery_soc
        time_arr[step] = current_time

    total_operational_cost = cost_grid_arr.sum() + cost_battery_arr.sum()
    total_revenue = revenue_arr.sum()
    grand_total_cost = total_operational_cost + total_depreciation
    net_profit = total_revenue - grand_total_cost

    results = {
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
        "total_ev_energy": total_ev_energy,
        "total_operational_cost": total_operational_cost,
        "total_depreciation": total_depreciation,
        "grand_total_cost": grand_total_cost,
        "total_revenue": total_revenue,
        "net_profit": net_profit
    }
    return results



def simulate_solar_system(params, use_battery):
    """
    Simulate the solar system (with or without battery storage) for one day at 30-minute resolution.
    Returns a dictionary with hourly details and aggregates, where daily results are later scaled to annual values.
    """
    params_day = params.copy()
    params_day["simulation_days"] = 1  
    sim_data = run_simulation_system(params_day, ev_demand_half_hour)
    aggregates = aggregate_results(sim_data, 1)  # aggregates computed over one day
    solar_to_batt = sim_data["solar_to_battery_arr"] + sim_data["grid_to_battery_arr"]
    
    df_hourly = pd.DataFrame({
        "hour": sim_data["time_arr"] % 24,
        "time": sim_data["time_arr"],
        "ev_demand": sim_data["demand_arr"],
        "grid_used": sim_data["grid_import_arr"],
        "solar_prod": sim_data["solar_total_arr"],
        "direct_solar": sim_data["solar_used_arr"],
        "battery_charged": solar_to_batt,
        "battery_discharged": sim_data["battery_discharged_arr"],
        "solar_sold": sim_data["solar_sold_arr"],
        "cost_grid": sim_data["cost_grid_arr"],
        "cost_battery": sim_data["cost_battery_arr"]
    }).to_dict("records")
    
    total_grid_cost = sim_data["cost_grid_arr"].sum()
    total_energy = sim_data["demand_arr"].sum()
    total_revenue = sim_data["revenue_arr"].sum()
    
    station_cost = params["station_cost"] * params["num_stations"]
    transformer_cost = params["transformer_cost"]
    solar_panel_cost = params["solar_panel_cost"]
    inverter_cost = params["inverter_cost"] * params["num_stations"]
    installation_cost = params["installation_cost"]
    battery_cost = params["battery_cost"] if use_battery else 0.0
    total_capital_cost = station_cost + transformer_cost + solar_panel_cost + inverter_cost + installation_cost + battery_cost
    
    results = {
        "hourly_details": df_hourly,
        "time": sim_data["time_arr"],
        "solar_total": sim_data["solar_total_arr"],
        "solar_used": sim_data["solar_used_arr"],
        "solar_to_battery": solar_to_batt,
        "total_ev_energy": total_energy,
        "total_grid_cost": total_grid_cost,
        "total_revenue": total_revenue,
        "total_capital_cost": total_capital_cost,
        "aggregates": aggregates,
        # <-- Add these lines so annualize_results can compute operating cost:
        "cost_grid_arr": sim_data["cost_grid_arr"],
        "cost_battery_arr": sim_data["cost_battery_arr"],
        "revenue_arr": sim_data["revenue_arr"]
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
    Simulate the grid-only scenario using half-hour time steps.
    All EV demand is met by grid import, and solar and battery contributions are zero.
    """
    dt = 0.5
    total_steps = int(24 / dt)  # 48 steps for one day

    # Compute daily EV demand as before.
    daily_ev_demand = params.get("daily_ev_demand", 
                                 params["charging_station_power"] * params["charging_sessions_per_day"] * dt)
    # Create a 48-step demand profile by distributing daily demand
    # (For simplicity, interpolate the 24-hour profile to 48 half-hour steps)
    base_profile = np.array(usage_profile())  # 24 values summing to 1
    # Duplicate each hour's value for half-hour resolution
    half_hour_profile = np.repeat(base_profile, 2)  
    # Adjust if needed so that it sums to 1
    half_hour_profile /= half_hour_profile.sum()

    time_arr = np.arange(0, 24, dt)
    demand_arr = daily_ev_demand * half_hour_profile
    grid_import_arr = demand_arr.copy()  # All demand met by grid
    cost_grid_arr = np.zeros(total_steps)
    for i, t in enumerate(time_arr):
        grid_rate = get_electricity_rate(t, day_of_week=1)
        cost_grid_arr[i] = demand_arr[i] * grid_rate

    sim_results = {
        "time_arr": time_arr,
        "demand_arr": demand_arr,
        "grid_import_arr": grid_import_arr,
        "cost_grid_arr": cost_grid_arr,
        # For compatibility, fill in zeros for keys not used
        "solar_total_arr": np.zeros(total_steps),
        "solar_used_arr": np.zeros(total_steps),
        "solar_to_battery_arr": np.zeros(total_steps),
        "grid_to_battery_arr": np.zeros(total_steps),
        "battery_discharged_arr": np.zeros(total_steps),
        "cost_battery_arr": np.zeros(total_steps),
        "revenue_arr": demand_arr * params["charging_price"],
        "total_ev_energy": demand_arr.sum(),
    }
    return sim_results


# --------------------------------------
# Annualization and ROI Calculation
# --------------------------------------

def annualize_results(sim_results, params):
    """
    Given one-day simulation results, compute annualized values by multiplying daily
    values by 365.
    """
    total_ev_energy = sim_results.get("total_ev_energy", np.sum(sim_results.get("demand_arr", [])))
    annual_energy = total_ev_energy * 365

    total_operational_cost = sim_results.get("total_operational_cost",
                                             np.sum(sim_results.get("cost_grid_arr", [])) +
                                             np.sum(sim_results.get("cost_battery_arr", [])))
    annual_operating_cost = total_operational_cost * 365

    station_cost = params["station_cost"] * params["num_stations"]
    transformer_cost = params["transformer_cost"]
    solar_panel_cost = params["solar_panel_cost"]
    inverter_cost = params["inverter_cost"] * params["num_stations"]
    installation_cost = params["installation_cost"]
    battery_cost = params["battery_cost"] if params.get("use_battery", False) else 0.0

    annual_station_cost = station_cost / params["charging_station_lifetime"]
    annual_transformer_cost = transformer_cost / params["transformer_lifetime"]
    annual_solar_panel_cost = solar_panel_cost / params["solar_panel_lifetime"]
    annual_inverter_cost = inverter_cost / params["inverter_lifetime"]
    annual_installation_cost = installation_cost / params["installation_lifetime"]
    annual_battery_cost = (battery_cost / params["battery_lifetime"]) if params.get("use_battery", False) else 0.0

    annual_capital_cost = (annual_station_cost + annual_transformer_cost + annual_solar_panel_cost +
                           annual_inverter_cost + annual_installation_cost + annual_battery_cost)

    effective_cost_per_kwh = ((annual_operating_cost + annual_capital_cost) / annual_energy
                              if annual_energy > 0 else float('nan'))

    total_revenue = sim_results.get("total_revenue", np.sum(sim_results.get("revenue_arr", [])))
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

def compute_roi(params):
    """
    Compute ROI for a configuration based on a one-day simulation.
    The simulation result is annualized by multiplying daily net profit by 365.
    """
    inverter_type = "hybrid" if params.get("use_battery", False) else "normal"
    sim_result = simulate_ev_station(params, seed=42)
    num_stations = params["num_stations"]
    solar_capacity = params["solar_capacity"]
    if inverter_type == "hybrid":
        num_battery_packs = params["number_of_battery_packs"]
    else:
        num_battery_packs = 0

    net_profit = sim_result["net_profit"] * num_stations
    annual_net_profit = net_profit * 365  # Annualize from one-day result

    station_cost = CHARGING_STATION_PRICE * num_stations
    inverter_cost = (INVERTER_PRICE if inverter_type == "hybrid" else 2000) * num_stations
    battery_cost = (BATTERY_PACK_PRICE * num_battery_packs * num_stations) if inverter_type == "hybrid" else 0
    solar_cost = (solar_capacity / 10) * SOLAR_PANEL_PRICE
    install_cost = (solar_capacity / 10) * INSTALLATION_PRICE
    total_capital_cost = station_cost + inverter_cost + battery_cost + solar_cost + install_cost

    roi = annual_net_profit / total_capital_cost
    return roi, annual_net_profit, total_capital_cost
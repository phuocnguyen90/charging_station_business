import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from main import simulate_ev_station
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Assume simulate_ev_station(params, seed) is defined (with our previous logic)
# and helper functions get_electricity_rate and solar_irradiance are available.

def compute_roi(num_stations, inverter_type, num_battery_packs, solar_capacity):
    """
    For a given configuration, run a 30-day simulation for one station and then scale
    revenue and net profit by the number of stations. Then compute the total capital cost
    and ROI = (annualized net profit) / (capital cost).

    inverter_type: 'normal' or 'hybrid'
    num_battery_packs: number of 5 kWh packs per station (only used if hybrid)
    solar_capacity: in kW (must be <= 18)
    
    **Utilization Update:**  
    We assume each station is used for 8 hours per day. With dt = 0.5 hr, this means 16 time steps per day
    will have EV charging demand.
    """
    params = {
         "simulation_days": 30,
         # Set charging_sessions_per_day = 16 to simulate 8 hours (16 * 0.5 hr = 8 hr) of usage per day.
         "charging_sessions_per_day": 16,  
         "charging_station_power": 30,     # kW; assume each session yields 30 kW*0.5 = 15 kWh demand per step
         "charging_price": 0.5,            # revenue per kWh delivered
         "solar_capacity": solar_capacity, # kW installed solar capacity (<= 18)
         "solar_randomness": 0.1,          # variability factor
         "use_battery": True if inverter_type=="hybrid" else False,
         # For hybrid, we assume a default battery pack spec (if used)
         "battery_pack_Ah": 280 if inverter_type=="hybrid" else 0,
         "battery_pack_voltage": 51.2 if inverter_type=="hybrid" else 0,
         "battery_pack_price": 1000,       # $ per 5 kWh pack
         "number_of_battery_packs": num_battery_packs if inverter_type=="hybrid" else 0,
         "battery_initial_soc_fraction": 0.5 if inverter_type=="hybrid" else 0.0,
         "battery_efficiency": 0.9,
         "inverter_efficiency": 0.95,
         "battery_degradation_cost": 0.05,
         "battery_usage_threshold": 0.20,
         "initial_costs": {
              "charging_station": 7000, 
              "transformer": 0,             # not used
              "solar_panel": 1000,          # per 10 kW
              "inverter": 3000 if inverter_type=="hybrid" else 2000, 
              "installation": 1000,         # per 10 kW
         },
         "component_lifetime_years": {
              "charging_station": 10,
              "transformer": 15,
              "solar_panel": 25,
              "battery": 10,
              "inverter": 10,
              "installation": 10,
         },
    }
    
    # Run the simulation for one station
    sim_result = simulate_ev_station(params, seed=42)
    
    # Scale net profit by number of stations
    net_profit = sim_result["net_profit"] * num_stations
    # Annualize net profit (from a 30-day simulation)
    annual_net_profit = net_profit * (365 / 30)
    
    # --- Compute capital cost ---
    station_cost = 7000 * num_stations
    inverter_cost = (3000 if inverter_type=="hybrid" else 2000) * num_stations
    battery_cost = (1000 * num_battery_packs * num_stations) if inverter_type=="hybrid" else 0
    solar_cost = (solar_capacity / 10) * 1000
    install_cost = (solar_capacity / 10) * 1000
    total_capital_cost = station_cost + inverter_cost + battery_cost + solar_cost + install_cost
    
    roi = annual_net_profit / total_capital_cost
    return roi, annual_net_profit, total_capital_cost

# --- Grid Search Over the Discrete Design Space ---
results_list = []
# Design space boundaries:
for num_stations in [1, 2]:
    for inverter_type in ['normal', 'hybrid']:
        if inverter_type == 'normal':
            # For a normal inverter (no battery)
            for solar_capacity in range(2, 19, 2):  # Solar capacity: 2 kW to 18 kW (step 2)
                num_battery_packs = 0
                roi, annual_profit, capital_cost = compute_roi(num_stations, inverter_type, num_battery_packs, solar_capacity)
                results_list.append({
                    'num_stations': num_stations,
                    'inverter_type': 0,  # encode normal as 0
                    'num_battery_packs': num_battery_packs,
                    'solar_capacity': solar_capacity,
                    'roi': roi,
                    'annual_profit': annual_profit,
                    'capital_cost': capital_cost,
                })
        else:
            # For a hybrid inverter (with battery), vary the number of battery packs
            for num_battery_packs in [1, 2, 3, 4]:
                for solar_capacity in range(2, 19, 2):
                    roi, annual_profit, capital_cost = compute_roi(num_stations, inverter_type, num_battery_packs, solar_capacity)
                    results_list.append({
                        'num_stations': num_stations,
                        'inverter_type': 1,  # encode hybrid as 1
                        'num_battery_packs': num_battery_packs,
                        'solar_capacity': solar_capacity,
                        'roi': roi,
                        'annual_profit': annual_profit,
                        'capital_cost': capital_cost,
                    })

df = pd.DataFrame(results_list)

# Identify the best configuration based on ROI
best_config = df.loc[df['roi'].idxmax()]

print("All configurations:")
print(df)
print("\nBest configuration based on ROI:")
print(best_config)

# --- (Optional) Regression Analysis for Sensitivity ---
X = df[['num_stations', 'inverter_type', 'num_battery_packs', 'solar_capacity']]
y = df['roi']

model = LinearRegression()
model.fit(X, y)

print("\nRegression Model Coefficients:")
print("Intercept:", model.intercept_)
print("Coefficients:", model.coef_)

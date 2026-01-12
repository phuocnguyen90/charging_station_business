import numpy as np
import pandas as pd
from schemas.simulation import SimulationConfig, SimulationResult

# Constants from app_default could be moved here or kept in config
SOLAR_PANEL_PRICE = 1000 # Benchmark if not provided
INSTALLATION_PRICE = 1000 

class CalculatorService:
    @staticmethod
    def get_electricity_rate(time_in_day: float, day_of_week: int, config: SimulationConfig) -> float:
        """
        Returns the grid electricity cost ($/kWh) for a given time of day.
        """
        if day_of_week == 6: # Sunday
            return config.normal_rate
        
        is_off_peak = time_in_day < 4 or time_in_day >= 22
        is_morning_peak = config.peak_start_morning <= time_in_day < config.peak_end_morning
        is_evening_peak = config.peak_start_evening <= time_in_day < config.peak_end_evening
        
        if is_off_peak:
            return config.off_peak_rate
        elif is_morning_peak or is_evening_peak:
            return config.peak_rate
        else:
            return config.normal_rate

    @staticmethod
    def solar_irradiance(time_in_day: float) -> float:
        if 6 <= time_in_day <= 18:
            return np.sin(np.pi * (time_in_day - 6) / 12)
        else:
            return 0.0

    @staticmethod
    def compute_infrastructure_cost(config: SimulationConfig) -> float:
        # Calculate capital costs based on config
        station_cost = config.charging_station_cost * config.num_stations
        transformer_cost = config.transformer_cost
        
        inverter_unit_cost = config.inverter_cost if config.use_battery else 2000
        inverter_cost = inverter_unit_cost * config.num_stations
        
        battery_cost = 0.0
        if config.use_battery:
            battery_cost = config.battery_pack_price * config.number_of_battery_packs * config.num_stations
            
        # Solar cost calculation from original code seemed to depend on capacity / 10 * price
        # We'll use the provided total solar_panel_cost input as the base unit or calculate?
        # The wizard inputs "Solar Panel Cost ($)" which seems to serve as a unit or total?
        # In wizard.py: config["solar_panel_cost"] = solar_panel_cost (value=2000)
        # In utils.py: solar_cost = (params.get("solar_capacity", 0) / 10) * SOLAR_PANEL_PRICE [if roi constants]
        # or solar_cost = (params.get("solar_capacity", 0) / 10) * 1000 
        
        # Let's assume the input constraint: Cost per 10kW unit roughly
        solar_cost = (config.solar_capacity / 10.0) * config.solar_panel_cost
        install_cost = (config.solar_capacity / 10.0) * config.installation_cost
        
        return station_cost + transformer_cost + solar_cost + inverter_cost + install_cost + battery_cost

    @staticmethod
    def get_usage_profile(profile_type: str = "standard") -> list:
        """
        Returns a list of 24 values summing to 1.0 representing hourly usage distribution.
        """
        if profile_type == "working_9_5":
            # Low day usage, high evening
            p = [0.02]*6 + [0.05]*2 + [0.01]*9 + [0.10]*5 + [0.03]*2
        elif profile_type == "stay_at_home":
            # Consistent usage throughout day
            p = [0.02]*6 + [0.06]*12 + [0.04]*6
        elif profile_type == "night_owl":
            # High night usage
            p = [0.08]*4 + [0.02]*12 + [0.05]*8
        else:
            # Standard / Default POC profile
            p = [0.02]*6   # Hours 0-5: 0.02 each  -> 0.12
            p += [0.06]*4  # Hours 6-9: 0.06 each  -> 0.24
            p += [0.03]*6  # Hours 10-15: 0.03 each -> 0.18
            p += [0.08]*5  # Hours 16-20: 0.08 each -> 0.40
            p += [0.02]*3  # Hours 21-23: 0.02 each -> 0.06
            
        # Normalize just in case
        total = sum(p)
        return [x/total for x in p]

    @staticmethod
    def generate_ev_demand_schedule(config: SimulationConfig, dt: float = 0.5) -> np.ndarray:
        # Note: In a real app, we might mix 'Base Load' (fridge, lights) + 'EV Load'
        # This function currently only generates the EV specific "sessions".
        # We might want to add a base load profile to the simulation.
        steps_per_day = int(24 / dt)
        ev_demand_schedule = np.zeros(steps_per_day)
        
        selected = np.random.choice(
            np.arange(steps_per_day), 
            size=min(config.charging_sessions_per_day, steps_per_day), 
            replace=False
        )
        ev_demand_schedule[selected] = config.charging_station_power * dt
        return ev_demand_schedule

    @staticmethod
    def simulate_day(config: SimulationConfig, seed: int = 42) -> dict:
        np.random.seed(seed)
        dt = 0.5
        steps = int(24 / dt)
        
        # Arrays
        results = {
            "time_arr": np.zeros(steps),
            "battery_soc_arr": np.zeros(steps),
            "grid_import_arr": np.zeros(steps),
            "solar_used_arr": np.zeros(steps),
            "battery_discharged_arr": np.zeros(steps),
            "cost_grid_arr": np.zeros(steps),
            "cost_battery_arr": np.zeros(steps),
            "demand_arr": np.zeros(steps),
            "revenue_arr": np.zeros(steps),
            "solar_total_arr": np.zeros(steps),
            "solar_to_battery_arr": np.zeros(steps),
            "solar_sold_arr": np.zeros(steps)
        }
        
        # setup battery
        battery_capacity = 0.0
        battery_soc = 0.0
        if config.use_battery:
            battery_capacity = config.number_of_battery_packs * (config.battery_pack_Ah * config.battery_pack_voltage / 1000.0)
            battery_soc = config.initial_soc_fraction * battery_capacity
            
        ev_demand_schedule = CalculatorService.generate_ev_demand_schedule(config, dt)
        
        for i in range(steps):
            current_time = i * dt
            time_in_day = current_time % 24
            day_of_week = int(current_time // 24) % 7 # Assumes day 0 is Monday, just simplified
            
            grid_rate = CalculatorService.get_electricity_rate(time_in_day, day_of_week, config)
            
            # Solar
            irr = CalculatorService.solar_irradiance(time_in_day)
            solar_prod = config.solar_capacity * irr * np.random.uniform(1 - config.solar_randomness, 1) * dt
            
            # Demand
            demand = ev_demand_schedule[i]
            
            # Direct Solar Usage
            solar_used = min(solar_prod, demand)
            remaining_demand = demand - solar_used
            leftover_solar = solar_prod - solar_used
            
            # Battery Discharge
            discharged = 0.0
            cost_batt = 0.0
            if remaining_demand > 0 and config.use_battery:
                # Logic from utils.py: discharge_battery_ev
                available_for_discharge = max(battery_soc - 0.2 * battery_capacity, 0)
                max_discharge = config.battery_max_charge_power * dt
                discharged = min(available_for_discharge, remaining_demand, max_discharge)
                battery_soc -= discharged
                cost_batt = discharged * config.battery_degradation_cost
                remaining_demand -= discharged
                
            # Grid Import
            grid_import = remaining_demand
            cost_grid = grid_import * grid_rate
            revenue = demand * config.charging_price
            
            # Charge Battery with Leftover Solar
            charged = 0.0
            if config.use_battery and leftover_solar > 0 and battery_soc < battery_capacity:
                available_space = battery_capacity - battery_soc
                charged = min(leftover_solar * config.inverter_efficiency, available_space)
                battery_soc += charged
                leftover_solar -= (charged / config.inverter_efficiency) # Consumed solar
                
            # Store results
            results["time_arr"][i] = current_time
            results["battery_soc_arr"][i] = battery_soc
            results["grid_import_arr"][i] = grid_import
            results["solar_used_arr"][i] = solar_used
            results["battery_discharged_arr"][i] = discharged
            results["cost_grid_arr"][i] = cost_grid
            results["cost_battery_arr"][i] = cost_batt
            results["demand_arr"][i] = demand
            results["revenue_arr"][i] = revenue
            results["solar_total_arr"][i] = solar_prod
            results["solar_to_battery_arr"][i] = charged
            
        return results

    @staticmethod
    def run_full_simulation(config: SimulationConfig) -> SimulationResult:
        # Run single station simulation
        sim_data = CalculatorService.simulate_day(config)
        
        # Scale by num_stations
        n = config.num_stations
        
        # Aggregate totals (daily)
        total_solar = np.sum(sim_data["solar_total_arr"]) * n
        total_grid = np.sum(sim_data["grid_import_arr"]) * n
        total_revenue = np.sum(sim_data["revenue_arr"]) * n
        total_operating_cost = (np.sum(sim_data["cost_grid_arr"]) + np.sum(sim_data["cost_battery_arr"])) * n
        total_energy = np.sum(sim_data["demand_arr"]) * n
        
        # Annualize
        annual_revenue = total_revenue * 365
        annual_operating_cost = total_operating_cost * 365
        capital_cost = CalculatorService.compute_infrastructure_cost(config)
        # 10 year depreciation roughly
        annual_depreciation = capital_cost / 10.0 
        net_profit = annual_revenue - annual_operating_cost - annual_depreciation
        
        roi = 0.0
        if capital_cost > 0:
            roi = (annual_revenue - annual_operating_cost - annual_depreciation) / capital_cost
            
        roi_metrics = {
             "total_capital_cost": capital_cost,
             "annual_revenue": annual_revenue,
             "annual_operating_cost": annual_operating_cost,
             "net_profit": net_profit,
             "roi": roi,
             "payback_years": capital_cost / (annual_revenue - annual_operating_cost) if (annual_revenue - annual_operating_cost) > 0 else -1
        }
        
        daily = {
            "solar_produced": total_solar,
            "grid_imported": total_grid,
            "revenue": total_revenue
        }
        
        return SimulationResult(
            daily=daily,
            monthly={k: v * 30 for k,v in daily.items()},
            yearly={k: v * 365 for k,v in daily.items()},
            annual_summary=roi_metrics, # duplicative but helpful structure
            roi_metrics=roi_metrics
        )

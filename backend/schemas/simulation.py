from pydantic import BaseModel, Field
from typing import List, Optional

class SimulationConfig(BaseModel):
    # General
    num_stations: int = Field(1, ge=1)
    charging_station_power: float = Field(30.0, description="kW")
    charging_price: float = Field(0.17, description="$/kWh")
    
    # Solar
    solar_capacity: float = Field(20.0, description="kW")
    solar_randomness: float = Field(0.1, ge=0.0, le=1.0)
    
    # Battery
    use_battery: bool = True
    battery_pack_Ah: float = 100.0
    battery_pack_voltage: float = 51.2
    number_of_battery_packs: int = 4
    battery_pack_price: float = 1000.0
    initial_soc_fraction: float = 0.5
    battery_max_charge_power: float = 15.0 # kW
    battery_efficiency: float = 0.9
    battery_degradation_cost: float = 0.05
    
    # Grid / Costs
    inverter_efficiency: float = 0.95
    charging_station_cost: float = 7000.0
    transformer_cost: float = 1000.0
    solar_panel_cost: float = 2000.0
    inverter_cost: float = 3000.0
    installation_cost: float = 1000.0
    
    # Lifetimes
    charging_station_lifetime: float = 10.0
    transformer_lifetime: float = 15.0
    solar_panel_lifetime: float = 25.0
    battery_lifetime: float = 10.0
    inverter_lifetime: float = 10.0
    installation_lifetime: float = 10.0
    
    # Grid Tariffs
    off_peak_rate: float = 0.06
    normal_rate: float = 0.108
    peak_rate: float = 0.188
    peak_start_morning: float = 9.5
    peak_end_morning: float = 11.5
    peak_start_evening: float = 17.0
    peak_end_evening: float = 20.0
    
    # Advanced
    monte_iterations: int = 50
    daily_ev_demand: float = 50.0  # Used in simplified simulations
    charging_sessions_per_day: int = 12

class SimulationResult(BaseModel):
    daily: dict
    monthly: dict
    yearly: dict
    annual_summary: dict
    roi_metrics: dict

# localization.py

UI_TEXTS = {
    "EN": {
        "title": "EV Charging Station Cost, Solar & ROI Simulation",
        "description": """
This tool simulates the cost-effectiveness of an EV charging station under various configurations.

**Features include:**
- Detailed simulation with solar production, battery integration, and grid tariffs.
- A Solar Report for Buon Ma Thuot, Vietnam.
- ROI analysis across different design configurations.
- Explanations of the underlying math and formulas via hover-help.
""",
        "sidebar": {
            "simulation_settings": "Simulation Settings",
            "simulation_duration": "Simulation Duration (Days)",
            "simulation_duration_help": "The number of days to simulate (affects depreciation and energy totals).",
            "average_charging_sessions": "Average Charging Sessions per Day",
            "average_charging_sessions_help": "Each session delivers (Charging Power x 0.5 hr) kWh.",
            "num_stations": "Number of Charging Stations",
            "num_stations_help": "Number of charging stations or ports.",
            "charging_station_power": "Charging Station Power (kW)",
            "charging_station_power_help": "Rated power of each charging station.",
            "charging_price": "Charging Price ($/kWh)",
            "charging_price_help": "Price charged to EV customers per kWh.",
            "use_battery": "Use Battery",
            "use_battery_help": "Enable battery integration for load management.",
            "solar_settings": "Solar Settings",
            "solar_panel_capacity": "Solar Panel Capacity (kW)",
            "solar_panel_capacity_help": "Installed capacity of the solar panels.",
            "solar_variability": "Solar Variability (Fraction)",
            "solar_variability_help": "Represents variability in solar output (e.g., due to clouds).",
            "battery_pack_configuration": "Battery Pack Configuration",
            "battery_pack_capacity": "Battery Pack Capacity (Ah)",
            "battery_pack_capacity_help": "Capacity of one battery pack in Ampere-hours.",
            "battery_pack_voltage": "Battery Pack Voltage (V)",
            "battery_pack_voltage_help": "Voltage of one battery pack.",
            "battery_pack_price": "Battery Pack Price ($)",
            "battery_pack_price_help": "Cost per battery pack.",
            "num_battery_packs": "Number of Battery Packs Installed",
            "num_battery_packs_help": "Total number of battery packs installed.",
            "initial_battery_soc": "Initial Battery SoC (Fraction)",
            "initial_battery_soc_help": "Initial state-of-charge as a fraction of total battery capacity.",
            "battery_max_charge_rate": "Battery Max Charge/Discharge Rate (C)",
            "battery_max_charge_rate_help": "Maximum charging rate as a fraction of battery capacity.",
            "battery_inverter_performance": "Battery & Inverter Performance",
            "battery_round_trip_efficiency": "Battery Round-Trip Efficiency",
            "battery_round_trip_efficiency_help": "Efficiency during a full charge/discharge cycle.",
            "inverter_efficiency": "Inverter Efficiency",
            "inverter_efficiency_help": "Efficiency of converting DC (solar) to AC when charging the battery.",
            "battery_degradation_cost": "Battery Degradation Cost ($/kWh discharged)",
            "battery_degradation_cost_help": "Cost associated with battery wear per kWh discharged.",
            "grid_price_threshold": "Grid Price Threshold for Battery Use ($/kWh)",
            "grid_price_threshold_help": "If the grid tariff exceeds this value, battery discharge is used.",
            "capital_costs_lifetimes": "Capital Costs & Lifetimes",
            "charging_station_cost": "Charging Station Cost ($)",
            "charging_station_cost_help": "Capital cost for the charging station.",
            "transformer_cost": "Transformer Cost ($)",
            "transformer_cost_help": "Cost of any required transformer.",
            "solar_panel_cost": "Solar Panel Cost ($)",
            "solar_panel_cost_help": "Cost for solar panel installation.",
            "inverter_cost": "Inverter Cost ($)",
            "inverter_cost_help": "Cost of the inverter (use lower cost if battery not used).",
            "installation_cost": "Installation & Other Costs ($)",
            "installation_cost_help": "Other installation-related costs.",
            "charging_station_lifetime": "Charging Station Lifetime (Years)",
            "charging_station_lifetime_help": "Expected lifetime of the charging station.",
            "transformer_lifetime": "Transformer Lifetime (Years)",
            "transformer_lifetime_help": "Expected lifetime of the transformer.",
            "solar_panel_lifetime": "Solar Panel Lifetime (Years)",
            "solar_panel_lifetime_help": "Expected lifetime of the solar panels.",
            "battery_lifetime": "Battery Lifetime (Years)",
            "battery_lifetime_help": "Expected lifetime of the battery system.",
            "inverter_lifetime": "Inverter Lifetime (Years)",
            "inverter_lifetime_help": "Expected lifetime of the inverter.",
            "installation_lifetime": "Installation Lifetime (Years)",
            "installation_lifetime_help": "Lifetime over which installation costs are amortized.",
            "monte_carlo": "Monte Carlo Simulation",
            "monte_carlo_iterations": "Monte Carlo Iterations",
            "monte_carlo_iterations_help": "Number of iterations for Monte Carlo simulation."
        },
        "tabs": {
            "main_report": "Main Report",
            "solar_report": "Solar Report",
            "roi_analysis": "ROI Analysis",
            "charging_cost": "Charging Cost"
        },
        "tab1": {
            "header": "Overview – Annual Expected Returns, Costs, and Payback Period",
            "annual_summary_metrics": "Annual Summary Metrics",
            "annual_energy": "Annual Energy Delivered",
            "annual_revenue": "Annual Revenue",
            "annual_operating_cost": "Annual Operating Cost",
            "effective_cost_per_kwh": "Effective Cost ($/kWh)",
            "annual_capital_cost": "Annual Capital Cost",
            "net_annual_profit": "Net Annual Profit",
            "total_initial_capital_cost": "Total Initial Capital Cost",
            "annual_cash_flow": "Annual Cash Flow (Revenue - Operating Cost)",
            "minimum_payback_period": "Minimum Payback Period",
            "operating_cost_tooltip_title": "Calculation Details:",
            "operating_cost_tooltip": """
The Annual Operating Cost is calculated by annualizing the total operational cost incurred during the simulation period. This cost includes:
- Grid Import Charges (based on time-of-use tariffs)
- Battery Degradation Costs (if applicable)

The cost is scaled to an annual value using the formula:
**Total Operational Cost × (365 / Simulation Days)**
"""
        }
    },
    "VI": {
        "title": "Mô phỏng chi phí đầu tư Trạm sạc EV",
        "description": """
Công cụ này mô phỏng hiệu quả chi phí của trạm sạc EV với các cấu hình khác nhau.

**Các tính năng bao gồm:**
- Mô phỏng chi tiết với sản lượng năng lượng mặt trời, tích hợp pin lưu trữ, và cước phí điện lưới.
- Báo cáo năng lượng mặt trời cho Buôn Ma Thuột, Việt Nam.
- Phân tích ROI theo các cấu hình thiết kế khác nhau.
- Giải thích các phép tính và công thức thông qua trợ giúp khi di chuột.
""",
        "sidebar": {
            "simulation_settings": "Cài đặt Mô phỏng",
            "simulation_duration": "Thời gian mô phỏng (Ngày)",
            "simulation_duration_help": "Số ngày mô phỏng (ảnh hưởng đến khấu hao và tổng năng lượng).",
            "average_charging_sessions": "Số phiên sạc trung bình mỗi ngày",
            "average_charging_sessions_help": "Điện năng sử dụng cho mỗi phiên sạc kéo dài 30 phút: (Công suất sạc × 0.5 giờ) kWh.",
            "num_stations": "Số trạm sạc",
            "num_stations_help": "Số trạm sạc hoặc cổng sạc.",
            "charging_station_power": "Công suất Trạm sạc (kW)",
            "charging_station_power_help": "Công suất định mức của mỗi trạm sạc.",
            "charging_price": "Giá sạc ($/kWh)",
            "charging_price_help": "Giá tính cho khách hàng EV theo kWh.",
            "use_battery": "Sử dụng Pin",
            "use_battery_help": "Bật tích hợp pin lưu trữ để quản lý tải.",
            "solar_settings": "Cài đặt Năng lượng Mặt trời",
            "solar_panel_capacity": "Công suất tấm pin mặt trời (kW)",
            "solar_panel_capacity_help": "Công suất lắp đặt của tấm pin mặt trời.",
            "solar_variability": "Độ biến động của năng lượng mặt trời (Phần trăm)",
            "solar_variability_help": "Biểu thị độ biến động của sản lượng năng lượng mặt trời (ví dụ: do mây che).",
            "battery_pack_configuration": "Cấu hình Pin lưu trữ",
            "battery_pack_capacity": "Dung lượng Pin lưu trữ (Ah)",
            "battery_pack_capacity_help": "Dung lượng của một Pin lưu trữ (Ampere-hour).",
            "battery_pack_voltage": "Điện áp Pin lưu trữ (V)",
            "battery_pack_voltage_help": "Điện áp của một Pin lưu trữ.",
            "battery_pack_price": "Giá Pin lưu trữ ($)",
            "battery_pack_price_help": "Giá mỗi Pin lưu trữ.",
            "num_battery_packs": "Số lượng Pin lưu trữ cài đặt",
            "num_battery_packs_help": "Tổng số Pin lưu trữ được cài đặt.",
            "initial_battery_soc": "Trạng thái sạc ban đầu (Phần trăm)",
            "initial_battery_soc_help": "Mức sạc ban đầu của pin dưới dạng phần trăm dung lượng tối đa.",
            "battery_max_charge_rate": "Tốc độ sạc/xả tối đa của Pin (C)",
            "battery_max_charge_rate_help": "Tốc độ sạc/xả tối đa dưới dạng phần trăm dung lượng pin (ví dụ: 0.5 nghĩa là pin được sạc/xả ở 50% dung lượng mỗi giờ).",
            "battery_inverter_performance": "Hiệu suất của Pin & Bộ Inverter",
            "battery_round_trip_efficiency": "Hiệu suất vòng đầy của Pin",
            "battery_round_trip_efficiency_help": "Hiệu suất trong quá trình sạc và xả đầy.",
            "inverter_efficiency": "Hiệu suất của Bộ Inverter",
            "inverter_efficiency_help": "Hiệu suất chuyển đổi từ DC (năng lượng mặt trời) sang AC khi sạc pin.",
            "battery_degradation_cost": "Chi phí hao mòn Pin ($/kWh xả)",
            "battery_degradation_cost_help": "Chi phí liên quan đến hao mòn pin mỗi kWh xả ra.",
            "grid_price_threshold": "Ngưỡng giá điện lưới ($/kWh)",
            "grid_price_threshold_help": "Nếu giá điện lưới vượt quá giá trị này, pin sẽ được xả ra.",
            "capital_costs_lifetimes": "Chi phí vốn & Tuổi thọ",
            "charging_station_cost": "Chi phí Trạm sạc ($)",
            "charging_station_cost_help": "Chi phí đầu tư cho trạm sạc.",
            "transformer_cost": "Chi phí Máy biến áp ($)",
            "transformer_cost_help": "Chi phí của máy biến áp nếu cần.",
            "solar_panel_cost": "Chi phí Tấm pin mặt trời ($)",
            "solar_panel_cost_help": "Chi phí lắp đặt tấm pin mặt trời.",
            "inverter_cost": "Chi phí Bộ Inverter ($)",
            "inverter_cost_help": "Chi phí của bộ inverter (nếu không sử dụng pin, dùng giá thấp hơn).",
            "installation_cost": "Chi phí Lắp đặt & khác ($)",
            "installation_cost_help": "Chi phí lắp đặt và các chi phí khác.",
            "charging_station_lifetime": "Tuổi thọ Trạm sạc (Năm)",
            "charging_station_lifetime_help": "Tuổi thọ dự kiến của trạm sạc.",
            "transformer_lifetime": "Tuổi thọ Máy biến áp (Năm)",
            "transformer_lifetime_help": "Tuổi thọ dự kiến của máy biến áp.",
            "solar_panel_lifetime": "Tuổi thọ Tấm pin mặt trời (Năm)",
            "solar_panel_lifetime_help": "Tuổi thọ dự kiến của tấm pin mặt trời.",
            "battery_lifetime": "Tuổi thọ của Pin (Năm)",
            "battery_lifetime_help": "Tuổi thọ dự kiến của hệ thống pin.",
            "inverter_lifetime": "Tuổi thọ của Bộ Inverter (Năm)",
            "inverter_lifetime_help": "Tuổi thọ dự kiến của bộ inverter.",
            "installation_lifetime": "Tuổi thọ của Lắp đặt (Năm)",
            "installation_lifetime_help": "Thời gian khấu hao của các chi phí lắp đặt.",
            "monte_carlo": "Mô phỏng Monte Carlo",
            "monte_carlo_iterations": "Số lượt mô phỏng Monte Carlo",
            "monte_carlo_iterations_help": "Số lần chạy mô phỏng Monte Carlo."
        },
        "tabs": {
            "main_report": "Báo cáo tổng quan",
            "solar_report": "Báo cáo năng lượng mặt trời",
            "roi_analysis": "Phân tích ROI",
            "charging_cost": "Chi phí sạc"
        },
        "tab1": {
            "header": "Tổng quan – Năng suất, Chi phí hàng năm và Thời gian hoàn vốn",
            "annual_summary_metrics": "Các chỉ số tóm tắt hàng năm",
            "annual_energy": "Lượng điện bán được hàng năm",
            "annual_revenue": "Doanh thu hàng năm",
            "annual_operating_cost": "Chi phí hoạt động hàng năm",
            "effective_cost_per_kwh": "Chi phí thực tế trung bình mỗi kWh",
            "annual_capital_cost": "Chi phí vốn hàng năm",
            "net_annual_profit": "Lợi nhuận ròng hàng năm",
            "total_initial_capital_cost": "Tổng chi phí đầu tư ban đầu",
            "annual_cash_flow": "Dòng tiền hàng năm (Doanh thu - Chi phí vận hành)",
            "minimum_payback_period": "Thời gian hoàn vốn tối thiểu",
            "operating_cost_tooltip_title": "Chi tiết Tính toán:",
            "operating_cost_tooltip": """
Chi phí hoạt động hàng năm được tính bằng cách quy đổi chi phí hoạt động tổng cộng phát sinh trong khoảng thời gian mô phỏng sang giá trị hàng năm. Chi phí này bao gồm:
- Phí mua điện lưới (dựa trên cước phí theo giờ)
- Chi phí hao mòn pin (nếu áp dụng)
  
Chi phí được quy đổi hàng năm theo công thức:
**Chi phí hoạt động tổng cộng × (365 / Số ngày mô phỏng)**
"""
        }
    }
}

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
            "monte_carlo_iterations_help": "Number of iterations for Monte Carlo simulation.",
            "advanced_settings": "Advanced settings",
            "selling_excess_checkbox":"Selling excess energy",
            "selling_excess_checkbox_help":"If checked, excess energy is sold back to the grid at the selling price. If not checked, excess energy is used to charge the battery.",
            "selling_excess_price":"Selling price ($/kWh)",
            "selling_excess_price_help":"The price at which excess energy is sold back to the grid. Only applicable if selling excess energy is checked.",
            "selling_percentage":"Selling percentage",
            "selling_percentage_help":"The percentage of excess energy that is sold back to the grid. Only applicable if selling excess energy is checked.",
            "grid_import_tariff_normal": "Grid Import Tariff ($/kWh)",
            "grid_import_tariff_normal_help": "The price charged by the grid for energy imported from the grid",
            "grid_import_tariff_peak": "Grid Import Tariff Peak ($/kWh)",
            "grid_import_tariff_peak_help": "The price charged by the grid for peak energy imported from the grid",
            "grid_import_tariff_offpeak": "Grid Import Tariff Off-Peak ($/kWh)",
            "grid_import_tariff_offpeak_help": "The price charged by the grid for off-peak energy imported from the grid",
            "grid_export_tariff": "Grid Export Tariff ($/kWh)",
            "grid_export_tariff_help": "The price charged by the grid for energy exported to the grid",
            "morning_peak_hour_start": "Morning Peak Start",
            "morning_peak_hour_start_help": "The hour of the day when peak energy is expected",
            "morning_peak_hour_end": "Morning Peak End",
            "morning_peak_hour_end_help": "The hour of the day when peak energy is expected",
            "evening_peak_hour_start": "Evening Peak Start",
            "evening_peak_hour_start_help": "The hour of the day when off-peak energy is expected",
            "evening_peak_hour_end": "Evening Peak End",
            "evening_peak_hour_end_help": "The hour of the day when off-peak energy is expected",


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
            "effective_cost_per_kwh": "Effective Cost per kWh used",
            "effective_cost_per_kwh_tooltip":"Average cost from utilizing from grid during off-peak hours, use solar directly, use battery",
            "annual_capital_cost": "Annual Capital Cost",
            "net_annual_profit": "Net Annual Profit",
            "total_initial_capital_cost": "Total Initial Capital Cost",
            "annual_cash_flow": "Annual Cash Flow (Revenue - Operating Cost)",
            "minimum_payback_period": "Minimum Payback Period",
            "operating_cost_tooltip_title": "Calculation Details:",
            "operating_cost_tooltip": """
                The Annual Operating Cost is calculated by annualizing the total operational cost incurred during the simulation period. This cost includes:
                </p>
                <ul>
                    <li>Grid Import Charges (based on time-of-use tariffs)</li>
                    <li>Battery Degradation Costs (if applicable)</li>
                </ul>
                <p>
                    The cost is scaled to an annual value using the formula: Total Operational Cost × (365 / Simulation Days)
                </p>
                """,
            "investment_cash_flow_overview": "Investment & Cash Flow Overview",
            "payback_analysis": "Payback Analysis",
            "payback_period": "Payback Period",
            "payback_not_achievable": "Payback period not achievable",
            "years_with_inflation": "years with 5% inflation",
            "component_contribution_analysis": "Effective cost projection",
            "grid_only": "Grid Only",
            "grid_and_solar": "Grid and Solar",
            "grid_and_solar_and_battery": "Grid and Solar and Battery",
            "waterfall_chart_title":"Effective cost comparison",
            "overview_explanation": """
                ### Overview Explanation

                The report is divided into several main sections that provide a comprehensive view of the project's performance:

                1. **Annual Summary**
                - **Annual Energy Output (`annual_energy`)**: The total kWh delivered to charging customers during the simulation period.

                - **Annual Revenue**: Calculated by multiplying the annual energy output by the `charging_price`.

                - **Annual Operating Cost (`annual_operating_cost`)**: Includes costs such as grid electricity and battery degradation costs.

                - **Annual Capital Cost (`annual_capital_cost`)**: Calculated by amortizing capital investments (e.g. `station_cost`, `inverter_cost`, `solar_panel_cost`, `installation_cost` and, if applicable, `battery_cost`) over their respective lifetimes.

                - **Net profit (`net_profit`)**: Annual revenue minus total operating and capital costs.

                2. **Overview of investment and cash flow**
                - **Total initial capital cost**: The sum of individual component costs, such as:

                - **Charging station cost (`station_cost`)**: Cost per station multiplied by the number of stations.

                - **Inverter cost (`inverter_cost`)**.

                - **Battery storage cost (`battery_cost`)**: If `use_battery` is false, an assumed value (e.g. \$5000 per pack/charging station) will be used.

                - **Solar panel cost (`solar_cost`)** and **Installation cost (`installation_cost`)**.
                - **Annual Cash Flow**: The difference between annual revenue and annual operating costs.

                3. **Payback Period Analysis**
                - Calculate the number of years it will take to recover the total initial capital cost (excluding depreciation).

                - Use an annual inflation rate (e.g. 5%) to adjust the annual cash flows.

                - The payback period is determined by adding the adjusted annual cash flows until they equal or exceed the total cost of capital.

                4. **Average Electricity Price Analysis**
                - **Grid-Only Scenario**: The basic effective cost per kWh.

                - **Grid-Only Scenario**: The effective cost per kWh when using a solar system.

                - **Solar + Storage Scenario**: The effective cost per kWh when adding a battery system.

                - If `use_battery` is unchecked, the assumed battery cost will be **estimated at \$5000 per unit/charger**, calculated annually over the battery life and added to the solar-only capital cost.

                - This comparison shows how each investment component affects the effective electricity cost.

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
            "solar_panel_capacity": "Công suất dàn pin mặt trời (kW)",
            "solar_panel_capacity_help": "Công suất lắp đặt của toàn bộ dàn pin mặt trời.",
            "solar_variability": "Độ biến động của năng lượng mặt trời (Phần trăm)",
            "solar_variability_help": "Biểu thị độ biến động của sản lượng năng lượng mặt trời (ví dụ: do mây che).",
            "battery_pack_configuration": "Cấu hình Pin lưu trữ",
            "battery_pack_capacity": "Dung lượng Pin lưu trữ (Ah)",
            "battery_pack_capacity_help": "Dung lượng của một Pin lưu trữ (Ampere-hour).",
            "battery_pack_voltage": "Điện áp Pin lưu trữ (V)",
            "battery_pack_voltage_help": "Điện áp của một Pin lưu trữ.",
            "battery_pack_price": "Giá Pin lưu trữ (đ)",
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
            "charging_station_cost": "Chi phí Trạm sạc (đ)",
            "charging_station_cost_help": "Chi phí đầu tư cho trạm sạc.",
            "transformer_cost": "Chi phí Máy biến áp (đ)",
            "transformer_cost_help": "Chi phí của máy biến áp nếu cần.",
            "solar_panel_cost": "Chi phí Tấm pin mặt trời (đ)",
            "solar_panel_cost_help": "Chi phí lắp đặt tấm pin mặt trời.",
            "inverter_cost": "Chi phí Bộ Inverter (đ)",
            "inverter_cost_help": "Chi phí của bộ inverter (nếu không sử dụng pin, dùng giá thấp hơn).",
            "installation_cost": "Chi phí Lắp đặt & khác (đ)",
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
            "monte_carlo_iterations_help": "Số lần chạy mô phỏng Monte Carlo.",
            "advanced_settings": "Cài đặt nâng cao",
            "selling_excess_checkbox":"Bán năng lượng dư thừa",
            "selling_excess_checkbox_help":"Nếu được chọn, năng lượng dư thừa sẽ được bán lại cho lưới điện với giá bán. Nếu không được chọn, năng lượng dư thừa sẽ được sử dụng để sạc pin hoặc không tiêu thụ",
            "selling_excess_price":"Giá bán (đ/kWh)",
            "selling_excess_price_help":"Giá mà năng lượng dư thừa được bán lại cho lưới điện. Chỉ áp dụng nếu chọn bán năng lượng dư thừa",
            "selling_percentage":"Tỷ lệ phần trăm bán",
            "selling_percentage_help":"Tỷ lệ phần trăm năng lượng dư thừa được bán lại cho lưới điện. Chỉ áp dụng nếu chọn bán năng lượng dư thừa",
            "grid_import_tariff_normal": "Giá nhập khẩu lưới điện bình thường (đ/kWh)",
            "grid_import_tariff_normal_help": "Giá mà lưới điện tính cho năng lượng nhập khẩu từ lưới điện",

            "grid_import_tariff_peak": "Giá nhập khẩu lưới điện cao điểm (đ/kWh)",
            "grid_import_tariff_peak_help": "Giá do lưới tính cho năng lượng đỉnh nhập khẩu từ lưới",
            "grid_import_tariff_offpeak": "Giá nhập khẩu lưới ngoài giờ cao điểm (đ/kWh)",
            "grid_import_tariff_offpeak_help": "Giá do lưới tính cho năng lượng ngoài giờ cao điểm nhập khẩu từ lưới",
            "grid_export_tariff": "Giá bán cho điện lưới ($/kWh)",
            "grid_export_tariff_help": "Giá do lưới tính cho năng lượng xuất khẩu vào lưới",
            "morning_peak_hour_start": "Giờ bắt đầu giờ cao điểm buổi sáng",
            "morning_peak_hour_start_help": "Giờ trong ngày dự kiến ​​đạt năng lượng đỉnh",
            "morning_peak_hour_end": "Giờ kết thúc giờ cao điểm buổi sáng",
            "morning_peak_hour_end_help": "Giờ giờ trong ngày khi dự kiến ​​đạt năng lượng cao điểm",
            "evening_peak_hour_start": "Bắt đầu giờ cao điểm buổi tối",
            "evening_peak_hour_start_help": "Giờ trong ngày khi dự kiến ​​đạt năng lượng ngoài giờ cao điểm",
            "evening_peak_hour_end": "Kết thúc giờ cao điểm buổi tối",
            "evening_peak_hour_end_help": "Giờ trong ngày khi dự kiến ​​đạt năng lượng ngoài giờ cao điểm",
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
            "effective_cost_per_kwh": "Chi phí ước tính trung bình mỗi kWh",
            "effective_cost_per_kwh_tooltip":"Chi phí này được tính bằng mức trung bình thông qua việc kết hợp nạp từ điện lưới lúc thấp điểm, sử dụng năng lượng mặt trời và hệ thống pin",
            "annual_capital_cost": "Chi phí khấu hao hàng năm",
            "net_annual_profit": "Lợi nhuận ròng hàng năm",
            "total_initial_capital_cost": "Tổng chi phí đầu tư ban đầu",
            "annual_cash_flow": "Dòng tiền hàng năm (Doanh thu - Chi phí vận hành)",
            "minimum_payback_period": "Thời gian hoàn vốn tối thiểu",
            "investment_cash_flow_overview": "Vốn đầu tư và dòng tiền hàng năm",
            "payback_analysis": "Thời gian hoàn vốn tối thiểu",
            "payback_period": "Thời gian hoàn vốn",
            "payback_not_achievable": "Không thể hoàn vốn",
            "years_with_inflation": "năm với lạm phát 5%.",
            "component_contribution_analysis": "Ước tính chi phí điện",
            "grid_only": "Chỉ điện lưới",
            "grid_and_solar": "NLMT bám tải",
            "grid_and_solar_and_battery": "NLMT lưu trữ",
            "waterfall_chart_title":"So sánh chi phí điện",
            "overview_explanation": """
                ### Tổng quan Giải thích

                Báo cáo được chia thành một số phần chính cung cấp góc nhìn toàn diện về hiệu suất của dự án:

                1. **Tóm tắt hàng năm**
                - **Sản lượng năng lượng hàng năm (`annual_energy`)**: Tổng số kWh được cung cấp cho khách hàng đến sạc trong suốt thời gian mô phỏng.
                - **Doanh thu hàng năm**: Được tính bằng cách nhân sản lượng năng lượng hàng năm với `charging_price`.
                - **Chi phí vận hành hàng năm (`annual_operating_cost`)**: Bao gồm các chi phí như điện lưới và chi phí xuống cấp pin.
                - **Chi phí vốn hàng năm (`annual_capital_cost`)**: Được tính bằng cách khấu hao các khoản đầu tư vốn (ví dụ: `station_cost`, `inverter_cost`, `solar_panel_cost`, `installation_cost` và, nếu có, `battery_cost`) trong suốt thời gian sử dụng tương ứng của chúng.
                - **Lợi nhuận ròng (`net_profit`)**: Doanh thu hàng năm trừ đi tổng chi phí hoạt động và chi phí vốn.

                2. **Tổng quan về đầu tư và dòng tiền**
                - **Tổng chi phí vốn ban đầu**: Tổng chi phí thành phần riêng lẻ, chẳng hạn như:
                - **Chi phí trạm sạc (`station_cost`)**: Chi phí cho mỗi trạm nhân với số lượng trạm.
                - **Chi phí biến tần (`inverter_cost`)**.
                - **Chi phí pin lưu trữ (`battery_cost`)**: Nếu `use_battery` là sai, một giá trị giả định (ví dụ: \$5000 cho mỗi gói/trạm sạc) sẽ được sử dụng.
                - **Chi phí tấm pin năng lượng mặt trời (`solar_cost`)** và **Chi phí lắp đặt (`installation_cost`)**.
                - **Dòng tiền hàng năm**: Chênh lệch giữa doanh thu hàng năm và chi phí vận hành hàng năm.

                3. **Phân tích thời gian hoàn vốn**
                - Tính toán số năm cần thiết để thu hồi tổng chi phí vốn ban đầu (không trừ khoản khấu hao).
                - Sử dụng tỷ lệ lạm phát hàng năm (ví dụ: 5%) để điều chỉnh dòng tiền hàng năm.
                - Thời gian hoàn vốn được xác định bằng cách cộng dồn các dòng tiền hàng năm đã điều chỉnh cho đến khi chúng bằng hoặc vượt quá tổng chi phí vốn.

                4. **Phân tích giá điện bình quân**
                - **Kịch bản chỉ sử dụng điện lưới**: Chi phí hiệu quả cơ bản cho mỗi kWh.
                - **Kịch bản chỉ sử dụng NLMT hòa lưới bám tải**: Chi phí hiệu quả cho mỗi kWh khi sử dụng hệ thống năng lượng mặt trời.
                - **Kịch bản NLMT + lưu trữ**: Chi phí hiệu quả cho mỗi kWh khi thêm hệ thống pin.
                - Nếu `use_battery` không được đánh dấu, chi phí pin giả định sẽ được **ước tính là \$5000 cho mỗi bộ/trạm sạc)**, được tính theo năm trong suốt thời gian sử dụng pin và được cộng vào chi phí vốn chỉ có năng lượng mặt trời.
                - So sánh này cho thấy từng thành phần đầu tư ảnh hưởng như thế nào đến chi phí điện hiệu quả.       
            """,
            "operating_cost_tooltip_title": "Chi tiết Tính toán:",
            "operating_cost_tooltip": """
             
                Chi phí hoạt động hàng năm được tính bằng cách quy đổi chi phí hoạt động tổng cộng phát sinh trong khoảng thời gian mô phỏng sang giá trị hàng năm. Chi phí này bao gồm:
                <ul>
                <li>- Phí mua điện lưới (dựa trên cước phí theo giờ)</li>
                <li>- Chi phí hao mòn pin (nếu áp dụng)</li>
                </ul>
                <p> Chi phí được quy đổi hàng năm theo công thức:
                <b>Chi phí hoạt động tổng cộng × (365 / Số ngày mô phỏng)</b></p>
                """
        }
    }
}

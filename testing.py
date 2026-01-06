import time
from datetime import datetime
import webbrowser
from Test_Log_Generator import HTMLTestReport, create_scatter_plot_example, create_line_plot_example, create_histogram_plot_example

# Example usage
if __name__ == "__main__":

    url = r'file:///C:/Users/Zacha/Documents/GitHub/pyTestLogs/test_report.html'

    # Create a new report with sticky header, version badge, and collapsible sections
    report = HTMLTestReport(
        title="Voyager 1088 - PIA2 PreTest",
        sticky_header=True,  # Set to False if you don't want sticky header
        version="0.1.2",  # Test script version - determines gradient colors
        collapsible=True,  # Enable collapsible sections
        test_log_path=r'C:/Users/Zacha/Documents/GitHub/pyTestLogs/'
    )

    # Add banner items
    report.add_header_item("Serial Number", "SN-2024-001234")
    report.add_header_item("Serial Number", "SN-2024-001234")
    report.add_header_item("Serial Number", "SN-2024-001234")
    report.add_header_item("Serial Number", "SN-2024-001234")
    report.add_header_item("Test Date", datetime.now().strftime("%B %d, %Y %I:%M %p"))
    report.add_header_item("Operator", "John Doe")
    report.add_header_item("Test Station", "Station 3")

    # Example 1: Section starts with default "running" status and progress bar
    # Category "running" gives it blue color to match status badge
    report.start_section("Power Supply Tests", collapsed=True)
    report.add_line("Testing 3.3V rail...")
    report.add_line("Measured voltage: 3.31V (within tolerance)")
    report.update_section_progress("Power Supply Tests", 33)  # Update to 33%

    report.add_line("Testing 5V rail...")
    report.add_line("Measured voltage: 5.02V (within tolerance)")
    report.update_section_progress("Power Supply Tests", 66)  # Update to 66%

    report.add_line_break()
    report.add_line("Testing 12V rail...")
    report.add_line("Measured voltage: 12.01V (within tolerance)")
    report.end_section(status = 'pass')

    # Example 2: Section with status badge (collapsed, failed)
    report.start_section("Voltage Measurements", collapsed=True)
    report.add_table(
        headers=["Rail", "Nominal (V)", "Tolerance (V)", "Measured (V)"],
        rows=[],
        title="Power Rail Test Results",
        category="fail",  # Red table headers to match fail status
        measured_col="Measured (V)",
        nominal_col="Nominal (V)",
        tolerance_col="Tolerance (V)"
    )

    # Add rows dynamically - pass/fail will be auto-calculated and colored
    report.add_table_row(["3.3V", "3.30", "0.10", "3.31"])
    report.add_table_row(["5.0V", "5.00", "0.25", "5.02"])
    report.add_table_row(["12.0V", "12.00", "0.50", "11.20"])  # Will show as FAIL
    report.add_table_row(["-5.0V", "-5.00", "0.25", "-5.01"])
    report.end_section(status = 'fail')


    # Example 3: Section with "pass" category that ends with "pass" status
    report.start_section("Current Measurements", collapsed=True)  # Starts as "running"
    report.add_table(
        headers=["Test Point", "Lower Spec (A)", "Upper Spec (A)", "Measured (A)"],
        rows=[
            ["Load 1", "0.90", "1.10", "0.98"],  # PASS
            ["Load 2", "1.80", "2.20", "2.05"],  # PASS
            ["Load 3", "0.45", "0.55", "0.51"],  # PASS
        ],
        title="Current Consumption Tests",
        category="pass",  # Green table headers to match pass status
        measured_col="Measured (A)",
        lower_spec_col="Lower Spec (A)",
        upper_spec_col="Upper Spec (A)"
    )
    report.end_section(status = 'warning')

    # Example 4: Section with "warning" category and status (collapsed)
    report.start_section("Communication Tests", collapsed=True)
    report.add_line("I2C bus scan: 4 devices found")
    report.add_line("SPI flash ID: 0xEF4018")
    report.add_line("UART loopback test: MARGINAL")
    report.end_section(status='pass')

    # Example 5: Section with fail status
    report.start_section("Temperature Tests")
    report.add_table(
        headers=["Sensor", "Lower Limit (°C)", "Upper Limit (°C)", "Measured (°C)"],
        rows=[
            ["CPU", "20", "85", "72"],
            ["Ambient", "15", "40", "28"],
            ["Power Supply", "20", "70", "95"],  # FAIL
        ],
        title="Temperature Readings",
        category="temperature",
        measured_col="Measured (°C)",
        lower_spec_col="Lower Limit (°C)",
        upper_spec_col="Upper Limit (°C)"
    )
    report.end_section(status = 'data')

    # Add matplotlib plots section (collapsed, pass status)
    try:
        report.start_section("Data Visualization", collapsed=True)

        scatter_light, scatter_dark = create_scatter_plot_example()
        report.add_dual_plot(scatter_light, scatter_dark,
                             title="Figure 1: Scatter plot showing correlation between variables")

        line_light, line_dark = create_line_plot_example()
        report.add_dual_plot(line_light, line_dark,
                             title="Figure 2: Line plot showing signal waveforms over time")

        hist_light, hist_dark = create_histogram_plot_example()
        report.add_dual_plot(hist_light, hist_dark,
                             title="Figure 3: Histogram showing distribution of measured values")

        report.end_section(status = 'pass')

    except ImportError:
        report.start_section("Data Visualization")
        report.add_line("⚠️ Matplotlib not available - cannot generate plots", status="warning")
        report.end_section()

    # Save the report
    report.save("test_report.html")
    print("\nExample report generated successfully!")
    print("Open 'test_report.html' in a browser to view the report.")
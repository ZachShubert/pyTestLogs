"""
HTML Test Report Generator Library
Generates professional HTML test reports with dark/light mode support
Compatible with PyQt6 browser and Jupyter notebooks
"""

import base64
from datetime import datetime
from typing import List, Dict, Optional, Union
import io
import matplotlib.pyplot as plt
import numpy as np
import webbrowser


class HTMLTestReport:
    """
    A library for generating professional HTML test reports line by line.
    Supports banners, headers, sections, tables, plots, and more.
    """

    def __init__(self, title: str = "Test Report", sticky_header: bool = False, version: Optional[str] = None, test_log_path: str = None, collapsible: bool = False):
        """
        Initialize a new HTML test report.

        :param title: Report title displayed in banner
        :type title: str
        :param sticky_header: Keep banner fixed when scrolling
        :type sticky_header: bool
        :param version: Version string "major.minor.patch" for color gradients
        :type version: str, optional
        :param test_log_path: Path to test log directory for footer link
        :type test_log_path: str, optional
        :param collapsible: Enable collapsible sections
        :type collapsible: bool

        .. versionadded:: 1.0.0
        """
        self.title = title
        self.sticky_header = sticky_header
        self.version = version
        self.collapsible = collapsible
        self.test_log_path = test_log_path
        self.lines = []
        self.last_table_index = None  # Track the last table position
        self.last_table_specs = None  # Track spec columns for auto pass/fail
        self.header_items = []  # Store banner items
        self.footer_class = 'no-version'  # Will be set in _init_html
        self.section_counter = 0  # Track section IDs for collapsible functionality
        self._init_html()
        self.current_section_title = None

    def _init_html(self):
        """Initialize the HTML document with styles and header."""
        sticky_class = ' sticky' if self.sticky_header else ''

        # Determine classes and gradients based on version
        banner_gradient = ''
        footer_gradient = ''
        banner_class = 'no-version'
        footer_class = 'no-version'

        # Build version display for banner
        banner_version_html = ''
        if self.version:
            banner_version_html = f'<span class="banner-version">Version: {self.version}</span>'

        if self.version:
            version_parts = self.version.split('.')
            if len(version_parts) >= 3:
                major, minor, patch = version_parts[0], version_parts[1], version_parts[2]

                # Map version numbers to colors (cycling through a palette)
                color_palette = [
                    '#e74c3c',  # Red
                    '#3498db',  # Blue
                    '#2ecc71',  # Green
                    '#f39c12',  # Orange
                    '#9b59b6',  # Purple
                    '#1abc9c',  # Turquoise
                    '#e67e22',  # Carrot
                    '#34495e',  # Wet Asphalt
                ]

                major_color = color_palette[int(major) % len(color_palette)]
                minor_color = color_palette[int(minor) % len(color_palette)]
                patch_color = color_palette[int(patch) % len(color_palette)]

                banner_class = 'with-version'
                footer_class = 'with-version'

                # Create gradient styles with actual color values
                banner_gradient = f"""
        .banner.with-version {{
            background: linear-gradient(90deg, {major_color} 0%, #ecf0f1 25%, #ecf0f1 75%, {minor_color} 100%) !important;
        }}

        [data-theme="dark"] .banner.with-version {{
            background: linear-gradient(90deg, {major_color} 0%, #2d2d2d 25%, #2d2d2d 75%, {minor_color} 100%) !important;
        }}"""

                footer_gradient = f"""
        .footer.with-version {{
            background: linear-gradient(135deg, {patch_color} 0%, #ecf0f1 35%) !important;
        }}

        [data-theme="dark"] .footer.with-version {{
            background: linear-gradient(135deg, {patch_color} 0%, #2d2d2d 35%) !important;
        }}"""

        html_header = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        :root {{
            --bg-color: #ffffff;
            --text-color: #333333;
            --banner-bg: #2c3e50;
            --banner-text: #000000;
            --header-bg: #ecf0f1;
            --section-bg: #f8f9fa;
            --border-color: #dee2e6;
            --table-header-bg: #e9ecef;
            --code-bg: #f5f5f5;
        }}

        [data-theme="dark"] {{
            --bg-color: #1e1e1e;
            --text-color: #e0e0e0;
            --banner-bg: #1a1a1a;
            --banner-text: #ffffff;
            --header-bg: #2d2d2d;
            --section-bg: #252525;
            --border-color: #404040;
            --table-header-bg: #333333;
            --code-bg: #2d2d2d;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1;
            transition: background-color 0.3s, color 0.3s;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        .banner {{
            color: var(--text-color);
            padding: 10px 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 100;
            flex-wrap: wrap;
            gap: 10px;
            flex-shrink: 0;
        }}

        .banner.no-version {{
            background: linear-gradient(135deg, var(--banner-bg) 0%, #34495e 100%);
        }}
        {banner_gradient}

        .banner.sticky {{
            position: sticky;
            top: 0;
        }}

        .banner h1 {{
            font-size: 24px;
            font-weight: 600;
        }}
        
        .banner-version {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 20px;
            color: var(--text-color);
            font-weight: 600;
        }}
        
        .banner-items-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            flex: 1;
            justify-content: center;
        }}

        .banner-item {{
            color: var(--text-color);
            background-color: rgba(0, 0, 0, 0.025);
            padding: 5px 10px;
            border-radius: 6px;
            border: 1px solid rgba(0, 0, 0, 0.2);
            min-width: 150px;
        }}

        [data-theme="dark"] .banner-item {{
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .banner-item-title {{
            font-weight: 600;
            font-size: 12px;
            color: var(--text-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}

        .banner-item-value {{
            font-size: 16px;
            color: var(--text-color);
            word-wrap: break-word;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 10px;
            flex: 1 0 auto;
            width: 100%;
        }}

        .header {{
            background-color: var(--header-bg);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
            display: none; /* Hidden by default */
        }}

        .header-item {{
            margin: 8px 0;
        }}

        .header-label {{
            font-weight: 600;
            display: inline-block;
            min-width: 150px;
        }}

        .section {{
            background-color: var(--section-bg);
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .section-title {{
            color: var(--text-color);
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
        }}
        
        .section-title.collapsible {{
            cursor: pointer;
            user-select: none;
            position: relative;
            padding-right: 30px;
        }}

        .section-title.collapsible::after {{
            content: '▼';
            position: absolute;
            right: 8px;
            transition: transform 0.3s;
            font-size: 14px;
        }}

        .section-title.collapsible.collapsed::after {{
            transform: rotate(-90deg);
        }}

        .section-status {{
            color: black;
            display: inline-block;
            margin-left: 12px;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            vertical-align: middle;
        }}
        
        [data-theme="dark"] .section-status {{
            color: white;
        }}

        .section-status-pass {{
            background-color: #229955;
        }}

        .section-status-pass::before {{
            content: '✓ PASS';
        }}

        .section-status-fail {{
            background-color: #e74c3c;
        }}

        .section-status-fail::before {{
            content: '✗ FAIL';
        }}

        .section-status-warning {{
            background-color: #f39c12;
        }}

        .section-status-warning::before {{
            content: '⚠ WARNING';
        }}

        .section-status-running {{
            background-color: #3498db;
            animation: pulse 1.5s ease-in-out infinite;
        }}

        .section-status-running::before {{
            content: '⟳ RUNNING';
        }}

        .section-status-data {{
            background-color: #9b59b6;
        }}

        .section-status-data::before {{
            content: '📊 DATA';
        }}

        .section-status-default {{
            background-color: #95a5a6;
        }}

        .section-status-default::before {{
            content: '● DEFAULT';
        }}

        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.6;
            }}
        }}

        [data-theme="dark"] .section-status-pass {{
            background-color: #229955;
        }}

        [data-theme="dark"] .section-status-fail {{
            background-color: #c0392b;
        }}

        [data-theme="dark"] .section-status-warning {{
            background-color: #e67e22;
        }}

        [data-theme="dark"] .section-status-running {{
            background-color: #2980b9;
        }}

        [data-theme="dark"] .section-status-data {{
            background-color: #8e44ad;
        }}

        [data-theme="dark"] .section-status-default {{
            background-color: #7f8c8d;
        }}

        .section-progress {{
            display: block;
            margin-top: 8px;
            height: 6px;
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 3px;
            overflow: hidden;
        }}

        [data-theme="dark"] .section-progress {{
            background-color: rgba(255, 255, 255, 0.1);
        }}

        .section-progress-bar {{
            height: 100%;
            background-color: #3498db;
            transition: width 0.3s ease;
            border-radius: 3px;
        }}

        .section-progress-bar.animated {{
            background: linear-gradient(90deg, #3498db 0%, #5dade2 50%, #3498db 100%);
            background-size: 200% 100%;
            animation: progressShimmer 1.5s ease-in-out infinite;
        }}

        .section-progress-bar.complete {{
            opacity: 0;
            transition: opacity 0.5s ease-out;
        }}

        .section-progress.complete {{
            display: none;
        }}

        @keyframes progressShimmer {{
            0% {{
                background-position: 200% 0;
            }}
            100% {{
                background-position: -200% 0;
            }}
        }}

        .section-content {{
            overflow: hidden;
            transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
        }}

        .section-content.collapsed {{
            max-height: 0 !important;
            opacity: 0;
        }}

        /* Category color classes for section titles */
        .section-title.category-pass {{
            border-bottom-color: #27ae60;
        }}

        .section-title.category-fail {{
            border-bottom-color: #e74c3c;
        }}

        .section-title.category-warning {{
            border-bottom-color: #f39c12;
        }}

        .section-title.category-running {{
            border-bottom-color: #3498db;
        }}

        .section-title.category-data {{
            border-bottom-color: #9b59b6;
        }}

        .section-title.category-default {{
            border-bottom-color: #95a5a6;
        }}

        [data-theme="dark"] .section-title {{
            color: #e0e0e0;
        }}

        .line {{
            margin: 10px 0;
        }}

        .line-break {{
            height: 1px;
            background-color: var(--border-color);
            margin: 15px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background-color: var(--bg-color);
            line-height: 0.5;
        }}

        th {{
            background-color: var(--table-header-bg);
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border: 1px solid var(--border-color);
        }}

        /* Category color classes for table headers */
        .category-pass th {{
            background-color: #27ae60 !important;
            color: white;
        }}

        .category-fail th {{
            background-color: #e74c3c !important;
            color: white;
        }}

        .category-warning th {{
            background-color: #f39c12 !important;
            color: white;
        }}

        .category-running th {{
            background-color: #3498db !important;
            color: white;
        }}

        .category-data th {{
            background-color: #9b59b6 !important;
            color: white;
        }}

        .category-default th {{
            background-color: #95a5a6 !important;
            color: white;
        }}

        td {{
            padding: 10px 12px;
            border: 1px solid var(--border-color);
        }}

        tr:nth-child(even) {{
            background-color: var(--section-bg);
        }}

        .figure {{
            margin: 20px 0;
            text-align: center;
        }}

        .figure img {{
            max-width: 100%;
            height: auto;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }}

        .figure-title {{
            font-weight: 600;
            margin-top: 10px;
            font-size: 14px;
            color: #555;
        }}
        
        .figure-light {{
            display: block;
        }}
        
        .figure-dark {{
            display: none;
        }}
        
        [data-theme="dark"] .figure-light {{
            display: none;
        }}
        
        [data-theme="dark"] .figure-dark {{
            display: block;
        }}

        .status-pass {{
            color: #27ae60;
            font-weight: 600;
        }}

        .status-fail {{
            color: #e74c3c;
            font-weight: 600;
        }}

        .status-warning {{
            color: #f39c12;
            font-weight: 600;
        }}

        /* Pass/Fail cell styling */
        .cell-pass {{
            background-color: #d4edda !important;
            color: #155724;
            font-weight: 600;
        }}

        .cell-fail {{
            background-color: #f8d7da !important;
            color: #721c24;
            font-weight: 600;
        }}

        [data-theme="dark"] .cell-pass {{
            background-color: #1e4620 !important;
            color: #4caf50;
        }}

        [data-theme="dark"] .cell-fail {{
            background-color: #5a1a1a !important;
            color: #ef5350;
        }}

        code {{
            background-color: var(--code-bg);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}

        .timestamp {{
            font-size: 12px;
            color: #7f8c8d;
        }}

        .footer {{
            padding: 5px 5px;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            bottom: 0;
            z-index: 98;
        }}

        .footer.no-version {{
            background-color: var(--header-bg);
        }}
        {footer_gradient}

        .footer-version {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 20px;
            color: var(--text-color);
            font-weight: 600;
        }}
        
        .footer-path {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 20px;
            color: var(--text-color);
            font-weight: 600;
        }}

        .footer-theme-toggle {{
            background: var(--section-bg);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}

        .footer-theme-toggle:hover {{
            background: var(--border-color);
        }}
    </style>
    <script>
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);

            const button = document.querySelector('.footer-theme-toggle');
            button.textContent = newTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
        }}
        
        function toggleSection(sectionId) {{
            const content = document.getElementById(sectionId + '-content');
            const title = document.getElementById(sectionId + '-title');
            
            if (content.classList.contains('collapsed')) {{
                // Expand
                content.classList.remove('collapsed');
                title.classList.remove('collapsed');
                content.style.maxHeight = content.scrollHeight + 'px';
            }} else {{
                // Collapse
                content.style.maxHeight = content.scrollHeight + 'px';
                // Force reflow
                content.offsetHeight;
                content.classList.add('collapsed');
                title.classList.add('collapsed');
            }}
        }}
    </script>
</head>
<body>
    <div class="banner {banner_class}{sticky_class}">
        <h1>{self.title}</h1>
        <div class="banner-items-container" id="banner-items-container">
            <!-- Banner items will be inserted here -->
        </div>
        {banner_version_html}
    </div>
    <div class="container">
"""
        self.lines.append(html_header)

        # Store footer class for finalize
        self.footer_class = footer_class

    def add_header_item(self, title: str, value: str):
        """
        Add an item to the banner.

        Args:
            title: The title/label (will be bold and uppercase)
            value: The value/text (will be normal weight)
        """
        self.header_items.append((title, value))
        return self

    def _build_banner_items(self) -> str:
        """Build the banner items HTML from stored items."""
        if not self.header_items:
            return ""

        banner_html = ""
        for title, value in self.header_items:
            banner_html += f"""            <div class="banner-item">
                <div class="banner-item-title">{title}</div>
                <div class="banner-item-value">{value}</div>
            </div>
"""
        return banner_html

    def add_header(self, info: Dict[str, str]):
        """
        Add header information to the banner.
        This is a convenience method that adds multiple header items at once.

        Args:
            info: Dictionary of title-value pairs
        """
        for title, value in info.items():
            self.add_header_item(title, value)
        return self

    def start_section(self, title: str, collapsed: bool = False):
        """
        Start a new section with progress bar.

        :param title: Section title
        :type title: str
        :param collapsed: Start in collapsed state
        :type collapsed: bool
        :returns: Self for method chaining
        :rtype: HTMLTestReport

        .. note::
           All sections automatically get progress bars and default to 'running' status

        .. versionadded:: 1.0.0
        """
        self.current_section_title = title

        # Build status badge
        status_badge = f'<span class="section-status section-status-running"></span>'

        # Build progress bar if requested
        progress_bar = ''
        section_id = f'section-{self.section_counter}'
        progress_bar = f'<div class="section-progress"><div id="{section_id}-progress" class="section-progress-bar animated" style="width: 0%"></div></div>'

        if self.collapsible:
            section_id = f'section-{self.section_counter}'
            self.section_counter += 1

            collapsed_class = ' collapsed' if collapsed else ''
            collapsible_class = ' collapsible'
            onclick = f' onclick="toggleSection(\'{section_id}\')"'

            section_html = f'<div class="section">\n'
            section_html += f'    <div id="{section_id}-title" class="section-title category-running{collapsible_class}{collapsed_class}"{onclick}>{title}{status_badge}{progress_bar}</div>\n'
            section_html += f'    <div id="{section_id}-content" class="section-content{collapsed_class}">\n'
        else:
            section_id = f'section-{self.section_counter}'
            self.section_counter += 1

            section_html = f'<div class="section">\n'
            section_html += f'    <div class="section-title category-running">{title}{status_badge}{progress_bar}</div>\n'

        self.lines.append(section_html)
        return self

    def end_section(self, status: Optional[str] = None):
        """
        End the current section and optionally set final status.

        Closes the currently open section. Optionally sets the progress bar
        to 100% and updates the status badge in one call. This is a convenience
        method that combines update_section_progress(100) and update_section_status()
        with end_section().

        Args:
            status (Optional[str]): Optional final status for the section.
                Valid values: 'pass', 'fail', 'warning', 'data', 'default'.
                If provided, automatically sets progress to 100% and updates
                the status badge. If None, section ends without status update.

        Returns:
            HTMLTestReport: Self for method chaining

        Note:
            - Always pair this with start_section()
            - When status is provided, progress bar automatically set to 100%
            - Progress bar will hide after reaching 100%
            - Failure to call end_section() will result in malformed HTML

        Example:
            >>> # Simple section close (manual status control)
            >>> report.start_section("Power Tests")
            >>> report.add_line("Test 1")
            >>> report.update_section_progress("Power Tests", 50)
            >>> report.add_line("Test 2")
            >>> report.update_section_progress("Power Tests", 100)
            >>> report.update_section_status("Power Tests", "pass")
            >>> report.end_section()  # Just closes section

            >>> # Simplified - end with status (auto 100% progress)
            >>> report.start_section("Voltage Tests")
            >>> report.add_line("Test 1")
            >>> report.update_section_progress("Voltage Tests", 50)
            >>> report.add_line("Test 2")
            >>> report.end_section(status="pass")  # Sets 100% AND pass status

            >>> # Failed section
            >>> report.start_section("Current Tests")
            >>> report.add_line("Test failed", status="fail")
            >>> report.end_section(status="fail")  # Sets 100% AND fail status

            >>> # Warning section
            >>> report.start_section("Connection Tests")
            >>> report.add_line("Marginal connection", status="warning")
            >>> report.end_section(status="warning")

            >>> # Data collection (not a test)
            >>> report.start_section("Data Acquisition")
            >>> report.add_line("Collected 1000 samples")
            >>> report.end_section(status="data")

        .. versionadded:: 1.0.0
        .. versionchanged:: 1.1.0
           Added status parameter for automatic progress and status setting
        """

        # If status is provided, set progress to 100% and update status
        if status is not None:
            self.update_section_progress(self.current_section_title, 100)  # Complete
            self.update_section_status(self.current_section_title, status)  # Complete

        if self.collapsible:
            self.lines.append('    </div>\n')  # Close section-content
        self.lines.append('</div>\n')  # Close section

        self.current_section_title = None
        return self

    def update_section_status(self, section_title: str, status: str):
        """
        Update the status badge and category color of an existing section.

        Useful for updating test results as tests complete. Changes the
        status from 'running' to 'pass', 'fail', etc., and updates the
        section title color to match the new status.

        Args:
            section_title: The exact title of the section to update
            status: New status. Valid values:
                'pass', 'fail', 'warning', 'running', 'data', 'default'

        Returns:
            HTMLTestReport: Self for method chaining

        Note:
            This method updates both:
            - The status badge (colored pill with text)
            - The category color (section title border and text color)

        Example:
            >>> report.start_section("Power Tests")  # Defaults to 'running'
            >>> # ... run tests ...
            >>> report.update_section_status("Power Tests", "pass")  # Updates badge AND color

        .. versionadded:: 1.0.0
        .. versionchanged:: 1.1.0
           Now also updates the section category color to match the status
        """
        import re

        for i, line in enumerate(self.lines):
            if f'class="section-title' in line and section_title in line:
                # Remove existing status badge
                line = re.sub(r'<span class="section-status section-status-\w+"></span>', '', line)

                # Remove any existing category class
                line = re.sub(r' category-\w+', '', line)

                # Add new category class (must be added to the section-title element)
                # Find the class="section-title and insert after it
                line = re.sub(
                    r'class="section-title',
                    f'class="section-title category-{status}',
                    line
                )

                # Add new status badge
                status_badge = f'<span class="section-status section-status-{status}"></span>'

                # Insert before progress bar if exists, otherwise before closing tag
                if '<div class="section-progress' in line:
                    line = line.replace('<div class="section-progress', f'{status_badge}<div class="section-progress')
                else:
                    line = line.replace(f'>{section_title}<', f'>{section_title}{status_badge}<')

                self.lines[i] = line
                break
        return self

    def update_section_progress(self, section_title: str, progress: int):
        """
        Update the progress bar of an existing section.

        Args:
            section_title: The title of the section to update
            progress: Progress percentage (0-100)
        """
        # Clamp progress to 0-100
        progress = max(0, min(100, progress))

        # Find the section in the lines
        for i, line in enumerate(self.lines):
            if f'class="section-title' in line and section_title in line:
                # Find and update the progress bar width
                import re
                line = re.sub(
                    r'(<div id="section-\d+-progress" class="section-progress-bar[^"]*" style="width: )\d+(%")',
                    f'\\g<1>{progress}\\g<2>',
                    line
                )

                # When complete, add complete class to hide progress bar
                if progress >= 100:
                    line = line.replace(' animated', '')
                    # Add complete class to progress bar
                    line = re.sub(
                        r'(<div id="section-\d+-progress" class="section-progress-bar)"',
                        r'\1 complete"',
                        line
                    )
                    # Add complete class to progress container
                    line = line.replace('<div class="section-progress">', '<div class="section-progress complete">')

                self.lines[i] = line
                break
        return self

    def add_line(self, text: str):
        """
        Add a line of text.

        Args:
            text: The text to add
        """
        line_html = f'    <div class="line">{text}</div>\n'
        self.lines.append(line_html)
        return self

    def add_line_break(self):
        """Add a horizontal line break."""
        self.lines.append('    <div class="line-break"></div>\n')
        return self

    def add_table(self, headers: List[str], rows: List[List[str]] = None,
                  title: Optional[str] = None, category: Optional[str] = None,
                  measured_col: Optional[str] = None,
                  nominal_col: Optional[str] = None, tolerance_col: Optional[str] = None,
                  lower_spec_col: Optional[str] = None, upper_spec_col: Optional[str] = None):
        """
        Add a table to the report with optional auto pass/fail coloring.

        Args:
            headers: List of column headers
            rows: List of rows, where each row is a list of values (can be empty list or None)
            title: Optional table title
            category: Optional category for header coloring ('pass', 'fail', 'warning', 'running', 'data', 'default')
            measured_col: Column name containing measured values (for auto pass/fail)
            nominal_col: Column name containing nominal values (requires tolerance_col)
            tolerance_col: Column name containing tolerance values (requires nominal_col)
            lower_spec_col: Column name containing lower spec limits
            upper_spec_col: Column name containing upper spec limits

        Note: Use either (nominal_col + tolerance_col) OR (lower_spec_col + upper_spec_col), not both.
        """
        if rows is None:
            rows = []

        # Store spec configuration for add_table_row
        self.last_table_specs = {
            'headers': headers,
            'measured_col': measured_col,
            'nominal_col': nominal_col,
            'tolerance_col': tolerance_col,
            'lower_spec_col': lower_spec_col,
            'upper_spec_col': upper_spec_col
        }

        category_class = f' category-{category}' if category else ''

        table_html = ''
        if title:
            table_html += f'    <div style="font-weight: 600; margin: 15px 0 5px 0;">{title}</div>\n'

        table_html += f'    <table class="{category_class}">\n        <thead>\n            <tr>\n'
        for header in headers:
            table_html += f'                <th>{header}</th>\n'
        table_html += '            </tr>\n        </thead>\n        <tbody>\n'

        for row in rows:
            processed_row = self._process_row_with_specs(row)
            table_html += processed_row

        table_html += '        </tbody>\n    </table>\n'

        # Track where this table ends (before the closing </table> tag)
        self.last_table_index = len(self.lines)
        self.lines.append(table_html)
        return self

    def _process_row_with_specs(self, row: List[str]) -> str:
        """Process a row and apply pass/fail coloring based on specs."""
        if not self.last_table_specs or not self.last_table_specs['measured_col']:
            # No specs configured, return regular row
            row_html = '            <tr>\n'
            for cell in row:
                row_html += f'                <td>{cell}</td>\n'
            row_html += '            </tr>\n'
            return row_html

        headers = self.last_table_specs['headers']
        measured_col = self.last_table_specs['measured_col']
        nominal_col = self.last_table_specs['nominal_col']
        tolerance_col = self.last_table_specs['tolerance_col']
        lower_spec_col = self.last_table_specs['lower_spec_col']
        upper_spec_col = self.last_table_specs['upper_spec_col']

        # Find column indices
        try:
            measured_idx = headers.index(measured_col)
        except ValueError:
            # Measured column not found, return regular row
            row_html = '            <tr>\n'
            for cell in row:
                row_html += f'                <td>{cell}</td>\n'
            row_html += '            </tr>\n'
            return row_html

        # Get measured value
        try:
            measured_value = float(row[measured_idx])
        except (ValueError, IndexError):
            # Can't parse measured value, return regular row
            row_html = '            <tr>\n'
            for cell in row:
                row_html += f'                <td>{cell}</td>\n'
            row_html += '            </tr>\n'
            return row_html

        # Determine pass/fail
        is_pass = False

        # Check nominal + tolerance method
        if nominal_col and tolerance_col:
            try:
                nominal_idx = headers.index(nominal_col)
                tolerance_idx = headers.index(tolerance_col)
                nominal_value = float(row[nominal_idx])
                tolerance_value = float(row[tolerance_idx])

                lower_limit = nominal_value - tolerance_value
                upper_limit = nominal_value + tolerance_value
                is_pass = lower_limit <= measured_value <= upper_limit
            except (ValueError, IndexError):
                pass

        # Check lower/upper spec method
        elif lower_spec_col and upper_spec_col:
            try:
                lower_idx = headers.index(lower_spec_col)
                upper_idx = headers.index(upper_spec_col)
                lower_limit = float(row[lower_idx])
                upper_limit = float(row[upper_idx])

                is_pass = lower_limit <= measured_value <= upper_limit
            except (ValueError, IndexError):
                pass

        # Build row with pass/fail status
        row_html = '            <tr>\n'
        for i, cell in enumerate(row):
            if i == measured_idx:
                css_class = ' class="cell-pass"' if is_pass else ' class="cell-fail"'
                status_text = " ✓" if is_pass else " ✗"
                row_html += f'                <td{css_class}>{cell}{status_text}</td>\n'
            else:
                row_html += f'                <td>{cell}</td>\n'
        row_html += '            </tr>\n'

        return row_html

    def add_table_row(self, row: List[str]):
        """
        Add a row to the last table in the report.
        Must be called after add_table() has been called.
        Automatically applies pass/fail coloring if specs were configured.

        Args:
            row: List of cell values for the new row
        """
        if self.last_table_index is None:
            raise ValueError("No table exists. Call add_table() first before adding rows.")

        # Get the last table HTML
        table_html = self.lines[self.last_table_index]

        # Find the position to insert the new row (before </tbody>)
        insert_pos = table_html.rfind('        </tbody>')

        if insert_pos == -1:
            raise ValueError("Could not find table body in the last table.")

        # Build the new row HTML with pass/fail processing
        new_row_html = self._process_row_with_specs(row)

        # Insert the new row before </tbody>
        updated_table_html = (
                table_html[:insert_pos] +
                new_row_html +
                table_html[insert_pos:]
        )

        # Update the stored table HTML
        self.lines[self.last_table_index] = updated_table_html
        return self

    def add_plot(self, plot_data: Union[bytes, str], title: Optional[str] = None, format: str = "png"):
        """
        Add a plot/figure to the report.

        Args:
            plot_data: Either base64-encoded string or raw bytes of the image
            title: Optional figure title
            format: Image format (png, jpg, svg, etc.)
        """
        if isinstance(plot_data, bytes):
            img_base64 = base64.b64encode(plot_data).decode('utf-8')
        else:
            img_base64 = plot_data

        figure_html = '    <div class="figure">\n'
        figure_html += f'        <img src="data:image/{format};base64,{img_base64}" alt="Plot">\n'
        if title:
            figure_html += f'        <div class="figure-title">{title}</div>\n'
        figure_html += '    </div>\n'
        self.lines.append(figure_html)
        return self

    def add_dual_plot(self, light_plot_data: Union[bytes, str], dark_plot_data: Union[bytes, str],
                      title: Optional[str] = None, format: str = "png"):
        """
        Add light and dark mode versions of a plot.

        Args:
            light_plot_data: Plot data for light mode
            dark_plot_data: Plot data for dark mode
            title: Optional figure title
            format: Image format (png, jpg, svg, etc.)
        """
        if isinstance(light_plot_data, bytes):
            light_base64 = base64.b64encode(light_plot_data).decode('utf-8')
        else:
            light_base64 = light_plot_data

        if isinstance(dark_plot_data, bytes):
            dark_base64 = base64.b64encode(dark_plot_data).decode('utf-8')
        else:
            dark_base64 = dark_plot_data

        figure_html = '    <div class="figure">\n'
        figure_html += f'        <img class="figure-light" src="data:image/{format};base64,{light_base64}" alt="Plot">\n'
        figure_html += f'        <img class="figure-dark" src="data:image/{format};base64,{dark_base64}" alt="Plot">\n'
        if title:
            figure_html += f'        <div class="figure-title">{title}</div>\n'
        figure_html += '    </div>\n'
        self.lines.append(figure_html)
        return self

    def add_matplotlib_plot(self, fig, title: Optional[str] = None):
        """
        Add a matplotlib figure to the report.

        Args:
            fig: Matplotlib figure object
            title: Optional figure title
        """
        try:
            import matplotlib.pyplot as plt
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_data = buf.read()
            buf.close()
            self.add_plot(img_data, title=title, format='png')
        except ImportError:
            self.add_line("⚠️ Matplotlib not available - cannot add plot", status="warning")
        return self

    def finalize(self) -> str:
        """
        Finalize and return the complete HTML document.

        Returns:
            Complete HTML string
        """
        # Build banner items content
        banner_items_html = self._build_banner_items()

        # Insert banner items into the HTML
        full_html = ''.join(self.lines)
        full_html = full_html.replace(
            '            <!-- Banner items will be inserted here -->',
            banner_items_html
        )

        # Build footer
        footer_version = f'Version: {self.version}' if self.version else ''

        footer = f"""    </div>
    <div class="footer {self.footer_class}">
        <div class="footer-version">{footer_version}</div>
        <a class= "footer-path" href="file:///{self.test_log_path}" target="_blank">Test Log Can be found here.</a>
        <button class="footer-theme-toggle" onclick="toggleTheme()">🌙 Dark Mode</button>
    </div>
</body>
</html>"""
        return full_html + footer

    def save(self, filename: str):
        """
        Save the report to an HTML file.

        Args:
            filename: Path to save the HTML file
        """
        html_content = self.finalize()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Report saved to: {filename}")

    def display_in_notebook(self):
        """Display the report in a Jupyter notebook."""
        try:
            from IPython.display import HTML, display
            html_content = self.finalize()
            display(HTML(html_content))
        except ImportError:
            print("IPython not available - cannot display in notebook")

def create_scatter_plot_example():
    # Create scatter plot - LIGHT VERSION
    fig1_light, ax1 = plt.subplots(figsize=(8, 5), facecolor='white')
    ax1.set_facecolor('white')
    x_scatter = np.random.randn(100)
    y_scatter = 2 * x_scatter + np.random.randn(100) * 0.5
    ax1.scatter(x_scatter, y_scatter, alpha=0.6, c='blue', edgecolors='black')
    ax1.set_xlabel('X Value', color='black')
    ax1.set_ylabel('Y Value', color='black')
    ax1.set_title('Scatter Plot: Correlation Analysis', color='black')
    ax1.tick_params(colors='black')
    ax1.grid(True, alpha=0.3, color='gray')
    for spine in ax1.spines.values():
        spine.set_edgecolor('black')

    buf1_light = io.BytesIO()
    fig1_light.savefig(buf1_light, format='png', dpi=150, bbox_inches='tight')
    buf1_light.seek(0)
    scatter_light = buf1_light.read()
    buf1_light.close()
    plt.close(fig1_light)

    # Create scatter plot - DARK VERSION
    fig1_dark, ax1 = plt.subplots(figsize=(8, 5), facecolor='#1e1e1e')
    ax1.set_facecolor('#1e1e1e')
    ax1.scatter(x_scatter, y_scatter, alpha=0.6, c='#3498db', edgecolors='white')
    ax1.set_xlabel('X Value', color='white')
    ax1.set_ylabel('Y Value', color='white')
    ax1.set_title('Scatter Plot: Correlation Analysis', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, alpha=0.3, color='gray')
    for spine in ax1.spines.values():
        spine.set_edgecolor('white')

    buf1_dark = io.BytesIO()
    fig1_dark.savefig(buf1_dark, format='png', dpi=150, bbox_inches='tight')
    buf1_dark.seek(0)
    scatter_dark = buf1_dark.read()
    buf1_dark.close()
    plt.close(fig1_dark)
    return scatter_light, scatter_dark

def create_line_plot_example():
    # Create line plot - LIGHT VERSION
    fig2_light, ax2 = plt.subplots(figsize=(8, 5), facecolor='white')
    ax2.set_facecolor('white')
    x_line = np.linspace(0, 10, 100)
    y_line1 = np.sin(x_line)
    y_line2 = np.cos(x_line)
    ax2.plot(x_line, y_line1, label='Sin(x)', linewidth=2, color='blue')
    ax2.plot(x_line, y_line2, label='Cos(x)', linewidth=2, color='orange')
    ax2.set_xlabel('Time (s)', color='black')
    ax2.set_ylabel('Amplitude', color='black')
    ax2.set_title('Line Plot: Waveform Analysis', color='black')
    ax2.tick_params(colors='black')
    ax2.legend(facecolor='white', edgecolor='black', labelcolor='black')
    ax2.grid(True, alpha=0.3, color='gray')
    for spine in ax2.spines.values():
        spine.set_edgecolor('black')

    buf2_light = io.BytesIO()
    fig2_light.savefig(buf2_light, format='png', dpi=150, bbox_inches='tight')
    buf2_light.seek(0)
    line_light = buf2_light.read()
    buf2_light.close()
    plt.close(fig2_light)

    # Create line plot - DARK VERSION
    fig2_dark, ax2 = plt.subplots(figsize=(8, 5), facecolor='#1e1e1e')
    ax2.set_facecolor('#1e1e1e')
    ax2.plot(x_line, y_line1, label='Sin(x)', linewidth=2, color='#3498db')
    ax2.plot(x_line, y_line2, label='Cos(x)', linewidth=2, color='#f39c12')
    ax2.set_xlabel('Time (s)', color='white')
    ax2.set_ylabel('Amplitude', color='white')
    ax2.set_title('Line Plot: Waveform Analysis', color='white')
    ax2.tick_params(colors='white')
    ax2.legend(facecolor='#1e1e1e', edgecolor='white', labelcolor='white')
    ax2.grid(True, alpha=0.3, color='gray')
    for spine in ax2.spines.values():
        spine.set_edgecolor('white')

    buf2_dark = io.BytesIO()
    fig2_dark.savefig(buf2_dark, format='png', dpi=150, bbox_inches='tight')
    buf2_dark.seek(0)
    line_dark = buf2_dark.read()
    buf2_dark.close()
    plt.close(fig2_dark)

    return line_light, line_dark,

def create_histogram_plot_example():
    # Create histogram - LIGHT VERSION
    fig3_light, ax3 = plt.subplots(figsize=(8, 5), facecolor='white')
    ax3.set_facecolor('white')
    data_hist = np.random.normal(100, 15, 1000)
    ax3.hist(data_hist, bins=30, alpha=0.7, color='green', edgecolor='black')
    ax3.set_xlabel('Value', color='black')
    ax3.set_ylabel('Frequency', color='black')
    ax3.set_title('Histogram: Data Distribution', color='black')
    ax3.tick_params(colors='black')
    mean_line = ax3.axvline(data_hist.mean(), color='red', linestyle='--', linewidth=2,
                            label=f'Mean: {data_hist.mean():.2f}')
    ax3.legend(facecolor='white', edgecolor='black', labelcolor='black')
    ax3.grid(True, alpha=0.3, axis='y', color='gray')
    for spine in ax3.spines.values():
        spine.set_edgecolor('black')

    buf3_light = io.BytesIO()
    fig3_light.savefig(buf3_light, format='png', dpi=150, bbox_inches='tight')
    buf3_light.seek(0)
    hist_light = buf3_light.read()
    buf3_light.close()
    plt.close(fig3_light)

    # Create histogram - DARK VERSION
    fig3_dark, ax3 = plt.subplots(figsize=(8, 5), facecolor='#1e1e1e')
    ax3.set_facecolor('#1e1e1e')
    ax3.hist(data_hist, bins=30, alpha=0.7, color='#2ecc71', edgecolor='white')
    ax3.set_xlabel('Value', color='white')
    ax3.set_ylabel('Frequency', color='white')
    ax3.set_title('Histogram: Data Distribution', color='white')
    ax3.tick_params(colors='white')
    ax3.axvline(data_hist.mean(), color='#e74c3c', linestyle='--', linewidth=2,
                label=f'Mean: {data_hist.mean():.2f}')
    ax3.legend(facecolor='#1e1e1e', edgecolor='white', labelcolor='white')
    ax3.grid(True, alpha=0.3, axis='y', color='gray')
    for spine in ax3.spines.values():
        spine.set_edgecolor('white')

    buf3_dark = io.BytesIO()
    fig3_dark.savefig(buf3_dark, format='png', dpi=150, bbox_inches='tight')
    buf3_dark.seek(0)
    hist_dark = buf3_dark.read()
    buf3_dark.close()
    plt.close(fig3_dark)

    return hist_light, hist_dark


# Example usage
if __name__ == "__main__":

    url = r'file:///C:/Users/Zacha/Documents/GitHub/pyTestLogs/'

    # Create a new report with sticky header, version badge, and collapsible sections
    report = HTMLTestReport(
        title="Voyager 1088 - PIA2 PreTest",
        sticky_header=True,  # Set to False if you don't want sticky header
        version="0.1.2",  # Test script version - determines gradient colors
        collapsible=True  # Enable collapsible sections
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
    report.start_section("Power Supply Tests", category="running", show_progress=True)
    report.add_line("Testing 3.3V rail...", status="pass")
    report.add_line("Measured voltage: 3.31V (within tolerance)")
    report.update_section_progress("Power Supply Tests", 33)  # Update to 33%
    report.save("test_report.html")
    webbrowser.open_new_tab(url)

    report.add_line("Testing 5V rail...", status="pass")
    report.add_line("Measured voltage: 5.02V (within tolerance)")
    report.update_section_progress("Power Supply Tests", 66)  # Update to 66%
    report.save("test_report.html")
    webbrowser.open_new_tab(url)

    report.add_line_break()
    report.add_line("Testing 12V rail...", status="pass")
    report.add_line("Measured voltage: 12.01V (within tolerance)")
    report.update_section_progress("Power Supply Tests", 100)  # Complete
    report.update_section_status("Power Supply Tests", "pass")  # Complete

    report.save("test_report.html")
    webbrowser.open_new_tab(url)

    report.end_section()
    # Update status after test completes (changes from default "running" to "pass")
    report.update_section_status("Power Supply Tests", "pass")
    report.save("test_report.html")
    webbrowser.open_new_tab(url)

    # Update status after test completes

    report.save("test_report.html")
    webbrowser.open_new_tab(url)

    # Example 2: Section with status badge (collapsed, failed)
    report.start_section("Voltage Measurements", category="voltage", collapsed=True, status="fail")
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
    report.end_section()
    # Update to "fail" because one measurement failed
    report.update_section_status("Voltage Measurements", "fail")

    # Example 3: Section with "pass" category that ends with "pass" status
    report.start_section("Current Measurements", category="pass")  # Starts as "running"
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
    report.end_section()
    # All tests passed, update to "pass"
    report.update_section_status("Current Measurements", "pass")

    # Example 4: Section with "warning" category and status (collapsed)
    report.start_section("Communication Tests", category="warning", collapsed=True)
    report.add_line("I2C bus scan: 4 devices found", status="pass")
    report.add_line("SPI flash ID: 0xEF4018", status="pass")
    report.add_line("UART loopback test: MARGINAL", status="warning")
    report.end_section()

    # Example 5: Section with fail status
    report.start_section("Temperature Tests", category="temperature", status="fail")
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
    report.end_section()

    # Add matplotlib plots section (collapsed, pass status)
    try:
        report.start_section("Data Visualization", category="custom", collapsed=True, status="pass")

        scatter_light, scatter_dark = create_scatter_plot_example()
        report.add_dual_plot(scatter_light, scatter_dark,
                             title="Figure 1: Scatter plot showing correlation between variables")

        line_light, line_dark = create_line_plot_example()
        report.add_dual_plot(line_light, line_dark,
                             title="Figure 2: Line plot showing signal waveforms over time")

        hist_light, hist_dark = create_histogram_plot_example()
        report.add_dual_plot(hist_light, hist_dark,
                             title="Figure 3: Histogram showing distribution of measured values")

        report.end_section()

    except ImportError:
        report.start_section("Data Visualization", category="custom", status="fail")
        report.add_line("⚠️ Matplotlib not available - cannot generate plots", status="warning")
        report.end_section()

    # Save the report
    report.save("test_report.html")
    print("\nExample report generated successfully!")
    print("Open 'test_report.html' in a browser to view the report.")
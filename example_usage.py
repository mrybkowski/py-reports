#!/usr/bin/env python3
"""Example usage of the PDF Reports Generator system."""

import sys
from pathlib import Path
from datetime import datetime, date

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from py_reports.renderer import ReportGenerator
from py_reports.config import get_settings

def example_sales_report():
    """Example: Generate a sales report."""
    print("Example: Sales Report Generation")
    print("=" * 40)
    
    try:
        # Create report generator
        generator = ReportGenerator(locale="en_US")
        
        # Define report parameters
        parameters = {
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "customer_id": ["customer1", "customer2"],
            "status": "completed"
        }
        
        print(f"Parameters: {parameters}")
        
        # Generate report
        print("Generating sales report...")
        pdf_path = generator.generate_report(
            report_name="sales",
            parameters=parameters,
            output_path="output/sales_report_example.pdf"
        )
        
        print(f"✓ Report generated: {pdf_path}")
        
        # Get report info
        info = generator.get_report_info("sales")
        print(f"Report info: {info['description']}")
        print(f"Columns: {info['column_count']}")
        print(f"Has pivot: {info['has_pivot']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating sales report: {e}")
        return False

def example_inventory_report():
    """Example: Generate an inventory report."""
    print("\nExample: Inventory Report Generation")
    print("=" * 40)
    
    try:
        # Create report generator
        generator = ReportGenerator(locale="pl_PL")
        
        # Define report parameters
        parameters = {
            "min_stock": 10,
            "category_id": ["electronics", "clothing"]
        }
        
        print(f"Parameters: {parameters}")
        
        # Generate report
        print("Generating inventory report...")
        pdf_path = generator.generate_report(
            report_name="inventory",
            parameters=parameters,
            output_path="output/inventory_report_example.pdf"
        )
        
        print(f"✓ Report generated: {pdf_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating inventory report: {e}")
        return False

def example_api_usage():
    """Example: Using the API programmatically."""
    print("\nExample: API Usage")
    print("=" * 40)
    
    try:
        from py_reports.api import get_generator
        
        # Get generator instance
        generator = get_generator("en_US")
        
        # List available reports
        reports = generator.list_available_reports()
        print(f"Available reports: {reports}")
        
        # Validate a report
        validation = generator.validate_report_config("sales")
        print(f"Sales report validation: {validation['valid']}")
        
        # Test report generation
        test_result = generator.test_report_generation("sales", {
            "date_from": "2025-01-01",
            "date_to": "2025-01-31"
        })
        print(f"Test result: {test_result['success']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in API usage: {e}")
        return False

def example_translation_usage():
    """Example: Using translations."""
    print("\nExample: Translation Usage")
    print("=" * 40)
    
    try:
        from py_reports.translations import get_translator
        
        # Get translator
        translator = get_translator()
        
        # Test different locales
        locales = ["en_US", "pl_PL"]
        
        for locale in locales:
            print(f"\nLocale: {locale}")
            
            # Translate report title
            title = translator.translate("report.sales.title", locale=locale)
            print(f"  Title: {title}")
            
            # Translate with parameters
            date_range = translator.translate(
                "header.date_range",
                from_date="2025-01-01",
                to_date="2025-01-31",
                locale=locale
            )
            print(f"  Date range: {date_range}")
            
            # Format currency
            currency = translator.format_currency(1234.56, "PLN", locale=locale)
            print(f"  Currency: {currency}")
            
            # Format date
            formatted_date = translator.format_date(date(2025, 1, 15), locale=locale)
            print(f"  Date: {formatted_date}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in translation usage: {e}")
        return False

def example_custom_template():
    """Example: Creating a custom template."""
    print("\nExample: Custom Template")
    print("=" * 40)
    
    try:
        from py_reports.templates import get_template_engine
        
        # Get template engine
        template_engine = get_template_engine()
        
        # Custom template string
        template_string = """
        <html>
        <head><title>{{ title }}</title></head>
        <body>
            <h1>{{ title }}</h1>
            <p>Generated at: {{ now }}</p>
            <p>Locale: {{ locale }}</p>
            
            {% if data %}
            <table border="1">
                <tr>
                    <th>Name</th>
                    <th>Value</th>
                </tr>
                {% for item in data %}
                <tr>
                    <td>{{ item.name }}</td>
                    <td>{{ item.value|currency('PLN') }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
        </body>
        </html>
        """
        
        # Render template
        context = {
            "title": "Custom Report",
            "data": [
                {"name": "Item 1", "value": 100.50},
                {"name": "Item 2", "value": 250.75},
                {"name": "Item 3", "value": 99.99}
            ]
        }
        
        html = template_engine.render_string(template_string, context)
        print("✓ Custom template rendered successfully")
        print(f"HTML length: {len(html)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in custom template: {e}")
        return False

def main():
    """Run all examples."""
    print("PDF Reports Generator - Usage Examples")
    print("=" * 50)
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    examples = [
        example_translation_usage,
        example_custom_template,
        example_api_usage,
        example_sales_report,
        example_inventory_report,
    ]
    
    passed = 0
    total = len(examples)
    
    for example in examples:
        if example():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Example Results: {passed}/{total} examples completed successfully")
    
    if passed == total:
        print("✓ All examples completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure MongoDB connection in .env file")
        print("3. Run CLI: python -m py_reports.cli list-reports")
        print("4. Start API server: python -m py_reports.cli serve")
        return 0
    else:
        print("✗ Some examples failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
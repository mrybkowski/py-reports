#!/usr/bin/env python3
"""Test script for report generation."""

import sys
from pathlib import Path
from datetime import datetime, date

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from py_reports.renderer import ReportGenerator

def test_simple_report():
    """Test generating a simple report without MongoDB."""
    print("Testing simple report generation...")
    
    try:
        # Create a simple HTML template for testing
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            <p>Generated at: {{ now }}</p>
            <p>Locale: {{ locale }}</p>
            
            <h2>Sample Data</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Value</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in data %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td>{{ item.value|currency('PLN') }}</td>
                        <td>{{ item.date|date }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Create sample data
        sample_data = [
            {"name": "Item 1", "value": 100.50, "date": "2025-01-15"},
            {"name": "Item 2", "value": 250.75, "date": "2025-01-16"},
            {"name": "Item 3", "value": 99.99, "date": "2025-01-17"}
        ]
        
        # Create template context
        context = {
            "data": sample_data,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "locale": "pl_PL"
        }
        
        # Generate PDF using template engine directly
        from py_reports.templates import get_template_engine
        from py_reports.renderer import get_pdf_renderer
        
        template_engine = get_template_engine(locale="pl_PL")
        pdf_renderer = get_pdf_renderer(locale="pl_PL")
        
        # Render HTML
        html = template_engine.render_string(html_content, context)
        print(f"✓ HTML rendered successfully ({len(html)} characters)")
        
        # Generate PDF
        output_path = Path("output/test_report.pdf")
        output_path.parent.mkdir(exist_ok=True)
        
        pdf_path = pdf_renderer.render_pdf_from_string(html, context, output_path)
        print(f"✓ PDF generated: {pdf_path}")
        
        # Check file size
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✓ File size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating simple report: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_system():
    """Test translation system."""
    print("\nTesting translation system...")
    
    try:
        from py_reports.translations import get_translator
        
        translator = get_translator()
        
        # Test different locales
        locales = ["en_US", "pl_PL"]
        
        for locale in locales:
            print(f"\nLocale: {locale}")
            
            # Test basic translation
            title = translator.translate("report.sales.title", locale=locale)
            print(f"  Title: {title}")
            
            # Test currency formatting
            currency = translator.format_currency(1234.56, "PLN", locale=locale)
            print(f"  Currency: {currency}")
            
            # Test date formatting
            formatted_date = translator.format_date(date(2025, 1, 15), locale=locale)
            print(f"  Date: {formatted_date}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing translations: {e}")
        return False

def main():
    """Run all tests."""
    print("PDF Reports Generator - Report Generation Test")
    print("=" * 50)
    
    tests = [
        test_translation_system,
        test_simple_report,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Report generation is working.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
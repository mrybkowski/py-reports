#!/usr/bin/env python3
"""Test script for the PDF Reports Generator system."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from py_reports.renderer import ReportGenerator
from py_reports.config import get_settings
from py_reports.data import get_mongodb_client
from py_reports.translations import get_translator

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from py_reports import __version__
        print(f"✓ Package version: {__version__}")
    except Exception as e:
        print(f"✗ Package import failed: {e}")
        return False
    
    try:
        from py_reports.config import get_settings
        settings = get_settings()
        print(f"✓ Settings loaded: {settings.mongodb_database}")
    except Exception as e:
        print(f"✗ Settings import failed: {e}")
        return False
    
    try:
        from py_reports.translations import get_translator
        translator = get_translator()
        print(f"✓ Translator loaded: {translator.get_available_locales()}")
    except Exception as e:
        print(f"✗ Translator import failed: {e}")
        return False
    
    try:
        from py_reports.data import get_mongodb_client
        client = get_mongodb_client()
        print(f"✓ MongoDB client created")
    except Exception as e:
        print(f"✗ MongoDB client import failed: {e}")
        return False
    
    try:
        from py_reports.renderer import ReportGenerator
        generator = ReportGenerator()
        print(f"✓ Report generator created")
    except Exception as e:
        print(f"✗ Report generator import failed: {e}")
        return False
    
    return True

def test_translations():
    """Test translation system."""
    print("\nTesting translations...")
    
    try:
        translator = get_translator()
        
        # Test English translation
        en_text = translator.translate("report.sales.title", locale="en_US")
        print(f"✓ English translation: {en_text}")
        
        # Test Polish translation
        pl_text = translator.translate("report.sales.title", locale="pl_PL")
        print(f"✓ Polish translation: {pl_text}")
        
        # Test parameter substitution
        param_text = translator.translate("header.date_range", 
                                        from_date="2025-01-01", 
                                        to_date="2025-01-31",
                                        locale="en_US")
        print(f"✓ Parameter substitution: {param_text}")
        
        return True
    except Exception as e:
        print(f"✗ Translation test failed: {e}")
        return False

def test_report_configs():
    """Test report configuration loading."""
    print("\nTesting report configurations...")
    
    try:
        generator = ReportGenerator()
        reports = generator.list_available_reports()
        print(f"✓ Available reports: {reports}")
        
        for report_name in reports:
            try:
                info = generator.get_report_info(report_name)
                print(f"✓ Report '{report_name}': {info.get('description', 'No description')}")
            except Exception as e:
                print(f"✗ Report '{report_name}' info failed: {e}")
        
        return True
    except Exception as e:
        print(f"✗ Report config test failed: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection."""
    print("\nTesting MongoDB connection...")
    
    try:
        client = get_mongodb_client()
        if client.connect():
            print("✓ MongoDB connection successful")
            client.disconnect()
            return True
        else:
            print("✗ MongoDB connection failed")
            return False
    except Exception as e:
        print(f"✗ MongoDB connection test failed: {e}")
        return False

def test_template_rendering():
    """Test template rendering."""
    print("\nTesting template rendering...")
    
    try:
        from py_reports.templates import get_template_engine
        
        template_engine = get_template_engine()
        
        # Test simple template
        context = {
            'title': 'Test Report',
            'data': [{'name': 'Item 1', 'value': 100}]
        }
        
        html = template_engine.render_string(
            "<h1>{{ title }}</h1><p>Items: {{ data|length }}</p>",
            context
        )
        print(f"✓ Template rendering: {html[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Template rendering test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("PDF Reports Generator - System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_translations,
        test_report_configs,
        test_mongodb_connection,
        test_template_rendering
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
        print("✓ All tests passed! System is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
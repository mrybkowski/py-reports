#!/usr/bin/env python3
"""Test script for Persons report generation with sample data."""

import sys
from pathlib import Path
from datetime import datetime, date

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from py_reports.renderer import ReportGenerator
from py_reports.templates import get_template_engine
from py_reports.renderer import get_pdf_renderer

def test_persons_report():
    """Test generating Persons report with sample data."""
    print("Testing Persons report generation...")
    
    try:
        # Create sample data based on the provided structure
        sample_persons = [
            {
                "_id": 9,
                "IdAsString": "9",
                "Title": "Mr.",
                "FirstName": "Jan",
                "SecondName": "",
                "LastName": "Brzęczyszczykiewicz",
                "PhoneNumber1": "+48 123 456 789",
                "PhoneNumber2": "",
                "Email": "jan.brzeczyszczykiewicz@example.com",
                "NationalIdentifier": "8222222222",
                "DateOfBirth": "1993-09-06T00:00:00.000Z",
                "Sex": "Male",
                "ImportantInformation": "",
                "FullName": "Brzęczyszczykiewicz Jan",
                "Groups": [
                    "/Polska",
                    "/enigma-admins",
                    "/Czech Republic/PMS EMS Monitorovaci Centrum/PMS SEMS 10101"
                ],
                "Monitorings": [],
                "Addresses": [],
                "Contacts": [],
                "Created": {
                    "Timestamp": "2023-09-20T12:38:52.578Z",
                    "UserId": "2a6ef090-6485-40a8-9d50-96350ee7f979",
                    "UserName": ""
                },
                "Updated": ""
            },
            {
                "_id": 10,
                "IdAsString": "10",
                "Title": "Ms.",
                "FirstName": "Anna",
                "SecondName": "Maria",
                "LastName": "Kowalska",
                "PhoneNumber1": "+48 987 654 321",
                "PhoneNumber2": "+48 111 222 333",
                "Email": "anna.kowalska@example.com",
                "NationalIdentifier": "90010112345",
                "DateOfBirth": "1990-01-01T00:00:00.000Z",
                "Sex": "Female",
                "ImportantInformation": "VIP Client",
                "FullName": "Kowalska Anna Maria",
                "Groups": [
                    "/Polska",
                    "/vip-clients"
                ],
                "Monitorings": [],
                "Addresses": [],
                "Contacts": [],
                "Created": {
                    "Timestamp": "2023-08-15T09:30:15.123Z",
                    "UserId": "3b7ef191-7596-51b9-ae61-07461ff8g080",
                    "UserName": "admin"
                },
                "Updated": "2023-09-01T14:22:10.456Z"
            },
            {
                "_id": 11,
                "IdAsString": "11",
                "Title": "Dr.",
                "FirstName": "Piotr",
                "SecondName": "",
                "LastName": "Nowak",
                "PhoneNumber1": "",
                "PhoneNumber2": "",
                "Email": "",
                "NationalIdentifier": "85031567890",
                "DateOfBirth": "1985-03-15T00:00:00.000Z",
                "Sex": "Male",
                "ImportantInformation": "",
                "FullName": "Nowak Piotr",
                "Groups": [
                    "/Polska",
                    "/doctors"
                ],
                "Monitorings": [],
                "Addresses": [],
                "Contacts": [],
                "Created": {
                    "Timestamp": "2023-07-10T16:45:30.789Z",
                    "UserId": "4c8fg202-8607-62c0-bf72-18572gg9h191",
                    "UserName": "system"
                },
                "Updated": ""
            }
        ]
        
        # Create template context
        context = {
            "report": {
                "main_data": {
                    "raw_data": sample_persons,
                    "row_count": len(sample_persons),
                    "table": {
                        "rows": sample_persons,
                        "totals": {
                            "total_persons": len(sample_persons),
                            "male_count": len([p for p in sample_persons if p.get("Sex") == "Male"]),
                            "female_count": len([p for p in sample_persons if p.get("Sex") == "Female"]),
                            "with_email_count": len([p for p in sample_persons if p.get("Email")])
                        }
                    }
                },
                "parameters": {},
                "generated_at": datetime.now().isoformat(),
                "locale": "pl_PL"
            },
            "config": {
                "columns": [
                    {"name": "IdAsString", "label_key": "persons.id", "align": "center"},
                    {"name": "Title", "label_key": "persons.title", "align": "center"},
                    {"name": "FirstName", "label_key": "persons.first_name", "align": "left"},
                    {"name": "LastName", "label_key": "persons.last_name", "align": "left"},
                    {"name": "FullName", "label_key": "persons.full_name", "align": "left"},
                    {"name": "Email", "label_key": "persons.email", "align": "left"},
                    {"name": "PhoneNumber1", "label_key": "persons.phone1", "align": "left"},
                    {"name": "NationalIdentifier", "label_key": "persons.national_id", "align": "center"},
                    {"name": "DateOfBirth", "label_key": "persons.date_of_birth", "align": "center"},
                    {"name": "Sex", "label_key": "persons.sex", "align": "center"},
                    {"name": "Groups", "label_key": "persons.groups", "align": "left"},
                    {"name": "Created.Timestamp", "label_key": "persons.created", "align": "center"}
                ],
                "summary": {"enabled": True}
            },
            "parameters": {},
            "locale": "pl_PL"
        }
        
        # Generate PDF using template engine directly
        template_engine = get_template_engine(locale="pl_PL")
        pdf_renderer = get_pdf_renderer(locale="pl_PL")
        
        # Render HTML
        html = template_engine.render_template("persons_report.html", context)
        print(f"✓ HTML rendered successfully ({len(html)} characters)")
        
        # Generate PDF
        output_path = Path("output/raport_osob.pdf")
        output_path.parent.mkdir(exist_ok=True)
        
        pdf_path = pdf_renderer.render_pdf_from_string(html, context, output_path)
        print(f"✓ PDF generated: {pdf_path}")
        
        # Check file size
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✓ File size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating Persons report: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("PDF Reports Generator - Persons Report Test")
    print("=" * 50)
    
    if test_persons_report():
        print("\n✓ Persons report test successful!")
        return 0
    else:
        print("\n✗ Persons report test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
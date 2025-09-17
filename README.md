# PDF Reports Generator

A comprehensive system for generating PDF reports from MongoDB data with support for:

- Headers and footers
- Regular tables and pivot tables
- Subreports
- Multi-language support with translation packages
- Parameterized queries

## Features

- **MongoDB Integration**: Direct queries and aggregation pipelines
- **PDF Generation**: High-quality PDF output with WeasyPrint
- **Multi-language**: i18n support with YAML translation packages
- **Flexible Templates**: Jinja2-based HTML/CSS templates
- **CLI & API**: Both command-line and REST API interfaces
- **Performance**: Optimized for large datasets (100k+ rows)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd py-reports

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=reports_db
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password

# Report Configuration
REPORTS_DIR=reports
TEMPLATES_DIR=py_reports/templates
TRANSLATIONS_DIR=py_reports/translations
OUTPUT_DIR=output

# Performance Settings
MAX_ROWS_PER_TABLE=100000
MAX_COLUMNS_PER_PIVOT=200
MAX_GENERATION_TIME=60

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## Quick Start

### CLI Usage

```bash
# List available reports
python -m py_reports.cli list-reports

# Generate a sales report
python -m py_reports.cli run sales \
  --params date_from=2025-01-01 date_to=2025-01-31 \
  --locale pl_PL \
  --output sales_report.pdf

# Test report generation
python -m py_reports.cli test sales \
  --params date_from=2025-01-01 date_to=2025-01-31

# Get report information
python -m py_reports.cli info sales
```

### API Usage

```bash
# Start the API server
python -m py_reports.cli serve

# Or start directly
python -m py_reports.api
```

Then access the API at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Python API

```python
from py_reports.renderer import ReportGenerator

# Create generator
generator = ReportGenerator(locale="en_US")

# Generate report
pdf_path = generator.generate_report(
    report_name="sales",
    parameters={
        "date_from": "2025-01-01",
        "date_to": "2025-01-31"
    },
    output_path="sales_report.pdf"
)
```

## Report Configuration

Reports are defined in YAML files in the `reports/` directory:

```yaml
# reports/sales.yaml
name: "sales"
description: "Monthly sales analysis report"
collection: "sales"

# MongoDB aggregation pipeline
pipeline:
  - $match:
      date:
        $gte: "{{date_from}}"
        $lte: "{{date_to}}"
  - $lookup:
      from: "customers"
      localField: "customer_id"
      foreignField: "_id"
      as: "customer"
  # ... more pipeline stages

# Table columns
columns:
  - label: "report.sales.columns.date"
    field: "date"
    type: "date"
    align: "left"
  - label: "report.sales.columns.customer"
    field: "customer_name"
    type: "string"
    align: "left"
  - label: "report.sales.columns.amount"
    field: "net_amount"
    type: "currency"
    format: "PLN"
    align: "right"

# Pivot table configuration
pivot:
  rows: ["customer_name"]
  columns: ["product_name"]
  measures:
    - name: "total_amount"
      field: "net_amount"
      type: "sum"
  show_totals: true
  show_grand_total: true

# Template
template: "sales_report.html"

# Parameters
parameters:
  date_from:
    type: "date"
    required: true
  date_to:
    type: "date"
    required: true
```

## Templates

Templates use Jinja2 with custom filters:

```html
<!-- templates/sales_report.html -->
{% extends "base.html" %} {% block content %}
<h1>{{ t('report.sales.title') }}</h1>

<table class="table">
  <thead>
    <tr>
      {% for header in report.main_data.table.headers %}
      <th>{{ t(header.label) }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for row in report.main_data.table.rows %}
    <tr>
      {% for header in report.main_data.table.headers %}
      <td>{{ row[header.field].formatted_value }}</td>
      {% endfor %}
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

## Translations

Translation files are in YAML format:

```yaml
# translations/en_US.yaml
report:
  sales:
    title: "Sales Report"
    columns:
      date: "Date"
      customer: "Customer"
      amount: "Amount"

# translations/pl_PL.yaml
report:
  sales:
    title: "Raport sprzedaży"
    columns:
      date: "Data"
      customer: "Kontrahent"
      amount: "Kwota"
```

## Testing

```bash
# Run system tests
python test_system.py

# Run examples
python example_usage.py

# Run with pytest (if installed)
pytest tests/
```

## Project Structure

```
py-reports/
├── py_reports/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── api.py              # FastAPI server
│   ├── config/             # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── report_config.py
│   ├── data/               # MongoDB data access
│   │   ├── __init__.py
│   │   ├── mongodb_client.py
│   │   ├── query_executor.py
│   │   └── pipeline_builder.py
│   ├── templates/          # Jinja2 templates
│   │   ├── __init__.py
│   │   ├── template_engine.py
│   │   ├── filters.py
│   │   ├── base.html
│   │   ├── base.css
│   │   ├── sales_report.html
│   │   └── inventory_report.html
│   ├── translations/       # i18n translation packages
│   │   ├── __init__.py
│   │   ├── translator.py
│   │   ├── locale_manager.py
│   │   ├── en_US.yaml
│   │   └── pl_PL.yaml
│   ├── transforms/         # Data transformations
│   │   ├── __init__.py
│   │   ├── table_transformer.py
│   │   ├── pivot_transformer.py
│   │   ├── data_formatter.py
│   │   └── subreport_processor.py
│   └── renderer/           # PDF rendering
│       ├── __init__.py
│       ├── pdf_renderer.py
│       └── report_generator.py
├── reports/                # Report definitions
│   ├── sales.yaml
│   └── inventory.yaml
├── tests/                  # Test suite
├── output/                 # Generated reports
├── requirements.txt
├── setup.py
├── test_system.py
├── example_usage.py
└── README.md
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /reports` - List available reports
- `GET /reports/{name}/info` - Get report information
- `GET /reports/{name}/validate` - Validate report configuration
- `POST /reports/{name}/render` - Generate report
- `POST /reports/{name}/render/download` - Download report as PDF
- `POST /reports/{name}/test` - Test report generation
- `GET /reports/{name}/sample` - Get sample data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

"""Command-line interface for PDF report generation."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import click
from datetime import datetime
from .renderer import ReportGenerator
from .config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--locale', default='en_US', help='Default locale for reports')
@click.pass_context
def cli(ctx, verbose, locale):
    """PDF Reports Generator - Generate PDF reports from MongoDB data."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    ctx.ensure_object(dict)
    ctx.obj['locale'] = locale


@cli.command()
@click.argument('report_name')
@click.option('--params', '-p', multiple=True, help='Report parameters (key=value)')
@click.option('--locale', '-l', default='en_US', help='Report locale')
@click.option('--output', '-o', help='Output file path')
@click.option('--validate-only', is_flag=True, help='Only validate report configuration')
@click.pass_context
def run(ctx, report_name, params, locale, output, validate_only):
    """Generate a report."""
    try:
        # Parse parameters
        parameters = {}
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                parameters[key] = value
            else:
                click.echo(f"Warning: Invalid parameter format: {param}", err=True)
        
        # Create report generator
        generator = ReportGenerator(locale)
        
        if validate_only:
            # Validate report configuration
            validation = generator.validate_report_config(report_name)
            
            if validation['valid']:
                click.echo(f"✓ Report '{report_name}' configuration is valid")
                click.echo(f"  Template: {validation['config']['template']}")
                click.echo(f"  Collection: {validation['config']['collection']}")
                click.echo(f"  Columns: {validation['config']['column_count']}")
                click.echo(f"  Subreports: {validation['config']['subreport_count']}")
            else:
                click.echo(f"✗ Report '{report_name}' configuration is invalid", err=True)
                if 'error' in validation:
                    click.echo(f"  Error: {validation['error']}", err=True)
                sys.exit(1)
        else:
            # Generate report
            click.echo(f"Generating report '{report_name}'...")
            
            if output:
                output_path = Path(output)
                result = generator.generate_report(report_name, parameters, output_path)
                click.echo(f"✓ Report saved to: {output_path}")
            else:
                # Generate to default output directory
                settings = get_settings()
                output_dir = Path(settings.output_dir)
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"{report_name}_{timestamp}.pdf"
                
                result = generator.generate_report(report_name, parameters, output_path)
                click.echo(f"✓ Report saved to: {output_path}")
    
    except Exception as e:
        click.echo(f"✗ Error generating report: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.option('--locale', '-l', default='en_US', help='Report locale')
def list_reports(locale):
    """List available reports."""
    try:
        generator = ReportGenerator(locale)
        reports = generator.list_available_reports()
        
        if not reports:
            click.echo("No reports found")
            return
        
        click.echo("Available reports:")
        for report_name in reports:
            try:
                info = generator.get_report_info(report_name)
                click.echo(f"  {report_name}: {info.get('description', 'No description')}")
            except Exception:
                click.echo(f"  {report_name}: (error loading info)")
    
    except Exception as e:
        click.echo(f"✗ Error listing reports: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('report_name')
@click.option('--locale', '-l', default='en_US', help='Report locale')
def info(report_name, locale):
    """Show detailed information about a report."""
    try:
        generator = ReportGenerator(locale)
        info = generator.get_report_info(report_name)
        
        if 'error' in info:
            click.echo(f"✗ Error: {info['error']}", err=True)
            sys.exit(1)
        
        click.echo(f"Report: {info['name']}")
        click.echo(f"Description: {info['description']}")
        click.echo(f"Collection: {info['collection']}")
        click.echo(f"Template: {info['template']}")
        click.echo(f"Columns: {info['column_count']}")
        click.echo(f"Subreports: {info['subreport_count']}")
        click.echo(f"Has Pivot: {'Yes' if info['has_pivot'] else 'No'}")
        
        if info['parameters']:
            click.echo("Parameters:")
            for param in info['parameters']:
                click.echo(f"  - {param}")
    
    except Exception as e:
        click.echo(f"✗ Error getting report info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('report_name')
@click.option('--params', '-p', multiple=True, help='Report parameters (key=value)')
@click.option('--locale', '-l', default='en_US', help='Report locale')
def test(report_name, params, locale):
    """Test report generation without saving output."""
    try:
        # Parse parameters
        parameters = {}
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                parameters[key] = value
        
        generator = ReportGenerator(locale)
        result = generator.test_report_generation(report_name, parameters)
        
        if result['success']:
            click.echo(f"✓ Report generation test successful")
            click.echo(f"  PDF size: {result['pdf_info']['size_mb']} MB")
            click.echo(f"  Generated at: {result['pdf_info']['created_at']}")
        else:
            click.echo(f"✗ Report generation test failed: {result['error']}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"✗ Error testing report: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('report_name')
@click.option('--size', '-s', default=100, help='Sample size')
@click.option('--locale', '-l', default='en_US', help='Report locale')
def sample(report_name, size, locale):
    """Generate sample data for a report."""
    try:
        generator = ReportGenerator(locale)
        result = generator.generate_sample_data(report_name, size)
        
        if result['success']:
            click.echo(f"✓ Sample data generated")
            click.echo(f"  Collection: {result['collection']}")
            click.echo(f"  Sample size: {result['sample_size']}")
            
            # Show first few records
            if result['sample_data']:
                click.echo("\nFirst 3 records:")
                for i, record in enumerate(result['sample_data'][:3]):
                    click.echo(f"  Record {i+1}: {record}")
        else:
            click.echo(f"✗ Error generating sample data: {result['error']}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"✗ Error generating sample data: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='API server host')
@click.option('--port', default=8000, help='API server port')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def serve(host, port, reload):
    """Start the API server."""
    try:
        import uvicorn
        from .api import app
        
        click.echo(f"Starting API server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, reload=reload)
    
    except ImportError:
        click.echo("✗ uvicorn not installed. Install with: pip install uvicorn", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error starting server: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"PDF Reports Generator v{__version__}")


if __name__ == '__main__':
    cli()
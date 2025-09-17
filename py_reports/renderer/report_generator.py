"""Main report generator that orchestrates the entire process."""

import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from ..config import get_settings, ReportConfig, load_report_config
from ..data import get_mongodb_client, QueryExecutor
from ..transforms import TableTransformer, PivotTransformer, SubreportProcessor
from ..templates import get_template_engine
from .pdf_renderer import get_pdf_renderer

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Main report generator that orchestrates the entire process."""
    
    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        self.settings = get_settings()
        self.mongodb_client = get_mongodb_client()
        self.query_executor = QueryExecutor(self.mongodb_client)
        self.table_transformer = TableTransformer(locale)
        self.pivot_transformer = PivotTransformer(locale)
        self.subreport_processor = SubreportProcessor(self.query_executor)
        self.template_engine = get_template_engine(locale=locale)
        self.pdf_renderer = get_pdf_renderer(locale=locale)
    
    def generate_report(self, report_name: str, parameters: Dict[str, Any] = None,
                       output_path: Optional[Union[str, Path]] = None) -> Union[bytes, Path]:
        """
        Generate a complete report.
        
        Args:
            report_name: Name of the report configuration
            parameters: Report parameters
            output_path: Output file path (if None, returns bytes)
            
        Returns:
            PDF bytes or output file path
        """
        try:
            logger.info(f"Starting report generation: {report_name}")
            start_time = datetime.now()
            
            # Load report configuration
            report_config = load_report_config(report_name, self.settings.reports_dir)
            
            # Validate parameters
            validated_params = self.query_executor.validate_parameters(
                parameters or {}, report_config.parameters
            )
            
            # Connect to MongoDB
            if not self.mongodb_client.connect():
                raise ConnectionError("Failed to connect to MongoDB")
            
            try:
                # Execute main report query
                main_data = self.query_executor.execute_report_query(
                    report_config.collection,
                    report_config.pipeline,
                    validated_params
                )
                
                # Process main data
                processed_data = self._process_main_data(main_data, report_config)
                
                # Process subreports
                subreports = self._process_subreports(report_config, validated_params)
                
                # Create report data structure
                report_data = {
                    'main_data': processed_data,
                    'subreports': subreports,
                    'parameters': validated_params,
                    'generated_at': datetime.now().isoformat(),
                    'locale': self.locale
                }
                
                # Generate PDF
                pdf_result = self.pdf_renderer.render_report(
                    report_data,
                    report_config.dict(),
                    validated_params,
                    output_path
                )
                
                # Log generation time
                generation_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Report generation completed in {generation_time:.2f} seconds")
                
                return pdf_result
                
            finally:
                # Disconnect from MongoDB
                self.mongodb_client.disconnect()
                
        except Exception as e:
            logger.error(f"Failed to generate report {report_name}: {e}")
            raise
    
    def _process_main_data(self, data: list, report_config: ReportConfig) -> Dict[str, Any]:
        """Process main report data."""
        processed_data = {
            'raw_data': data,
            'row_count': len(data)
        }
        
        # Process regular table if columns are defined
        if report_config.columns:
            table_data = self.table_transformer.transform_table_data(
                data, report_config.columns
            )
            processed_data['table'] = table_data
        
        # Process pivot table if configured
        if report_config.pivot:
            pivot_data = self.pivot_transformer.transform_pivot_data(
                data, report_config.pivot
            )
            processed_data['pivot'] = pivot_data
        
        # Process summary if configured
        if report_config.summary and report_config.summary.enabled:
            summary_data = self._process_summary(data, report_config.summary)
            processed_data['summary'] = summary_data
        
        return processed_data
    
    def _process_summary(self, data: list, summary_config) -> Dict[str, Any]:
        """Process summary statistics based on configuration."""
        summary = {}
        
        for field in summary_config.fields:
            field_name = field.name
            field_type = field.type
            field_filter = getattr(field, 'filter', None)
            
            if field_type == "count":
                if field_filter:
                    # Apply filter
                    filtered_data = self._apply_filter(data, field_filter)
                    summary[field_name] = len(filtered_data)
                else:
                    summary[field_name] = len(data)
            else:
                # For other types, just count for now
                summary[field_name] = len(data)
        
        return summary
    
    def _apply_filter(self, data: list, filter_str: str) -> list:
        """Apply filter to data."""
        if not filter_str:
            return data
        
        filtered_data = []
        for row in data:
            if self._matches_filter(row, filter_str):
                filtered_data.append(row)
        
        return filtered_data
    
    def _matches_filter(self, row: dict, filter_str: str) -> bool:
        """Check if row matches filter."""
        if ":" not in filter_str:
            return True
        
        field, condition = filter_str.split(":", 1)
        
        # Get nested value
        value = self._get_nested_value(row, field)
        
        if condition == "!=":
            return value is not None and value != ""
        elif condition.startswith("="):
            return str(value) == condition[1:]
        elif condition.startswith("!="):
            return str(value) != condition[2:]
        else:
            return str(value) == condition
    
    def _get_nested_value(self, row: dict, field: str) -> Any:
        """Get nested value from row."""
        if "." in field:
            parts = field.split(".")
            value = row
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        else:
            return row.get(field)
    
    def _process_subreports(self, report_config: ReportConfig, 
                          parameters: Dict[str, Any]) -> list:
        """Process subreports."""
        if not report_config.subreports:
            return []
        
        # Create parent context for subreports
        parent_context = {
            'parameters': parameters,
            'main_data_count': len(parameters.get('main_data', [])),
            'generated_at': datetime.now().isoformat()
        }
        
        # Process each subreport
        subreports = self.subreport_processor.process_multiple_subreports(
            report_config.subreports,
            parent_context,
            report_config.collection
        )
        
        return subreports
    
    def validate_report_config(self, report_name: str) -> Dict[str, Any]:
        """Validate report configuration."""
        try:
            report_config = load_report_config(report_name, self.settings.reports_dir)
            
            # Validate template
            template_valid = self.template_engine.validate_template(report_config.template)
            
            # Validate MongoDB connection
            mongodb_valid = self.mongodb_client.connect()
            if mongodb_valid:
                self.mongodb_client.disconnect()
            
            # Validate collection exists
            collection_exists = False
            if mongodb_valid:
                if self.mongodb_client.connect():
                    collections = self.mongodb_client.list_collections()
                    collection_exists = report_config.collection in collections
                    self.mongodb_client.disconnect()
            
            return {
                'valid': template_valid['valid'] and mongodb_valid and collection_exists,
                'report_name': report_name,
                'template_valid': template_valid,
                'mongodb_connected': mongodb_valid,
                'collection_exists': collection_exists,
                'config': report_config.dict()
            }
            
        except Exception as e:
            return {
                'valid': False,
                'report_name': report_name,
                'error': str(e),
                'message': f'Validation failed: {e}'
            }
    
    def list_available_reports(self) -> list:
        """List all available reports."""
        try:
            from ..config.report_config import list_available_reports
            return list_available_reports(self.settings.reports_dir)
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []
    
    def get_report_info(self, report_name: str) -> Dict[str, Any]:
        """Get information about a specific report."""
        try:
            report_config = load_report_config(report_name, self.settings.reports_dir)
            
            return {
                'name': report_config.name,
                'description': report_config.description,
                'collection': report_config.collection,
                'template': report_config.template,
                'has_columns': len(report_config.columns) > 0,
                'has_pivot': report_config.pivot is not None,
                'has_subreports': len(report_config.subreports) > 0,
                'parameters': list(report_config.parameters.keys()),
                'column_count': len(report_config.columns),
                'subreport_count': len(report_config.subreports)
            }
            
        except Exception as e:
            logger.error(f"Failed to get report info for {report_name}: {e}")
            return {'error': str(e)}
    
    def test_report_generation(self, report_name: str, 
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test report generation without saving output."""
        try:
            # Generate report to bytes
            pdf_bytes = self.generate_report(report_name, parameters)
            
            # Get PDF info
            pdf_info = self.pdf_renderer.get_pdf_info(pdf_bytes)
            
            return {
                'success': True,
                'report_name': report_name,
                'pdf_info': pdf_info,
                'message': 'Report generation test successful'
            }
            
        except Exception as e:
            logger.error(f"Report generation test failed for {report_name}: {e}")
            return {
                'success': False,
                'report_name': report_name,
                'error': str(e),
                'message': f'Report generation test failed: {e}'
            }
    
    def generate_sample_data(self, report_name: str, 
                           sample_size: int = 100) -> Dict[str, Any]:
        """Generate sample data for testing."""
        try:
            report_config = load_report_config(report_name, self.settings.reports_dir)
            
            # Connect to MongoDB
            if not self.mongodb_client.connect():
                raise ConnectionError("Failed to connect to MongoDB")
            
            try:
                # Get sample data
                sample_data = self.query_executor.execute_simple_query(
                    report_config.collection,
                    limit=sample_size
                )
                
                return {
                    'success': True,
                    'sample_data': sample_data,
                    'sample_size': len(sample_data),
                    'collection': report_config.collection
                }
                
            finally:
                self.mongodb_client.disconnect()
                
        except Exception as e:
            logger.error(f"Failed to generate sample data for {report_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to generate sample data: {e}'
            }
"""Table data transformation and formatting."""

import logging
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal
from datetime import datetime, date
from .data_formatter import DataFormatter
from ..config.report_config import ColumnConfig

logger = logging.getLogger(__name__)


class TableTransformer:
    """Transforms raw data into formatted table data."""
    
    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        self.formatter = DataFormatter(locale)
    
    def transform_table_data(self, data: List[Dict[str, Any]], 
                           columns: List[ColumnConfig]) -> Dict[str, Any]:
        """
        Transform raw data into formatted table data.
        
        Args:
            data: Raw data from MongoDB
            columns: Column configuration
            
        Returns:
            Formatted table data with headers and rows
        """
        try:
            # Prepare table headers
            headers = self._prepare_headers(columns)
            
            # Transform data rows
            rows = self._transform_rows(data, columns)
            
            # Calculate totals if needed
            totals = self._calculate_totals(data, columns)
            
            # Prepare summary statistics
            summary = self._prepare_summary(data, columns)
            
            return {
                'headers': headers,
                'rows': rows,
                'totals': totals,
                'summary': summary,
                'row_count': len(rows),
                'column_count': len(columns)
            }
            
        except Exception as e:
            logger.error(f"Failed to transform table data: {e}")
            raise
    
    def _prepare_headers(self, columns: List[ColumnConfig]) -> List[Dict[str, Any]]:
        """Prepare table headers from column configuration."""
        headers = []
        
        for col in columns:
            header = {
                'label': col.label,
                'field': col.field,
                'type': col.type,
                'align': col.align,
                'width': col.width,
                'sortable': True,  # Could be configurable
                'filterable': True  # Could be configurable
            }
            headers.append(header)
        
        return headers
    
    def _transform_rows(self, data: List[Dict[str, Any]], 
                       columns: List[ColumnConfig]) -> List[Dict[str, Any]]:
        """Transform data rows with formatting."""
        rows = []
        
        for index, row_data in enumerate(data, 1):
            row = {}
            
            for col in columns:
                field_value = self._get_nested_value(row_data, col.field)
                
                # Special handling for "No" field - use row number starting from 1
                if col.field == "No":
                    field_value = index
                
                formatted_value = self._format_cell_value(field_value, col)
                
                row[col.field] = {
                    'raw_value': field_value,
                    'formatted_value': formatted_value,
                    'type': col.type,
                    'align': col.align
                }
            
            rows.append(row)
        
        return rows
    
    def _format_cell_value(self, value: Any, column: ColumnConfig) -> str:
        """Format cell value according to column configuration."""
        if value is None:
            return ""
        
        try:
            if column.type == "string":
                return str(value)
            elif column.type == "number":
                return self.formatter.format_number(value, column.format)
            elif column.type == "currency":
                currency = column.format or "USD"
                return self.formatter.format_currency(value, currency)
            elif column.type == "date":
                return self.formatter.format_date(value, column.format)
            elif column.type == "datetime":
                return self.formatter.format_datetime(value, column.format)
            elif column.type == "percentage":
                return self.formatter.format_percentage(value, column.format)
            elif column.type == "boolean":
                return self.formatter.format_boolean(value)
            else:
                return str(value)
                
        except Exception as e:
            logger.warning(f"Failed to format value {value} for column {column.field}: {e}")
            return str(value)
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value from data using dot notation."""
        try:
            value = data
            for part in field_path.split('.'):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        except Exception:
            return None
    
    def _calculate_totals(self, data: List[Dict[str, Any]], 
                         columns: List[ColumnConfig]) -> Dict[str, Any]:
        """Calculate column totals for numeric fields."""
        totals = {}
        
        for col in columns:
            if col.type in ["number", "currency"]:
                try:
                    values = []
                    for row in data:
                        value = self._get_nested_value(row, col.field)
                        if value is not None:
                            try:
                                values.append(float(value))
                            except (ValueError, TypeError):
                                pass
                    
                    if values:
                        totals[col.field] = {
                            'sum': sum(values),
                            'avg': sum(values) / len(values),
                            'min': min(values),
                            'max': max(values),
                            'count': len(values)
                        }
                except Exception as e:
                    logger.warning(f"Failed to calculate totals for column {col.field}: {e}")
        
        return totals
    
    def _prepare_summary(self, data: List[Dict[str, Any]], 
                        columns: List[ColumnConfig]) -> Dict[str, Any]:
        """Prepare summary statistics."""
        summary = {
            'total_rows': len(data),
            'columns': len(columns),
            'numeric_columns': len([col for col in columns if col.type in ["number", "currency"]]),
            'date_columns': len([col for col in columns if col.type in ["date", "datetime"]]),
            'text_columns': len([col for col in columns if col.type == "string"])
        }
        
        return summary
    
    def group_data(self, data: List[Dict[str, Any]], 
                  group_by: List[str], 
                  aggregations: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Group data by specified fields with aggregations.
        
        Args:
            data: Raw data
            group_by: Fields to group by
            aggregations: Field aggregations (field: operation)
            
        Returns:
            Grouped data
        """
        groups = {}
        
        for row in data:
            # Create group key
            group_key = tuple(self._get_nested_value(row, field) for field in group_by)
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(row)
        
        # Process groups
        grouped_data = []
        for group_key, group_rows in groups.items():
            group_row = {}
            
            # Add group fields
            for i, field in enumerate(group_by):
                group_row[field] = group_key[i]
            
            # Add aggregations
            if aggregations:
                for field, operation in aggregations.items():
                    values = [self._get_nested_value(row, field) for row in group_rows]
                    numeric_values = [v for v in values if v is not None and isinstance(v, (int, float, Decimal))]
                    
                    if operation == "sum" and numeric_values:
                        group_row[f"{field}_sum"] = sum(numeric_values)
                    elif operation == "avg" and numeric_values:
                        group_row[f"{field}_avg"] = sum(numeric_values) / len(numeric_values)
                    elif operation == "count":
                        group_row[f"{field}_count"] = len(values)
                    elif operation == "min" and numeric_values:
                        group_row[f"{field}_min"] = min(numeric_values)
                    elif operation == "max" and numeric_values:
                        group_row[f"{field}_max"] = max(numeric_values)
            
            group_row['_group_size'] = len(group_rows)
            grouped_data.append(group_row)
        
        return grouped_data
    
    def sort_data(self, data: List[Dict[str, Any]], 
                 sort_fields: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Sort data by specified fields.
        
        Args:
            data: Data to sort
            sort_fields: Field names and sort directions ("asc" or "desc")
            
        Returns:
            Sorted data
        """
        def sort_key(row):
            key_values = []
            for field, direction in sort_fields.items():
                value = self._get_nested_value(row, field)
                if value is None:
                    value = ""
                
                # Convert to appropriate type for sorting
                if isinstance(value, str):
                    try:
                        # Try to convert to number for numeric sorting
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                
                key_values.append(value)
            
            return key_values
        
        try:
            return sorted(data, key=sort_key, 
                        reverse=any(direction.lower() == "desc" for direction in sort_fields.values()))
        except Exception as e:
            logger.warning(f"Failed to sort data: {e}")
            return data
    
    def filter_data(self, data: List[Dict[str, Any]], 
                   filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter data based on criteria.
        
        Args:
            data: Data to filter
            filters: Filter criteria
            
        Returns:
            Filtered data
        """
        filtered_data = []
        
        for row in data:
            include_row = True
            
            for field, criteria in filters.items():
                value = self._get_nested_value(row, field)
                
                if isinstance(criteria, dict):
                    # Complex criteria
                    if "$eq" in criteria and value != criteria["$eq"]:
                        include_row = False
                        break
                    elif "$ne" in criteria and value == criteria["$ne"]:
                        include_row = False
                        break
                    elif "$gt" in criteria and not (value and value > criteria["$gt"]):
                        include_row = False
                        break
                    elif "$lt" in criteria and not (value and value < criteria["$lt"]):
                        include_row = False
                        break
                    elif "$in" in criteria and value not in criteria["$in"]:
                        include_row = False
                        break
                    elif "$nin" in criteria and value in criteria["$nin"]:
                        include_row = False
                        break
                else:
                    # Simple equality
                    if value != criteria:
                        include_row = False
                        break
            
            if include_row:
                filtered_data.append(row)
        
        return filtered_data
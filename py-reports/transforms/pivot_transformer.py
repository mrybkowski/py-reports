"""Pivot table transformation and generation."""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from collections import defaultdict, OrderedDict
from decimal import Decimal
from .data_formatter import DataFormatter
from ..config.report_config import PivotConfig

logger = logging.getLogger(__name__)


class PivotTransformer:
    """Transforms data into pivot table format."""
    
    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        self.formatter = DataFormatter(locale)
    
    def transform_pivot_data(self, data: List[Dict[str, Any]], 
                           pivot_config: PivotConfig) -> Dict[str, Any]:
        """
        Transform data into pivot table format.
        
        Args:
            data: Raw data from MongoDB
            pivot_config: Pivot table configuration
            
        Returns:
            Formatted pivot table data
        """
        try:
            # Extract unique values for rows and columns
            row_values = self._extract_unique_values(data, pivot_config.rows)
            column_values = self._extract_unique_values(data, pivot_config.columns)
            
            # Limit columns if needed
            if len(column_values) > pivot_config.max_columns:
                column_values = column_values[:pivot_config.max_columns]
                logger.warning(f"Limited columns to {pivot_config.max_columns}")
            
            # Create pivot matrix
            pivot_matrix = self._create_pivot_matrix(
                data, pivot_config, row_values, column_values
            )
            
            # Generate pivot table structure
            pivot_table = self._generate_pivot_table(
                pivot_matrix, row_values, column_values, pivot_config
            )
            
            # Calculate totals
            totals = self._calculate_pivot_totals(
                pivot_table, pivot_config, row_values, column_values
            )
            
            return {
                'pivot_table': pivot_table,
                'row_values': row_values,
                'column_values': column_values,
                'totals': totals,
                'config': {
                    'rows': pivot_config.rows,
                    'columns': pivot_config.columns,
                    'measures': pivot_config.measures,
                    'show_totals': pivot_config.show_totals,
                    'show_grand_total': pivot_config.show_grand_total
                },
                'summary': {
                    'row_count': len(row_values),
                    'column_count': len(column_values),
                    'cell_count': len(row_values) * len(column_values)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to transform pivot data: {e}")
            raise
    
    def _extract_unique_values(self, data: List[Dict[str, Any]], 
                              fields: List[str]) -> List[Any]:
        """Extract unique values for pivot dimensions."""
        unique_values = set()
        
        for row in data:
            # Create composite key for multiple fields
            if len(fields) == 1:
                value = self._get_nested_value(row, fields[0])
                if value is not None:
                    unique_values.add(value)
            else:
                # Multiple fields - create tuple key
                key_parts = []
                for field in fields:
                    value = self._get_nested_value(row, field)
                    key_parts.append(value if value is not None else "")
                unique_values.add(tuple(key_parts))
        
        # Sort values
        sorted_values = sorted(unique_values)
        return sorted_values
    
    def _create_pivot_matrix(self, data: List[Dict[str, Any]], 
                           pivot_config: PivotConfig,
                           row_values: List[Any], 
                           column_values: List[Any]) -> Dict[Tuple, Dict[str, Any]]:
        """Create pivot matrix with aggregated values."""
        matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        for row in data:
            # Get row key
            row_key = self._get_row_key(row, pivot_config.rows)
            if row_key not in row_values:
                continue
            
            # Get column key
            column_key = self._get_column_key(row, pivot_config.columns)
            if column_key not in column_values:
                continue
            
            # Aggregate measures
            for measure in pivot_config.measures:
                measure_name = measure.get('name', 'value')
                measure_field = measure.get('field', 'value')
                measure_type = measure.get('type', 'sum')
                
                value = self._get_nested_value(row, measure_field)
                if value is not None:
                    try:
                        numeric_value = float(value)
                        matrix[row_key][column_key][measure_name] += numeric_value
                    except (ValueError, TypeError):
                        pass
        
        return dict(matrix)
    
    def _get_row_key(self, row: Dict[str, Any], row_fields: List[str]) -> Any:
        """Get row key from data row."""
        if len(row_fields) == 1:
            return self._get_nested_value(row, row_fields[0])
        else:
            return tuple(
                self._get_nested_value(row, field) for field in row_fields
            )
    
    def _get_column_key(self, row: Dict[str, Any], column_fields: List[str]) -> Any:
        """Get column key from data row."""
        if len(column_fields) == 1:
            return self._get_nested_value(row, column_fields[0])
        else:
            return tuple(
                self._get_nested_value(row, field) for field in column_fields
            )
    
    def _generate_pivot_table(self, matrix: Dict[Tuple, Dict[str, Any]], 
                            row_values: List[Any], 
                            column_values: List[Any],
                            pivot_config: PivotConfig) -> List[Dict[str, Any]]:
        """Generate pivot table structure."""
        pivot_table = []
        
        for row_value in row_values:
            row_data = {
                'row_key': row_value,
                'row_label': self._format_row_label(row_value, pivot_config.rows),
                'cells': {},
                'row_totals': {}
            }
            
            # Calculate row totals
            row_total = defaultdict(float)
            
            for column_value in column_values:
                cell_data = matrix.get(row_value, {}).get(column_value, {})
                row_data['cells'][column_value] = cell_data
                
                # Add to row totals
                for measure in pivot_config.measures:
                    measure_name = measure.get('name', 'value')
                    row_total[measure_name] += cell_data.get(measure_name, 0)
            
            # Format row totals
            for measure in pivot_config.measures:
                measure_name = measure.get('name', 'value')
                measure_type = measure.get('type', 'sum')
                row_data['row_totals'][measure_name] = self._format_measure_value(
                    row_total[measure_name], measure_type
                )
            
            pivot_table.append(row_data)
        
        return pivot_table
    
    def _format_row_label(self, row_value: Any, row_fields: List[str]) -> str:
        """Format row label for display."""
        if isinstance(row_value, tuple):
            return " - ".join(str(v) if v is not None else "" for v in row_value)
        else:
            return str(row_value) if row_value is not None else ""
    
    def _format_measure_value(self, value: float, measure_type: str) -> str:
        """Format measure value for display."""
        if measure_type == "avg" and value != 0:
            # For averages, we might need to divide by count
            # This is a simplified version
            return self.formatter.format_number(value)
        else:
            return self.formatter.format_number(value)
    
    def _calculate_pivot_totals(self, pivot_table: List[Dict[str, Any]], 
                              pivot_config: PivotConfig,
                              row_values: List[Any], 
                              column_values: List[Any]) -> Dict[str, Any]:
        """Calculate column totals and grand totals."""
        totals = {
            'column_totals': {},
            'grand_totals': {},
            'row_totals': []
        }
        
        if not pivot_config.show_totals:
            return totals
        
        # Calculate column totals
        column_totals = defaultdict(float)
        grand_totals = defaultdict(float)
        
        for row_data in pivot_table:
            for column_value in column_values:
                cell_data = row_data['cells'].get(column_value, {})
                for measure in pivot_config.measures:
                    measure_name = measure.get('name', 'value')
                    value = cell_data.get(measure_name, 0)
                    column_totals[(column_value, measure_name)] += value
                    grand_totals[measure_name] += value
        
        # Format column totals
        for (column_value, measure_name), total in column_totals.items():
            if column_value not in totals['column_totals']:
                totals['column_totals'][column_value] = {}
            totals['column_totals'][column_value][measure_name] = self._format_measure_value(
                total, next(m.get('type', 'sum') for m in pivot_config.measures 
                          if m.get('name') == measure_name)
            )
        
        # Format grand totals
        for measure in pivot_config.measures:
            measure_name = measure.get('name', 'value')
            measure_type = measure.get('type', 'sum')
            totals['grand_totals'][measure_name] = self._format_measure_value(
                grand_totals[measure_name], measure_type
            )
        
        # Add row totals to totals structure
        totals['row_totals'] = [
            {
                'row_key': row_data['row_key'],
                'row_label': row_data['row_label'],
                'totals': row_data['row_totals']
            }
            for row_data in pivot_table
        ]
        
        return totals
    
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
    
    def create_pivot_summary(self, pivot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary statistics for pivot table."""
        pivot_table = pivot_data['pivot_table']
        measures = pivot_data['config']['measures']
        
        summary = {
            'total_rows': len(pivot_table),
            'total_columns': len(pivot_data['column_values']),
            'measures': {}
        }
        
        # Calculate measure statistics
        for measure in measures:
            measure_name = measure.get('name', 'value')
            measure_type = measure.get('type', 'sum')
            
            all_values = []
            for row_data in pivot_table:
                for cell_data in row_data['cells'].values():
                    value = cell_data.get(measure_name, 0)
                    if value != 0:
                        all_values.append(value)
            
            if all_values:
                summary['measures'][measure_name] = {
                    'type': measure_type,
                    'total': sum(all_values),
                    'average': sum(all_values) / len(all_values),
                    'min': min(all_values),
                    'max': max(all_values),
                    'count': len(all_values)
                }
        
        return summary
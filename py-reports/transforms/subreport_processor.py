"""Subreport processing and context management."""

import logging
from typing import Dict, Any, List, Optional
from ..data.query_executor import QueryExecutor
from ..config.report_config import SubreportConfig

logger = logging.getLogger(__name__)


class SubreportProcessor:
    """Processes subreports with context parameter passing."""
    
    def __init__(self, query_executor: QueryExecutor):
        self.query_executor = query_executor
    
    def process_subreport(self, subreport_config: SubreportConfig, 
                         parent_context: Dict[str, Any],
                         collection_name: str) -> Dict[str, Any]:
        """
        Process a subreport with context from parent report.
        
        Args:
            subreport_config: Subreport configuration
            parent_context: Context from parent report
            collection_name: MongoDB collection name
            
        Returns:
            Processed subreport data
        """
        try:
            # Extract context parameters
            context_params = self._extract_context_parameters(
                subreport_config.context_params, parent_context
            )
            
            # Execute subreport query
            subreport_data = self.query_executor.execute_report_query(
                collection_name, 
                subreport_config.pipeline, 
                context_params
            )
            
            # Process subreport data
            processed_data = {
                'name': subreport_config.name,
                'template': subreport_config.template,
                'data': subreport_data,
                'context_params': context_params,
                'page_break_before': subreport_config.page_break_before,
                'page_break_after': subreport_config.page_break_after,
                'row_count': len(subreport_data)
            }
            
            logger.info(f"Processed subreport '{subreport_config.name}' with {len(subreport_data)} rows")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process subreport '{subreport_config.name}': {e}")
            raise
    
    def _extract_context_parameters(self, context_params: List[str], 
                                   parent_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context parameters from parent context."""
        extracted = {}
        
        for param_name in context_params:
            if param_name in parent_context:
                extracted[param_name] = parent_context[param_name]
            else:
                logger.warning(f"Context parameter '{param_name}' not found in parent context")
        
        return extracted
    
    def process_multiple_subreports(self, subreport_configs: List[SubreportConfig],
                                  parent_context: Dict[str, Any],
                                  collection_name: str) -> List[Dict[str, Any]]:
        """Process multiple subreports."""
        subreports = []
        
        for subreport_config in subreport_configs:
            try:
                subreport = self.process_subreport(
                    subreport_config, parent_context, collection_name
                )
                subreports.append(subreport)
            except Exception as e:
                logger.error(f"Failed to process subreport '{subreport_config.name}': {e}")
                # Continue with other subreports
                subreports.append({
                    'name': subreport_config.name,
                    'template': subreport_config.template,
                    'data': [],
                    'error': str(e),
                    'page_break_before': subreport_config.page_break_before,
                    'page_break_after': subreport_config.page_break_after,
                    'row_count': 0
                })
        
        return subreports
    
    def validate_subreport_context(self, subreport_config: SubreportConfig,
                                 parent_context: Dict[str, Any]) -> List[str]:
        """Validate that required context parameters are available."""
        missing_params = []
        
        for param_name in subreport_config.context_params:
            if param_name not in parent_context:
                missing_params.append(param_name)
        
        return missing_params
    
    def create_subreport_summary(self, subreports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary statistics for subreports."""
        total_rows = sum(subreport.get('row_count', 0) for subreport in subreports)
        error_count = sum(1 for subreport in subreports if 'error' in subreport)
        
        return {
            'total_subreports': len(subreports),
            'successful_subreports': len(subreports) - error_count,
            'failed_subreports': error_count,
            'total_rows': total_rows,
            'subreports': [
                {
                    'name': subreport['name'],
                    'row_count': subreport.get('row_count', 0),
                    'has_error': 'error' in subreport,
                    'error': subreport.get('error')
                }
                for subreport in subreports
            ]
        }
"""Query execution and result processing."""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from .mongodb_client import MongoDBClient
from .pipeline_builder import PipelineBuilder

logger = logging.getLogger(__name__)


class QueryExecutor:
    """Executes MongoDB queries and processes results."""
    
    def __init__(self, mongodb_client: MongoDBClient):
        self.mongodb_client = mongodb_client
        self.pipeline_builder = PipelineBuilder()
    
    def execute_report_query(self, collection_name: str, pipeline: List[Dict[str, Any]], 
                           parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a report query with parameter substitution.
        
        Args:
            collection_name: MongoDB collection name
            pipeline: Aggregation pipeline
            parameters: Query parameters for substitution
            
        Returns:
            Processed query results
        """
        try:
            # Substitute parameters in pipeline
            processed_pipeline = self._substitute_parameters(pipeline, parameters or {})
            
            # Execute aggregation
            results = self.mongodb_client.execute_aggregation(collection_name, processed_pipeline)
            
            # Process results
            processed_results = self._process_results(results)
            
            logger.info(f"Query executed successfully, returned {len(processed_results)} records")
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to execute report query: {e}")
            raise
    
    def execute_simple_query(self, collection_name: str, query: Dict[str, Any] = None,
                           projection: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        Execute a simple find query.
        
        Args:
            collection_name: MongoDB collection name
            query: Find query
            projection: Field projection
            limit: Result limit
            
        Returns:
            Query results
        """
        try:
            results = self.mongodb_client.execute_find(collection_name, query, projection, limit)
            processed_results = self._process_results(results)
            
            logger.info(f"Simple query executed successfully, returned {len(processed_results)} records")
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to execute simple query: {e}")
            raise
    
    def _substitute_parameters(self, pipeline: List[Dict[str, Any]], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Substitute parameters in pipeline stages."""
        import json
        import re
        
        # Convert pipeline to JSON string for parameter substitution
        pipeline_str = json.dumps(pipeline)
        
        # Replace parameters in the format {{param_name}}
        for param_name, param_value in parameters.items():
            # Handle different parameter types
            if isinstance(param_value, (str, int, float, bool)):
                # Direct substitution
                pattern = f"{{{{{param_name}}}}}"
                pipeline_str = pipeline_str.replace(pattern, str(param_value))
            elif isinstance(param_value, (list, tuple)):
                # Convert list to MongoDB array format
                pattern = f'"{{{{{param_name}}}}}"'
                replacement = json.dumps(list(param_value))
                pipeline_str = pipeline_str.replace(pattern, replacement)
            elif isinstance(param_value, dict):
                # Convert dict to MongoDB object format
                pattern = f'"{{{{{param_name}}}}}"'
                replacement = json.dumps(param_value)
                pipeline_str = pipeline_str.replace(pattern, replacement)
            elif isinstance(param_value, (datetime, date)):
                # Convert datetime to MongoDB ISODate format
                pattern = f'"{{{{{param_name}}}}}"'
                if isinstance(param_value, date) and not isinstance(param_value, datetime):
                    param_value = datetime.combine(param_value, datetime.min.time())
                replacement = f'{{"$date": "{param_value.isoformat()}Z"}}'
                pipeline_str = pipeline_str.replace(pattern, replacement)
        
        # Parse back to Python objects
        try:
            return json.loads(pipeline_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pipeline after parameter substitution: {e}")
            logger.error(f"Pipeline string: {pipeline_str}")
            raise ValueError(f"Invalid pipeline after parameter substitution: {e}")
    
    def _process_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process query results for consistency."""
        processed = []
        
        for doc in results:
            processed_doc = {}
            
            for key, value in doc.items():
                # Handle MongoDB ObjectId
                if hasattr(value, '__class__') and value.__class__.__name__ == 'ObjectId':
                    processed_doc[key] = str(value)
                # Handle datetime objects
                elif isinstance(value, datetime):
                    processed_doc[key] = value.isoformat()
                # Handle Decimal objects
                elif isinstance(value, Decimal):
                    processed_doc[key] = float(value)
                # Handle other MongoDB types
                elif hasattr(value, '__class__') and 'bson' in str(value.__class__.__module__):
                    processed_doc[key] = str(value)
                else:
                    processed_doc[key] = value
            
            processed.append(processed_doc)
        
        return processed
    
    def validate_parameters(self, parameters: Dict[str, Any], 
                          parameter_definitions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate and convert parameters according to definitions.
        
        Args:
            parameters: Input parameters
            parameter_definitions: Parameter type definitions
            
        Returns:
            Validated and converted parameters
        """
        validated = {}
        
        for param_name, param_def in parameter_definitions.items():
            param_type = param_def.get('type', 'string')
            required = param_def.get('required', False)
            default = param_def.get('default')
            
            # Check if parameter is provided
            if param_name not in parameters:
                if required:
                    raise ValueError(f"Required parameter '{param_name}' is missing")
                elif default is not None:
                    validated[param_name] = default
                continue
            
            value = parameters[param_name]
            
            # Type conversion and validation
            try:
                if param_type == 'string':
                    validated[param_name] = str(value)
                elif param_type == 'integer':
                    validated[param_name] = int(value)
                elif param_type == 'float':
                    validated[param_name] = float(value)
                elif param_type == 'boolean':
                    if isinstance(value, str):
                        validated[param_name] = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        validated[param_name] = bool(value)
                elif param_type == 'date':
                    if isinstance(value, str):
                        validated[param_name] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        validated[param_name] = value
                elif param_type == 'array':
                    if isinstance(value, (list, tuple)):
                        validated[param_name] = list(value)
                    else:
                        validated[param_name] = [value]
                else:
                    validated[param_name] = value
                    
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid value for parameter '{param_name}': {e}")
        
        return validated
    
    def get_query_plan(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get query execution plan for performance analysis."""
        try:
            # Add explain stage to pipeline
            explain_pipeline = pipeline + [{"$explain": True}]
            
            # Execute explain query
            results = self.mongodb_client.execute_aggregation(collection_name, explain_pipeline)
            
            if results:
                return results[0]
            else:
                return {}
                
        except Exception as e:
            logger.warning(f"Failed to get query plan: {e}")
            return {}
    
    def estimate_query_cost(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate query execution cost and performance."""
        try:
            # Get collection stats
            stats = self.mongodb_client.get_collection_stats(collection_name)
            
            # Get query plan
            plan = self.get_query_plan(collection_name, pipeline)
            
            # Estimate based on pipeline stages
            estimated_docs = stats.get('count', 0)
            estimated_time = 0
            
            for stage in pipeline:
                stage_name = list(stage.keys())[0] if stage else 'unknown'
                
                # Rough estimation based on stage type
                if stage_name in ['$match', '$lookup']:
                    estimated_time += 0.1
                elif stage_name in ['$group', '$sort']:
                    estimated_time += 0.2
                elif stage_name in ['$project', '$addFields']:
                    estimated_time += 0.05
            
            return {
                'estimated_documents': estimated_docs,
                'estimated_time_seconds': estimated_time,
                'pipeline_stages': len(pipeline),
                'collection_stats': stats,
                'query_plan': plan
            }
            
        except Exception as e:
            logger.warning(f"Failed to estimate query cost: {e}")
            return {'error': str(e)}
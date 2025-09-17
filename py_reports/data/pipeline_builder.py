"""MongoDB aggregation pipeline builder with common patterns."""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date

logger = logging.getLogger(__name__)


class PipelineBuilder:
    """Builder for MongoDB aggregation pipelines with common patterns."""
    
    def __init__(self):
        self.pipeline = []
    
    def match(self, query: Dict[str, Any]) -> 'PipelineBuilder':
        """Add $match stage to pipeline."""
        self.pipeline.append({"$match": query})
        return self
    
    def project(self, fields: Dict[str, Any]) -> 'PipelineBuilder':
        """Add $project stage to pipeline."""
        self.pipeline.append({"$project": fields})
        return self
    
    def add_fields(self, fields: Dict[str, Any]) -> 'PipelineBuilder':
        """Add $addFields stage to pipeline."""
        self.pipeline.append({"$addFields": fields})
        return self
    
    def group(self, group_by: Dict[str, Any], aggregations: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add $group stage to pipeline."""
        group_stage = {"_id": group_by}
        if aggregations:
            group_stage.update(aggregations)
        self.pipeline.append({"$group": group_stage})
        return self
    
    def sort(self, sort_fields: Dict[str, int]) -> 'PipelineBuilder':
        """Add $sort stage to pipeline."""
        self.pipeline.append({"$sort": sort_fields})
        return self
    
    def limit(self, count: int) -> 'PipelineBuilder':
        """Add $limit stage to pipeline."""
        self.pipeline.append({"$limit": count})
        return self
    
    def skip(self, count: int) -> 'PipelineBuilder':
        """Add $skip stage to pipeline."""
        self.pipeline.append({"$skip": count})
        return self
    
    def lookup(self, from_collection: str, local_field: str, foreign_field: str, 
              as_field: str, pipeline: List[Dict[str, Any]] = None) -> 'PipelineBuilder':
        """Add $lookup stage to pipeline."""
        lookup_stage = {
            "from": from_collection,
            "localField": local_field,
            "foreignField": foreign_field,
            "as": as_field
        }
        if pipeline:
            lookup_stage["pipeline"] = pipeline
        self.pipeline.append({"$lookup": lookup_stage})
        return self
    
    def unwind(self, field: str, preserve_null_and_empty_arrays: bool = False) -> 'PipelineBuilder':
        """Add $unwind stage to pipeline."""
        unwind_stage = {"path": field}
        if preserve_null_and_empty_arrays:
            unwind_stage["preserveNullAndEmptyArrays"] = True
        self.pipeline.append({"$unwind": unwind_stage})
        return self
    
    def facet(self, facets: Dict[str, List[Dict[str, Any]]]) -> 'PipelineBuilder':
        """Add $facet stage to pipeline."""
        self.pipeline.append({"$facet": facets})
        return self
    
    def bucket(self, group_by: str, boundaries: List[Any], default: str = "Other",
              output: Dict[str, Any] = None) -> 'PipelineBuilder':
        """Add $bucket stage to pipeline."""
        bucket_stage = {
            "groupBy": group_by,
            "boundaries": boundaries,
            "default": default
        }
        if output:
            bucket_stage["output"] = output
        self.pipeline.append({"$bucket": bucket_stage})
        return self
    
    def bucket_auto(self, group_by: str, buckets: int, output: Dict[str, Any] = None,
                   granularity: str = None) -> 'PipelineBuilder':
        """Add $bucketAuto stage to pipeline."""
        bucket_stage = {
            "groupBy": group_by,
            "buckets": buckets
        }
        if output:
            bucket_stage["output"] = output
        if granularity:
            bucket_stage["granularity"] = granularity
        self.pipeline.append({"$bucketAuto": bucket_stage})
        return self
    
    def count(self, field: str = "count") -> 'PipelineBuilder':
        """Add $count stage to pipeline."""
        self.pipeline.append({"$count": field})
        return self
    
    def sample(self, size: int) -> 'PipelineBuilder':
        """Add $sample stage to pipeline."""
        self.pipeline.append({"$sample": {"size": size}})
        return self
    
    def replace_root(self, new_root: Union[str, Dict[str, Any]]) -> 'PipelineBuilder':
        """Add $replaceRoot stage to pipeline."""
        if isinstance(new_root, str):
            self.pipeline.append({"$replaceRoot": {"newRoot": f"${new_root}"}})
        else:
            self.pipeline.append({"$replaceRoot": {"newRoot": new_root}})
        return self
    
    def add_stage(self, stage: Dict[str, Any]) -> 'PipelineBuilder':
        """Add custom stage to pipeline."""
        self.pipeline.append(stage)
        return self
    
    def build(self) -> List[Dict[str, Any]]:
        """Build and return the pipeline."""
        return self.pipeline.copy()
    
    def reset(self) -> 'PipelineBuilder':
        """Reset pipeline to empty state."""
        self.pipeline = []
        return self
    
    @classmethod
    def create_date_range_filter(cls, date_field: str, from_date: Union[str, datetime, date], 
                                to_date: Union[str, datetime, date]) -> Dict[str, Any]:
        """Create date range filter for MongoDB queries."""
        if isinstance(from_date, str):
            from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        elif isinstance(from_date, date) and not isinstance(from_date, datetime):
            from_date = datetime.combine(from_date, datetime.min.time())
        
        if isinstance(to_date, str):
            to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        elif isinstance(to_date, date) and not isinstance(to_date, datetime):
            to_date = datetime.combine(to_date, datetime.max.time())
        
        return {
            date_field: {
                "$gte": from_date,
                "$lte": to_date
            }
        }
    
    @classmethod
    def create_status_filter(cls, status_field: str, statuses: List[str]) -> Dict[str, Any]:
        """Create status filter for MongoDB queries."""
        if len(statuses) == 1:
            return {status_field: statuses[0]}
        else:
            return {status_field: {"$in": statuses}}
    
    @classmethod
    def create_id_filter(cls, id_field: str, ids: List[str]) -> Dict[str, Any]:
        """Create ID filter for MongoDB queries."""
        if len(ids) == 1:
            return {id_field: ids[0]}
        else:
            return {id_field: {"$in": ids}}
    
    @classmethod
    def create_text_search_filter(cls, search_fields: List[str], search_term: str) -> Dict[str, Any]:
        """Create text search filter for MongoDB queries."""
        if not search_term:
            return {}
        
        return {
            "$or": [
                {field: {"$regex": search_term, "$options": "i"}}
                for field in search_fields
            ]
        }
    
    @classmethod
    def create_pivot_pipeline(cls, rows: List[str], columns: List[str], 
                             measures: List[Dict[str, Any]], 
                             collection: str = None) -> List[Dict[str, Any]]:
        """Create pipeline for pivot table generation."""
        pipeline = []
        
        # Group by rows and columns
        group_id = {}
        for row in rows:
            group_id[row] = f"${row}"
        for col in columns:
            group_id[col] = f"${col}"
        
        # Add measures to group stage
        group_stage = {"_id": group_id}
        for measure in measures:
            measure_name = measure.get('name', 'value')
            measure_type = measure.get('type', 'sum')
            measure_field = measure.get('field', 'value')
            
            if measure_type == 'sum':
                group_stage[measure_name] = {"$sum": f"${measure_field}"}
            elif measure_type == 'avg':
                group_stage[measure_name] = {"$avg": f"${measure_field}"}
            elif measure_type == 'count':
                group_stage[measure_name] = {"$sum": 1}
            elif measure_type == 'min':
                group_stage[measure_name] = {"$min": f"${measure_field}"}
            elif measure_type == 'max':
                group_stage[measure_name] = {"$max": f"${measure_field}"}
        
        pipeline.append({"$group": group_stage})
        
        # Sort by rows
        if rows:
            sort_fields = {row: 1 for row in rows}
            pipeline.append({"$sort": sort_fields})
        
        return pipeline
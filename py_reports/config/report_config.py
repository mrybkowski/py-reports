"""Report configuration management."""

import os
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator


class ColumnConfig(BaseModel):
    """Column configuration for tables."""
    
    label: str = Field(..., description="Column label key for translation")
    field: str = Field(..., description="MongoDB field name")
    type: str = Field(default="string", description="Data type (string, number, date, currency)")
    format: Optional[str] = Field(default=None, description="Format string for data")
    align: str = Field(default="left", description="Alignment (left, center, right)")
    width: Optional[str] = Field(default=None, description="Column width (CSS value)")
    wrap: bool = Field(default=True, description="Enable text wrapping")
    ellipsis: bool = Field(default=True, description="Show ellipsis for long text")


class PivotConfig(BaseModel):
    """Pivot table configuration."""
    
    rows: List[str] = Field(..., description="Row dimensions")
    columns: List[str] = Field(..., description="Column dimensions")
    measures: List[Dict[str, Any]] = Field(..., description="Measure definitions")
    show_totals: bool = Field(default=True, description="Show row/column totals")
    show_grand_total: bool = Field(default=True, description="Show grand total")
    column_order: str = Field(default="alphabetical", description="Column ordering (alphabetical, by_sum, custom)")
    max_columns: int = Field(default=200, description="Maximum number of columns")


class SummaryFieldConfig(BaseModel):
    """Summary field configuration."""
    
    name: str = Field(..., description="Field name")
    label_key: str = Field(..., description="Translation key for field label")
    type: str = Field(default="count", description="Field type (count, sum, avg, etc.)")
    filter: Optional[str] = Field(default=None, description="Filter condition (field:value)")


class SummaryConfig(BaseModel):
    """Summary configuration."""
    
    enabled: bool = Field(default=True, description="Enable summary")
    fields: List[SummaryFieldConfig] = Field(default=[], description="Summary fields")


class SubreportConfig(BaseModel):
    """Subreport configuration."""
    
    name: str = Field(..., description="Subreport name")
    template: str = Field(..., description="Template file name")
    pipeline: List[Dict[str, Any]] = Field(..., description="MongoDB aggregation pipeline")
    context_params: List[str] = Field(default=[], description="Parameters to pass from parent context")
    page_break_before: bool = Field(default=False, description="Force page break before subreport")
    page_break_after: bool = Field(default=False, description="Force page break after subreport")


class HeaderFooterConfig(BaseModel):
    """Header and footer configuration."""
    
    show_logo: bool = Field(default=True, description="Show logo in header")
    logo_path: Optional[str] = Field(default=None, description="Path to logo file")
    title_key: str = Field(..., description="Translation key for report title")
    show_date_range: bool = Field(default=True, description="Show date range in header")
    show_generation_time: bool = Field(default=True, description="Show generation timestamp")
    show_page_numbers: bool = Field(default=True, description="Show page numbers in footer")
    show_report_id: bool = Field(default=True, description="Show report ID in footer")
    environment: Optional[str] = Field(default=None, description="Environment identifier")


class ReportConfig(BaseModel):
    """Complete report configuration."""
    
    name: str = Field(..., description="Report name")
    description: str = Field(default="", description="Report description")
    collection: str = Field(..., description="MongoDB collection name")
    pipeline: List[Dict[str, Any]] = Field(..., description="MongoDB aggregation pipeline")
    template: str = Field(..., description="Main template file")
    
    # Table configurations
    columns: List[ColumnConfig] = Field(default=[], description="Table columns")
    pivot: Optional[PivotConfig] = Field(default=None, description="Pivot table configuration")
    
    # Summary
    summary: Optional[SummaryConfig] = Field(default=None, description="Summary configuration")
    
    # Layout
    header: Optional[HeaderFooterConfig] = Field(default=None, description="Header configuration")
    footer: Optional[HeaderFooterConfig] = Field(default=None, description="Footer configuration")
    
    # Subreports
    subreports: List[SubreportConfig] = Field(default=[], description="Subreports")
    
    # Parameters
    parameters: Dict[str, Dict[str, Any]] = Field(
        default={}, 
        description="Parameter definitions with validation rules"
    )
    
    # Styling
    css_file: Optional[str] = Field(default=None, description="Custom CSS file")
    
    @validator('pipeline')
    def validate_pipeline(cls, v):
        """Validate that pipeline is a list of dictionaries."""
        if not isinstance(v, list):
            raise ValueError("Pipeline must be a list")
        for stage in v:
            if not isinstance(stage, dict):
                raise ValueError("Each pipeline stage must be a dictionary")
        return v


def load_report_config(report_name: str, reports_dir: str = "reports") -> ReportConfig:
    """Load report configuration from YAML file."""
    config_path = Path(reports_dir) / f"{report_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Report configuration not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    return ReportConfig(**config_data)


def list_available_reports(reports_dir: str = "reports") -> List[str]:
    """List all available report configurations."""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return []
    
    return [
        f.stem for f in reports_path.glob("*.yaml")
        if f.is_file()
    ]
"""FastAPI REST API for PDF report generation."""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Body, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from io import BytesIO

from .renderer import ReportGenerator
from .config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF Reports Generator API",
    description="Generate PDF reports from MongoDB data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global report generator
_generator: Optional[ReportGenerator] = None


def get_generator(locale: str = "en_US") -> ReportGenerator:
    """Get report generator instance."""
    global _generator
    if _generator is None:
        _generator = ReportGenerator(locale)
    return _generator


# Pydantic models
class ReportParameters(BaseModel):
    """Report parameters model."""
    parameters: Dict[str, Any] = Field(default={}, description="Report parameters")
    locale: str = Field(default="en_US", description="Report locale")


class ReportResponse(BaseModel):
    """Report generation response model."""
    success: bool
    message: str
    report_name: str
    generated_at: str
    file_size_bytes: Optional[int] = None
    file_size_mb: Optional[float] = None


class ReportInfo(BaseModel):
    """Report information model."""
    name: str
    description: str
    collection: str
    template: str
    has_columns: bool
    has_pivot: bool
    has_subreports: bool
    parameters: List[str]
    column_count: int
    subreport_count: int


class ValidationResponse(BaseModel):
    """Report validation response model."""
    valid: bool
    report_name: str
    template_valid: Dict[str, Any]
    mongodb_connected: bool
    collection_exists: bool
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PDF Reports Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        generator = get_generator()
        # Test MongoDB connection
        mongodb_connected = generator.mongodb_client.connect()
        if mongodb_connected:
            generator.mongodb_client.disconnect()
        
        return {
            "status": "healthy",
            "mongodb_connected": mongodb_connected,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/reports", response_model=List[str])
async def list_reports():
    """List all available reports."""
    try:
        generator = get_generator()
        reports = generator.list_available_reports()
        return reports
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {e}")


@app.get("/reports/{report_name}/info", response_model=ReportInfo)
async def get_report_info(report_name: str):
    """Get detailed information about a report."""
    try:
        generator = get_generator()
        info = generator.get_report_info(report_name)
        
        if 'error' in info:
            raise HTTPException(status_code=404, detail=info['error'])
        
        return ReportInfo(**info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report info for {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get report info: {e}")


@app.get("/reports/{report_name}/validate", response_model=ValidationResponse)
async def validate_report(report_name: str):
    """Validate report configuration."""
    try:
        generator = get_generator()
        validation = generator.validate_report_config(report_name)
        
        return ValidationResponse(**validation)
    except Exception as e:
        logger.error(f"Failed to validate report {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate report: {e}")


@app.post("/reports/{report_name}/render", response_model=ReportResponse)
async def render_report(
    report_name: str,
    params: ReportParameters = Body(...),
    output_format: str = Query("bytes", description="Output format: bytes or file")
):
    """Generate a report."""
    try:
        generator = get_generator(params.locale)
        
        if output_format == "file":
            # Generate to file
            settings = get_settings()
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"{report_name}_{timestamp}.pdf"
            
            result = generator.generate_report(
                report_name, 
                params.parameters, 
                output_path
            )
            
            file_size = output_path.stat().st_size
            
            return ReportResponse(
                success=True,
                message=f"Report generated successfully",
                report_name=report_name,
                generated_at=datetime.now().isoformat(),
                file_size_bytes=file_size,
                file_size_mb=round(file_size / (1024 * 1024), 2)
            )
        else:
            # Generate to bytes
            pdf_bytes = generator.generate_report(
                report_name, 
                params.parameters
            )
            
            return ReportResponse(
                success=True,
                message=f"Report generated successfully",
                report_name=report_name,
                generated_at=datetime.now().isoformat(),
                file_size_bytes=len(pdf_bytes),
                file_size_mb=round(len(pdf_bytes) / (1024 * 1024), 2)
            )
    
    except Exception as e:
        logger.error(f"Failed to generate report {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")


@app.post("/reports/{report_name}/render/download")
async def download_report(
    report_name: str,
    params: ReportParameters = Body(...)
):
    """Generate and download a report as PDF file."""
    try:
        generator = get_generator(params.locale)
        pdf_bytes = generator.generate_report(report_name, params.parameters)
        
        # Create streaming response
        def iter_pdf():
            yield pdf_bytes
        
        return StreamingResponse(
            iter_pdf(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to generate report {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")


@app.post("/reports/{report_name}/test")
async def test_report(
    report_name: str,
    params: ReportParameters = Body(...)
):
    """Test report generation without saving output."""
    try:
        generator = get_generator(params.locale)
        result = generator.test_report_generation(report_name, params.parameters)
        
        return result
    except Exception as e:
        logger.error(f"Failed to test report {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test report: {e}")


@app.get("/reports/{report_name}/sample")
async def get_sample_data(
    report_name: str,
    size: int = Query(100, description="Sample size"),
    locale: str = Query("en_US", description="Report locale")
):
    """Get sample data for a report."""
    try:
        generator = get_generator(locale)
        result = generator.generate_sample_data(report_name, size)
        
        return result
    except Exception as e:
        logger.error(f"Failed to get sample data for {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sample data: {e}")


@app.get("/reports/{report_name}/file")
async def get_report_file(
    report_name: str,
    params: ReportParameters = Body(...)
):
    """Generate report and return file path for download."""
    try:
        generator = get_generator(params.locale)
        
        # Generate to file
        settings = get_settings()
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"{report_name}_{timestamp}.pdf"
        
        generator.generate_report(report_name, params.parameters, output_path)
        
        return FileResponse(
            path=output_path,
            filename=f"{report_name}_{timestamp}.pdf",
            media_type="application/pdf"
        )
    
    except Exception as e:
        logger.error(f"Failed to generate report file {report_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report file: {e}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "detail": str(exc)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("PDF Reports Generator API starting up")
    try:
        # Test MongoDB connection
        generator = get_generator()
        if generator.mongodb_client.connect():
            generator.mongodb_client.disconnect()
            logger.info("MongoDB connection test successful")
        else:
            logger.warning("MongoDB connection test failed")
    except Exception as e:
        logger.error(f"Startup error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("PDF Reports Generator API shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
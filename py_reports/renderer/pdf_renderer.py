"""PDF renderer using WeasyPrint with header/footer support."""

import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from io import BytesIO
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from ..templates import get_template_engine
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class PDFRenderer:
    """PDF renderer with WeasyPrint backend."""
    
    def __init__(self, templates_dir: str = "py_reports/templates", locale: str = "en_US"):
        self.templates_dir = Path(templates_dir)
        self.locale = locale
        self.settings = get_settings()
        self.template_engine = get_template_engine(templates_dir, locale)
        
        # Font configuration for Unicode support
        self.font_config = FontConfiguration()
        
        # CSS files to include
        self.css_files = [
            self.templates_dir / "base.css"
        ]
    
    def render_pdf(self, template_name: str, context: Dict[str, Any], 
                   output_path: Optional[Union[str, Path]] = None) -> Union[bytes, Path]:
        """
        Render PDF from template and context.
        
        Args:
            template_name: Name of the template file
            context: Template context variables
            output_path: Output file path (if None, returns bytes)
            
        Returns:
            PDF bytes or output file path
        """
        try:
            # Render HTML from template
            html_content = self.template_engine.render_template(template_name, context)
            
            # Create HTML object
            html_doc = HTML(string=html_content, base_url=str(self.templates_dir))
            
            # Load CSS files
            css_docs = []
            for css_file in self.css_files:
                if css_file.exists():
                    css_docs.append(CSS(filename=str(css_file), font_config=self.font_config))
            
            # Add custom CSS if specified in context
            if 'config' in context and context['config'].get('css_file'):
                custom_css_path = self.templates_dir / context['config']['css_file']
                if custom_css_path.exists():
                    css_docs.append(CSS(filename=str(custom_css_path), font_config=self.font_config))
            
            # Add page CSS for pagination if available
            if 'page_css' in context:
                page_css_content = context['page_css']
                if page_css_content:
                    css_docs.append(CSS(string=page_css_content, font_config=self.font_config))
            
            # Render PDF
            pdf_doc = html_doc.render(stylesheets=css_docs, font_config=self.font_config)
            
            if output_path:
                # Save to file
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                pdf_doc.write_pdf(str(output_path))
                logger.info(f"PDF saved to: {output_path}")
                return output_path
            else:
                # Return bytes
                pdf_bytes = pdf_doc.write_pdf()
                logger.info(f"PDF generated, size: {len(pdf_bytes)} bytes")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Failed to render PDF: {e}")
            raise
    
    def render_pdf_from_string(self, html_content: str, context: Dict[str, Any],
                              output_path: Optional[Union[str, Path]] = None) -> Union[bytes, Path]:
        """
        Render PDF from HTML string.
        
        Args:
            html_content: HTML content string
            context: Template context variables
            output_path: Output file path (if None, returns bytes)
            
        Returns:
            PDF bytes or output file path
        """
        try:
            # Create HTML object
            html_doc = HTML(string=html_content, base_url=str(self.templates_dir))
            
            # Load CSS files
            css_docs = []
            for css_file in self.css_files:
                if css_file.exists():
                    css_docs.append(CSS(filename=str(css_file), font_config=self.font_config))
            
            # Add custom CSS if specified in context
            if 'config' in context and context['config'].get('css_file'):
                custom_css_path = self.templates_dir / context['config']['css_file']
                if custom_css_path.exists():
                    css_docs.append(CSS(filename=str(custom_css_path), font_config=self.font_config))
            
            # Add page CSS for pagination if available
            if 'page_css' in context:
                page_css_content = context['page_css']
                if page_css_content:
                    css_docs.append(CSS(string=page_css_content, font_config=self.font_config))
            
            # Render PDF
            pdf_doc = html_doc.render(stylesheets=css_docs, font_config=self.font_config)
            
            if output_path:
                # Save to file
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                pdf_doc.write_pdf(str(output_path))
                logger.info(f"PDF saved to: {output_path}")
                return output_path
            else:
                # Return bytes
                pdf_bytes = pdf_doc.write_pdf()
                logger.info(f"PDF generated, size: {len(pdf_bytes)} bytes")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Failed to render PDF from string: {e}")
            raise
    
    def render_report(self, report_data: Dict[str, Any], 
                     report_config: Dict[str, Any],
                     parameters: Dict[str, Any] = None,
                     output_path: Optional[Union[str, Path]] = None) -> Union[bytes, Path]:
        """
        Render complete report to PDF.
        
        Args:
            report_data: Processed report data
            report_config: Report configuration
            parameters: Report parameters
            output_path: Output file path (if None, returns bytes)
            
        Returns:
            PDF bytes or output file path
        """
        try:
            # Create template context
            context = self.template_engine.create_report_context(
                report_data, report_config, parameters
            )
            
            # Get template name from config
            template_name = report_config.get('template', 'base.html')
            
            # Render PDF
            return self.render_pdf(template_name, context, output_path)
            
        except Exception as e:
            logger.error(f"Failed to render report: {e}")
            raise
    
    def get_pdf_info(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Get information about PDF content."""
        try:
            from weasyprint import HTML
            from io import BytesIO
            
            # This is a simplified version - in practice, you'd need to parse the PDF
            return {
                'size_bytes': len(pdf_bytes),
                'size_mb': round(len(pdf_bytes) / (1024 * 1024), 2),
                'format': 'PDF',
                'created_at': self.template_engine._get_current_time()
            }
        except Exception as e:
            logger.warning(f"Failed to get PDF info: {e}")
            return {'error': str(e)}
    
    def validate_html(self, html_content: str) -> Dict[str, Any]:
        """Validate HTML content before rendering."""
        try:
            # Try to create HTML object
            html_doc = HTML(string=html_content, base_url=str(self.templates_dir))
            
            # Try to render (this will catch most errors)
            pdf_doc = html_doc.render(font_config=self.font_config)
            
            return {
                'valid': True,
                'message': 'HTML is valid'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'message': f'HTML validation failed: {e}'
            }
    
    def add_css_file(self, css_path: Union[str, Path]):
        """Add CSS file to rendering process."""
        css_path = Path(css_path)
        if css_path.exists():
            self.css_files.append(css_path)
            logger.info(f"Added CSS file: {css_path}")
        else:
            logger.warning(f"CSS file not found: {css_path}")
    
    def set_font_config(self, font_config: FontConfiguration):
        """Set custom font configuration."""
        self.font_config = font_config
        logger.info("Font configuration updated")
    
    def get_supported_fonts(self) -> list:
        """Get list of supported fonts."""
        try:
            # This would require font enumeration - simplified for now
            return [
                'DejaVu Sans',
                'Arial',
                'Times New Roman',
                'Courier New',
                'Helvetica'
            ]
        except Exception as e:
            logger.warning(f"Failed to get supported fonts: {e}")
            return []


# Global PDF renderer instance
_pdf_renderer: Optional[PDFRenderer] = None


def get_pdf_renderer(templates_dir: str = "py_reports/templates", 
                    locale: str = "en_US") -> PDFRenderer:
    """Get PDF renderer instance (singleton pattern)."""
    global _pdf_renderer
    if _pdf_renderer is None:
        _pdf_renderer = PDFRenderer(templates_dir, locale)
    return _pdf_renderer
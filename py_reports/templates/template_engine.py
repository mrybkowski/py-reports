"""Jinja2 template engine with custom filters and functions."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from ..translations import get_translator
from ..transforms.data_formatter import DataFormatter
from .filters import register_filters

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Jinja2 template engine with custom filters and functions."""
    
    def __init__(self, templates_dir: str = "py_reports/templates", locale: str = "en_US"):
        self.templates_dir = Path(templates_dir)
        self.locale = locale
        self.translator = get_translator()
        self.formatter = DataFormatter(locale)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters and functions
        self._register_globals()
        register_filters(self.env, self.translator, self.formatter)
    
    def _register_globals(self):
        """Register global functions and variables."""
        self.env.globals.update({
            't': self._translate,
            'format_number': self.formatter.format_number,
            'format_currency': self.formatter.format_currency,
            'format_date': self.formatter.format_date,
            'format_datetime': self.formatter.format_datetime,
            'format_time': self.formatter.format_time,
            'format_percentage': self.formatter.format_percentage,
            'format_boolean': self.formatter.format_boolean,
            'format_text': self.formatter.format_text,
            'locale': self.locale,
            'now': self._get_current_time,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'round': round,
            'sum': sum,
            'max': max,
            'min': min,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'range': range
        })
    
    def _translate(self, key: str, **kwargs) -> str:
        """Translation function for templates."""
        return self.translator.translate(key, self.locale, **kwargs)
    
    def _get_current_time(self) -> str:
        """Get current time formatted for the locale."""
        from datetime import datetime
        return self.formatter.format_datetime(datetime.now())
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Template context variables
            
        Returns:
            Rendered HTML content
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}")
            raise
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {template_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with the given context.
        
        Args:
            template_string: Template string content
            context: Template context variables
            
        Returns:
            Rendered HTML content
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to render template string: {e}")
            raise
    
    def get_template_variables(self, template_name: str) -> set:
        """Get variables used in a template."""
        try:
            template = self.env.get_template(template_name)
            return template.get_corresponding_lineno(template_name)
        except Exception as e:
            logger.warning(f"Failed to get template variables for {template_name}: {e}")
            return set()
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate template syntax and dependencies."""
        try:
            template = self.env.get_template(template_name)
            
            # Try to render with empty context to check for syntax errors
            template.render()
            
            return {
                'valid': True,
                'template_name': template_name,
                'message': 'Template is valid'
            }
        except TemplateSyntaxError as e:
            return {
                'valid': False,
                'template_name': template_name,
                'error': str(e),
                'line': getattr(e, 'lineno', None),
                'message': f'Syntax error: {e}'
            }
        except Exception as e:
            return {
                'valid': False,
                'template_name': template_name,
                'error': str(e),
                'message': f'Validation error: {e}'
            }
    
    def list_templates(self) -> list:
        """List all available templates."""
        try:
            return self.env.list_templates()
        except Exception as e:
            logger.warning(f"Failed to list templates: {e}")
            return []
    
    def create_report_context(self, report_data: Dict[str, Any], 
                            report_config: Dict[str, Any],
                            parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create template context for report rendering."""
        context = {
            'report': report_data,
            'config': report_config,
            'parameters': parameters or {},
            'locale': self.locale,
            'translator': self.translator,
            'formatter': self.formatter,
            'pagination_css': self._get_pagination_css(),
            'page_css': self._get_page_css()
        }
        
        return context
    
    def _get_pagination_css(self) -> str:
        """Get pagination CSS for current locale."""
        # Get the translation for page_x_of_y
        translation = self.translator.translate('footer.page_x_of_y', self.locale, x='', y='')
        
        # Extract the text parts for WeasyPrint CSS
        if 'Strona' in translation and 'z' in translation:
            # Polish format: "Strona {x} z {y}"
            return 'content: "Strona: " counter(page) " z " counter(pages);'
        elif 'Page' in translation and 'of' in translation:
            # English format: "Page {x} of {y}"
            return 'content: "Page: " counter(page) " of " counter(pages);'
        else:
            # Fallback to English
            return 'content: "Page: " counter(page) " of " counter(pages);'
    
    def _get_page_css(self) -> str:
        """Get complete @page CSS with pagination for current locale."""
        pagination_css = self._get_pagination_css()
        
        # Use English for CSS compatibility
        header_title = "Report"
        
        # Get current date for generation date
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Get translated "Generated" text
        generated_text = self.translator.translate('footer.generated', self.locale)
        
        return f"""
        @page {{
          size: A4;
          margin: 2cm 1.5cm 2cm 1.5cm;

          @top-center {{
            content: "{header_title}";
            font-size: 12px;
            font-weight: bold;
          }}

          @bottom-right {{
            {pagination_css}
            font-size: 10px;
          }}

          @bottom-left {{
            content: "{generated_text}: {current_date}";
            font-size: 10px;
          }}
        }}

        @page :first {{
          @top-center {{
            content: "{header_title} - Date Range";
          }}
        }}

        .page-break {{
          page-break-before: always;
        }}

        .page-break-after {{
          page-break-after: always;
        }}

        .no-page-break {{
          page-break-inside: avoid;
        }}
        """


# Global template engine instance
_template_engine: Optional[TemplateEngine] = None


def get_template_engine(templates_dir: str = "py_reports/templates", 
                       locale: str = "en_US") -> TemplateEngine:
    """Get template engine instance (singleton pattern)."""
    global _template_engine
    if _template_engine is None or _template_engine.locale != locale:
        _template_engine = TemplateEngine(templates_dir, locale)
    return _template_engine
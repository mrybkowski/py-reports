"""Custom Jinja2 filters for template rendering."""

import logging
from typing import Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from jinja2 import Environment

logger = logging.getLogger(__name__)


def register_filters(env: Environment, translator, formatter):
    """Register custom filters with Jinja2 environment."""
    
    @env.filter('currency')
    def currency_filter(value: Any, currency: str = "USD") -> str:
        """Format value as currency."""
        return formatter.format_currency(value, currency)
    
    @env.filter('number')
    def number_filter(value: Any, format_string: str = None) -> str:
        """Format value as number."""
        return formatter.format_number(value, format_string)
    
    @env.filter('date')
    def date_filter(value: Any, format_string: str = None) -> str:
        """Format value as date."""
        return formatter.format_date(value, format_string)
    
    @env.filter('datetime')
    def datetime_filter(value: Any, format_string: str = None) -> str:
        """Format value as datetime."""
        return formatter.format_datetime(value, format_string)
    
    @env.filter('time')
    def time_filter(value: Any, format_string: str = None) -> str:
        """Format value as time."""
        return formatter.format_time(value, format_string)
    
    @env.filter('percentage')
    def percentage_filter(value: Any, format_string: str = None) -> str:
        """Format value as percentage."""
        return formatter.format_percentage(value, format_string)
    
    @env.filter('boolean')
    def boolean_filter(value: Any, true_text: str = "Yes", false_text: str = "No") -> str:
        """Format value as boolean."""
        return formatter.format_boolean(value, true_text, false_text)
    
    @env.filter('text')
    def text_filter(value: Any, max_length: int = None, ellipsis: bool = True) -> str:
        """Format value as text with optional length limit."""
        return formatter.format_text(value, max_length, ellipsis)
    
    @env.filter('phone')
    def phone_filter(value: str, country_code: str = "US") -> str:
        """Format value as phone number."""
        return formatter.format_phone(value, country_code)
    
    @env.filter('filesize')
    def filesize_filter(value: Any, binary: bool = True) -> str:
        """Format value as file size."""
        return formatter.format_file_size(value, binary)
    
    @env.filter('t')
    def translate_filter(key: str, **kwargs) -> str:
        """Translation filter."""
        return translator.translate(key, **kwargs)
    
    @env.filter('default')
    def default_filter(value: Any, default_value: str = "") -> str:
        """Return default value if value is None or empty."""
        if value is None or value == "":
            return default_value
        return str(value)
    
    @env.filter('join')
    def join_filter(value: list, separator: str = ", ") -> str:
        """Join list items with separator."""
        if not isinstance(value, (list, tuple)):
            return str(value)
        return separator.join(str(item) for item in value)
    
    @env.filter('split')
    def split_filter(value: str, separator: str = " ") -> list:
        """Split string by separator."""
        if not isinstance(value, str):
            return [str(value)]
        return value.split(separator)
    
    @env.filter('upper')
    def upper_filter(value: str) -> str:
        """Convert string to uppercase."""
        return str(value).upper()
    
    @env.filter('lower')
    def lower_filter(value: str) -> str:
        """Convert string to lowercase."""
        return str(value).lower()
    
    @env.filter('title')
    def title_filter(value: str) -> str:
        """Convert string to title case."""
        return str(value).title()
    
    @env.filter('capitalize')
    def capitalize_filter(value: str) -> str:
        """Capitalize first letter of string."""
        return str(value).capitalize()
    
    @env.filter('truncate')
    def truncate_filter(value: str, length: int = 50, ellipsis: str = "...") -> str:
        """Truncate string to specified length."""
        if not isinstance(value, str):
            value = str(value)
        
        if len(value) <= length:
            return value
        
        return value[:length - len(ellipsis)] + ellipsis
    
    @env.filter('wordwrap')
    def wordwrap_filter(value: str, width: int = 50) -> str:
        """Wrap text to specified width."""
        if not isinstance(value, str):
            value = str(value)
        
        words = value.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return "<br>".join(lines)
    
    @env.filter('pluralize')
    def pluralize_filter(value: int, singular: str = "", plural: str = "s") -> str:
        """Return singular or plural form based on count."""
        if value == 1:
            return singular
        else:
            return plural
    
    @env.filter('ordinal')
    def ordinal_filter(value: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                return str(value)
        
        if 10 <= value % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
        
        return f"{value}{suffix}"
    
    @env.filter('abs')
    def abs_filter(value: Any) -> Any:
        """Return absolute value."""
        try:
            return abs(float(value))
        except (ValueError, TypeError):
            return value
    
    @env.filter('round')
    def round_filter(value: Any, precision: int = 0) -> Any:
        """Round number to specified precision."""
        try:
            return round(float(value), precision)
        except (ValueError, TypeError):
            return value
    
    @env.filter('sum')
    def sum_filter(value: list) -> Any:
        """Sum list of numbers."""
        if not isinstance(value, (list, tuple)):
            return value
        
        try:
            return sum(float(item) for item in value if item is not None)
        except (ValueError, TypeError):
            return 0
    
    @env.filter('avg')
    def avg_filter(value: list) -> Any:
        """Calculate average of list of numbers."""
        if not isinstance(value, (list, tuple)) or not value:
            return 0
        
        try:
            numbers = [float(item) for item in value if item is not None]
            return sum(numbers) / len(numbers) if numbers else 0
        except (ValueError, TypeError):
            return 0
    
    @env.filter('min')
    def min_filter(value: list) -> Any:
        """Find minimum value in list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        
        try:
            return min(float(item) for item in value if item is not None)
        except (ValueError, TypeError):
            return None
    
    @env.filter('max')
    def max_filter(value: list) -> Any:
        """Find maximum value in list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        
        try:
            return max(float(item) for item in value if item is not None)
        except (ValueError, TypeError):
            return None
    
    @env.filter('count')
    def count_filter(value: list) -> int:
        """Count items in list."""
        if not isinstance(value, (list, tuple)):
            return 1
        return len(value)
    
    @env.filter('first')
    def first_filter(value: list) -> Any:
        """Get first item from list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        return value[0]
    
    @env.filter('last')
    def last_filter(value: list) -> Any:
        """Get last item from list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        return value[-1]
    
    @env.filter('sort')
    def sort_filter(value: list, reverse: bool = False) -> list:
        """Sort list."""
        if not isinstance(value, (list, tuple)):
            return [value]
        
        try:
            return sorted(value, reverse=reverse)
        except TypeError:
            # If sorting fails, return as-is
            return list(value)
    
    @env.filter('unique')
    def unique_filter(value: list) -> list:
        """Remove duplicates from list while preserving order."""
        if not isinstance(value, (list, tuple)):
            return [value]
        
        seen = set()
        result = []
        for item in value:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    @env.filter('groupby')
    def groupby_filter(value: list, key: str) -> dict:
        """Group list items by key."""
        if not isinstance(value, (list, tuple)):
            return {}
        
        groups = {}
        for item in value:
            if isinstance(item, dict) and key in item:
                group_key = item[key]
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(item)
        
        return groups
    
    @env.filter('selectattr')
    def selectattr_filter(value: list, attr: str, test: str = None) -> list:
        """Select items from list based on attribute."""
        if not isinstance(value, (list, tuple)):
            return []
        
        result = []
        for item in value:
            if isinstance(item, dict) and attr in item:
                if test is None or test == 'truthy':
                    if item[attr]:
                        result.append(item)
                elif test == 'falsy':
                    if not item[attr]:
                        result.append(item)
                elif test == 'none':
                    if item[attr] is None:
                        result.append(item)
                elif test == 'notnone':
                    if item[attr] is not None:
                        result.append(item)
        
        return result
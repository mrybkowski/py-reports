"""Custom Jinja2 filters for template rendering."""

import logging
from typing import Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from jinja2 import Environment

logger = logging.getLogger(__name__)


def register_filters(env: Environment, translator, formatter):
    """Register custom filters with Jinja2 environment."""
    
    def currency_filter(value: Any, currency: str = "USD") -> str:
        """Format value as currency."""
        return formatter.format_currency(value, currency)
    
    def number_filter(value: Any, format_string: str = None) -> str:
        """Format value as number."""
        return formatter.format_number(value, format_string)
    
    def date_filter(value: Any, format_string: str = None) -> str:
        """Format value as date."""
        return formatter.format_date(value, format_string)
    
    def datetime_filter(value: Any, format_string: str = None) -> str:
        """Format value as datetime."""
        return formatter.format_datetime(value, format_string)
    
    def time_filter(value: Any, format_string: str = None) -> str:
        """Format value as time."""
        return formatter.format_time(value, format_string)
    
    def percentage_filter(value: Any, format_string: str = None) -> str:
        """Format value as percentage."""
        return formatter.format_percentage(value, format_string)
    
    def boolean_filter(value: Any, true_text: str = "Yes", false_text: str = "No") -> str:
        """Format value as boolean."""
        return formatter.format_boolean(value, true_text, false_text)
    
    def text_filter(value: Any, max_length: int = None, ellipsis: bool = True) -> str:
        """Format value as text with optional length limit."""
        return formatter.format_text(value, max_length, ellipsis)
    
    def phone_filter(value: str, country_code: str = "US") -> str:
        """Format value as phone number."""
        return formatter.format_phone(value, country_code)
    
    def filesize_filter(value: Any, binary: bool = True) -> str:
        """Format value as file size."""
        return formatter.format_file_size(value, binary)
    
    def translate_filter(key: str, **kwargs) -> str:
        """Translation filter."""
        return translator.translate(key, **kwargs)
    
    def default_filter(value: Any, default_value: str = "") -> str:
        """Return default value if value is None or empty."""
        if value is None or value == "":
            return default_value
        return str(value)
    
    def join_filter(value: list, separator: str = ", ") -> str:
        """Join list items with separator."""
        if not isinstance(value, (list, tuple)):
            return str(value)
        return separator.join(str(item) for item in value)
    
    def split_filter(value: str, separator: str = " ") -> list:
        """Split string by separator."""
        if not isinstance(value, str):
            return [str(value)]
        return value.split(separator)
    
    def upper_filter(value: str) -> str:
        """Convert string to uppercase."""
        return str(value).upper()
    
    def lower_filter(value: str) -> str:
        """Convert string to lowercase."""
        return str(value).lower()
    
    def title_filter(value: str) -> str:
        """Convert string to title case."""
        return str(value).title()
    
    def capitalize_filter(value: str) -> str:
        """Capitalize first letter of string."""
        return str(value).capitalize()
    
    def truncate_filter(value: str, length: int = 50, ellipsis: str = "...") -> str:
        """Truncate string to specified length."""
        if not isinstance(value, str):
            value = str(value)
        
        if len(value) <= length:
            return value
        
        return value[:length - len(ellipsis)] + ellipsis
    
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
    
    def pluralize_filter(value: int, singular: str = "", plural: str = "s") -> str:
        """Return singular or plural form based on count."""
        if value == 1:
            return singular
        else:
            return plural
    
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
    
    def abs_filter(value: Any) -> Any:
        """Return absolute value."""
        try:
            return abs(float(value))
        except (ValueError, TypeError):
            return value
    
    def round_filter(value: Any, precision: int = 0) -> Any:
        """Round number to specified precision."""
        try:
            return round(float(value), precision)
        except (ValueError, TypeError):
            return value
    
    def sum_filter(value: list) -> Any:
        """Sum list of numbers."""
        if not isinstance(value, (list, tuple)):
            return value
        
        try:
            return sum(float(item) for item in value if item is not None)
        except (ValueError, TypeError):
            return 0
    
    def avg_filter(value: list) -> Any:
        """Calculate average of list of numbers."""
        if not isinstance(value, (list, tuple)) or not value:
            return 0
        
        try:
            numbers = [float(item) for item in value if item is not None]
            return sum(numbers) / len(numbers) if numbers else 0
        except (ValueError, TypeError):
            return 0
    
    def min_filter(value: list) -> Any:
        """Find minimum value in list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        
        try:
            return min(float(item) for item in value if item is not None)
        except (ValueError, TypeError):
            return None
    
    def max_filter(value: list) -> Any:
        """Find maximum value in list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        
        try:
            return max(float(item) for item in value if item is not None)
        except (ValueError, TypeError):
            return None
    
    def count_filter(value: list) -> int:
        """Count items in list."""
        if not isinstance(value, (list, tuple)):
            return 1
        return len(value)
    
    def first_filter(value: list) -> Any:
        """Get first item from list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        return value[0]
    
    def last_filter(value: list) -> Any:
        """Get last item from list."""
        if not isinstance(value, (list, tuple)) or not value:
            return None
        return value[-1]
    
    def sort_filter(value: list, reverse: bool = False) -> list:
        """Sort list."""
        if not isinstance(value, (list, tuple)):
            return [value]
        
        try:
            return sorted(value, reverse=reverse)
        except TypeError:
            # If sorting fails, return as-is
            return list(value)
    
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
    
    # Register all filters
    env.filters.update({
        'currency': currency_filter,
        'number': number_filter,
        'date': date_filter,
        'datetime': datetime_filter,
        'time': time_filter,
        'percentage': percentage_filter,
        'boolean': boolean_filter,
        'text': text_filter,
        'phone': phone_filter,
        'filesize': filesize_filter,
        't': translate_filter,
        'default': default_filter,
        'join': join_filter,
        'split': split_filter,
        'upper': upper_filter,
        'lower': lower_filter,
        'title': title_filter,
        'capitalize': capitalize_filter,
        'truncate': truncate_filter,
        'wordwrap': wordwrap_filter,
        'pluralize': pluralize_filter,
        'ordinal': ordinal_filter,
        'abs': abs_filter,
        'round': round_filter,
        'sum': sum_filter,
        'avg': avg_filter,
        'min': min_filter,
        'max': max_filter,
        'count': count_filter,
        'first': first_filter,
        'last': last_filter,
        'sort': sort_filter,
        'unique': unique_filter,
        'groupby': groupby_filter,
        'selectattr': selectattr_filter,
    })
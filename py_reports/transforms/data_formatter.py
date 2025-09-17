"""Data formatting utilities for different data types and locales."""

import logging
from typing import Any, Optional, Union
from decimal import Decimal
from datetime import datetime, date
from babel import Locale
from babel.numbers import format_number, format_currency, format_decimal, format_percent
from babel.dates import format_date, format_datetime, format_time

logger = logging.getLogger(__name__)


class DataFormatter:
    """Formats data according to locale and type specifications."""
    
    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        try:
            self.babel_locale = Locale.parse(locale)
        except Exception as e:
            logger.warning(f"Failed to parse locale {locale}, using en_US: {e}")
            self.babel_locale = Locale.parse("en_US")
    
    def format_number(self, value: Union[int, float, Decimal], 
                     format_string: Optional[str] = None) -> str:
        """Format number according to locale."""
        if value is None:
            return ""
        
        try:
            if format_string:
                # Use custom format string
                if format_string.startswith("#,##0"):
                    return format_decimal(value, format=format_string, locale=self.babel_locale)
                else:
                    return format_number(value, format=format_string, locale=self.babel_locale)
            else:
                # Use default formatting
                return format_number(value, locale=self.babel_locale)
        except Exception as e:
            logger.warning(f"Failed to format number {value}: {e}")
            return str(value)
    
    def format_currency(self, value: Union[int, float, Decimal], 
                       currency: str = "USD", 
                       format_string: Optional[str] = None) -> str:
        """Format currency according to locale."""
        if value is None:
            return ""
        
        try:
            if format_string:
                return format_currency(value, currency, format=format_string, locale=self.babel_locale)
            else:
                return format_currency(value, currency, locale=self.babel_locale)
        except Exception as e:
            logger.warning(f"Failed to format currency {value} {currency}: {e}")
            return f"{value} {currency}"
    
    def format_percentage(self, value: Union[int, float, Decimal], 
                         format_string: Optional[str] = None) -> str:
        """Format percentage according to locale."""
        if value is None:
            return ""
        
        try:
            # Convert to decimal if needed (e.g., 0.15 -> 15%)
            if isinstance(value, (int, float)) and value <= 1:
                value = value * 100
            
            if format_string:
                return format_percent(value, format=format_string, locale=self.babel_locale)
            else:
                return format_percent(value, locale=self.babel_locale)
        except Exception as e:
            logger.warning(f"Failed to format percentage {value}: {e}")
            return f"{value}%"
    
    def format_date(self, value: Union[datetime, date, str], 
                   format_string: Optional[str] = None) -> str:
        """Format date according to locale."""
        if value is None:
            return ""
        
        try:
            # Convert string to date if needed
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        return value  # Return as-is if can't parse
            
            if format_string:
                if isinstance(value, datetime):
                    return format_datetime(value, format=format_string, locale=self.babel_locale)
                else:
                    return format_date(value, format=format_string, locale=self.babel_locale)
            else:
                if isinstance(value, datetime):
                    return format_date(value, locale=self.babel_locale)
                else:
                    return format_date(value, locale=self.babel_locale)
        except Exception as e:
            logger.warning(f"Failed to format date {value}: {e}")
            return str(value)
    
    def format_datetime(self, value: Union[datetime, str], 
                       format_string: Optional[str] = None) -> str:
        """Format datetime according to locale."""
        if value is None:
            return ""
        
        try:
            # Convert string to datetime if needed
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return value  # Return as-is if can't parse
            
            if format_string:
                return format_datetime(value, format=format_string, locale=self.babel_locale)
            else:
                return format_datetime(value, locale=self.babel_locale)
        except Exception as e:
            logger.warning(f"Failed to format datetime {value}: {e}")
            return str(value)
    
    def format_time(self, value: Union[datetime, str], 
                   format_string: Optional[str] = None) -> str:
        """Format time according to locale."""
        if value is None:
            return ""
        
        try:
            # Convert string to time if needed
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        value = datetime.strptime(value, "%H:%M:%S")
                    except ValueError:
                        return value  # Return as-is if can't parse
            
            if format_string:
                return format_time(value, format=format_string, locale=self.babel_locale)
            else:
                return format_time(value, locale=self.babel_locale)
        except Exception as e:
            logger.warning(f"Failed to format time {value}: {e}")
            return str(value)
    
    def format_boolean(self, value: Any, true_text: str = "Yes", 
                      false_text: str = "No") -> str:
        """Format boolean value."""
        if value is None:
            return ""
        
        if isinstance(value, bool):
            return true_text if value else false_text
        elif isinstance(value, str):
            return true_text if value.lower() in ('true', '1', 'yes', 'on') else false_text
        elif isinstance(value, (int, float)):
            return true_text if value != 0 else false_text
        else:
            return true_text if value else false_text
    
    def format_text(self, value: Any, max_length: Optional[int] = None, 
                   ellipsis: bool = True) -> str:
        """Format text with optional length limit."""
        if value is None:
            return ""
        
        text = str(value)
        
        if max_length and len(text) > max_length:
            if ellipsis:
                return text[:max_length-3] + "..."
            else:
                return text[:max_length]
        
        return text
    
    def format_phone(self, value: str, country_code: str = "US") -> str:
        """Format phone number according to locale."""
        if not value:
            return ""
        
        # Remove non-digit characters
        digits = ''.join(filter(str.isdigit, str(value)))
        
        if len(digits) == 10:
            # US format: (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # US format with country code
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            # Return as-is for other formats
            return value
    
    def format_file_size(self, value: Union[int, float], 
                        binary: bool = True) -> str:
        """Format file size in human-readable format."""
        if value is None:
            return ""
        
        try:
            value = float(value)
            if value < 0:
                return "0 B"
            
            units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
            if binary:
                units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
                base = 1024
            else:
                base = 1000
            
            size = value
            unit_index = 0
            
            while size >= base and unit_index < len(units) - 1:
                size /= base
                unit_index += 1
            
            return f"{size:.1f} {units[unit_index]}"
        except Exception as e:
            logger.warning(f"Failed to format file size {value}: {e}")
            return str(value)
    
    def get_locale_info(self) -> dict:
        """Get information about the current locale."""
        return {
            'locale': str(self.babel_locale),
            'language': self.babel_locale.language,
            'territory': self.babel_locale.territory,
            'decimal_symbol': self.babel_locale.number_symbols['decimal'],
            'group_symbol': self.babel_locale.number_symbols['group'],
            'currency_symbol': self.babel_locale.currency_symbols.get('USD', '$'),
            'date_format': self.babel_locale.date_formats['short'].pattern,
            'time_format': self.babel_locale.time_formats['short'].pattern
        }
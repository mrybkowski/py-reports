"""Locale management for formatting and localization."""

import logging
from typing import Optional, Dict, Any
from babel import Locale
from babel.numbers import get_currency_symbol, get_decimal_symbol, get_group_symbol
from babel.dates import get_date_format, get_datetime_format, get_time_format

logger = logging.getLogger(__name__)


class LocaleManager:
    """Manages locale-specific formatting and symbols."""
    
    def __init__(self, default_locale: str = "en_US"):
        self.default_locale = default_locale
        self._locale_cache: Dict[str, Locale] = {}
    
    def get_locale(self, locale_str: str = None) -> Locale:
        """Get Babel Locale object for the given locale string."""
        if locale_str is None:
            locale_str = self.default_locale
        
        if locale_str not in self._locale_cache:
            try:
                self._locale_cache[locale_str] = Locale.parse(locale_str)
            except Exception as e:
                logger.warning(f"Failed to parse locale '{locale_str}': {e}")
                self._locale_cache[locale_str] = Locale.parse(self.default_locale)
        
        return self._locale_cache[locale_str]
    
    def get_currency_symbol(self, currency_code: str, locale_str: str = None) -> str:
        """Get currency symbol for the given currency and locale."""
        locale = self.get_locale(locale_str)
        try:
            return get_currency_symbol(currency_code, locale=locale)
        except Exception as e:
            logger.warning(f"Failed to get currency symbol for {currency_code} in {locale_str}: {e}")
            return currency_code
    
    def get_decimal_symbol(self, locale_str: str = None) -> str:
        """Get decimal separator for the locale."""
        locale = self.get_locale(locale_str)
        try:
            return get_decimal_symbol(locale)
        except Exception as e:
            logger.warning(f"Failed to get decimal symbol for {locale_str}: {e}")
            return "."
    
    def get_group_symbol(self, locale_str: str = None) -> str:
        """Get thousands separator for the locale."""
        locale = self.get_locale(locale_str)
        try:
            return get_group_symbol(locale)
        except Exception as e:
            logger.warning(f"Failed to get group symbol for {locale_str}: {e}")
            return ","
    
    def get_date_format(self, format_type: str = "short", locale_str: str = None) -> str:
        """Get date format pattern for the locale."""
        locale = self.get_locale(locale_str)
        try:
            return get_date_format(format_type, locale=locale)
        except Exception as e:
            logger.warning(f"Failed to get date format for {locale_str}: {e}")
            return "MM/dd/yyyy"
    
    def get_datetime_format(self, format_type: str = "short", locale_str: str = None) -> str:
        """Get datetime format pattern for the locale."""
        locale = self.get_locale(locale_str)
        try:
            return get_datetime_format(format_type, locale=locale)
        except Exception as e:
            logger.warning(f"Failed to get datetime format for {locale_str}: {e}")
            return "MM/dd/yyyy HH:mm"
    
    def get_time_format(self, format_type: str = "short", locale_str: str = None) -> str:
        """Get time format pattern for the locale."""
        locale = self.get_locale(locale_str)
        try:
            return get_time_format(format_type, locale=locale)
        except Exception as e:
            logger.warning(f"Failed to get time format for {locale_str}: {e}")
            return "HH:mm"
    
    def get_locale_info(self, locale_str: str = None) -> Dict[str, Any]:
        """Get comprehensive locale information."""
        locale = self.get_locale(locale_str)
        
        return {
            "language": locale.language,
            "territory": locale.territory,
            "display_name": str(locale),
            "currency_symbol": self.get_currency_symbol("USD", locale_str),
            "decimal_symbol": self.get_decimal_symbol(locale_str),
            "group_symbol": self.get_group_symbol(locale_str),
            "date_format": self.get_date_format("short", locale_str),
            "datetime_format": self.get_datetime_format("short", locale_str),
            "time_format": self.get_time_format("short", locale_str),
        }


# Global locale manager instance
_locale_manager: Optional[LocaleManager] = None


def get_locale_manager(default_locale: str = "en_US") -> LocaleManager:
    """Get locale manager instance (singleton pattern)."""
    global _locale_manager
    if _locale_manager is None:
        _locale_manager = LocaleManager(default_locale)
    return _locale_manager
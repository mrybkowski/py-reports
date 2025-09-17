"""Translation system with support for multiple languages."""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from babel import Locale
from babel.numbers import format_number, format_currency, format_decimal
from babel.dates import format_date, format_datetime, format_time
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger(__name__)


class Translator:
    """Handles translation and localization."""
    
    def __init__(self, translations_dir: str = "py_reports/translations", default_locale: str = "en_US"):
        self.translations_dir = Path(translations_dir)
        self.default_locale = default_locale
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._loaded_locales: set = set()
        
        # Load default locale
        self._load_locale(default_locale)
    
    def _load_locale(self, locale: str) -> None:
        """Load translations for a specific locale."""
        if locale in self._loaded_locales:
            return
        
        locale_file = self.translations_dir / f"{locale}.yaml"
        
        if not locale_file.exists():
            logger.warning(f"Translation file not found for locale {locale}: {locale_file}")
            if locale != self.default_locale:
                logger.info(f"Falling back to default locale: {self.default_locale}")
                self._load_locale(self.default_locale)
            return
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                translations = yaml.safe_load(f)
                self._translations[locale] = translations or {}
                self._loaded_locales.add(locale)
                logger.info(f"Loaded translations for locale: {locale}")
        except Exception as e:
            logger.error(f"Failed to load translations for {locale}: {e}")
            if locale != self.default_locale:
                self._load_locale(self.default_locale)
    
    def translate(self, key: str, locale: str = None, **kwargs) -> str:
        """
        Translate a key with optional parameters.
        
        Args:
            key: Translation key (e.g., "report.sales.title")
            locale: Target locale (defaults to default_locale)
            **kwargs: Parameters for string formatting
            
        Returns:
            Translated string
        """
        if locale is None:
            locale = self.default_locale
        
        # Load locale if not already loaded
        if locale not in self._loaded_locales:
            self._load_locale(locale)
        
        # Get translations for the locale
        translations = self._translations.get(locale, {})
        
        # Navigate through nested keys
        value = translations
        for part in key.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                # Fallback to default locale
                if locale != self.default_locale:
                    logger.warning(f"Translation key '{key}' not found in locale '{locale}', falling back to default")
                    return self.translate(key, self.default_locale, **kwargs)
                else:
                    logger.warning(f"Translation key '{key}' not found in default locale")
                    return key  # Return key as fallback
        
        if not isinstance(value, str):
            logger.warning(f"Translation value for '{key}' is not a string: {value}")
            return key
        
        # Format string with parameters
        try:
            return value.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing parameter {e} for translation key '{key}'")
            return value
    
    def format_number(self, value: Union[int, float, Decimal], locale: str = None, **kwargs) -> str:
        """Format a number according to locale."""
        if locale is None:
            locale = self.default_locale
        
        try:
            babel_locale = Locale.parse(locale)
            return format_number(value, locale=babel_locale, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to format number {value} for locale {locale}: {e}")
            return str(value)
    
    def format_currency(self, value: Union[int, float, Decimal], currency: str, locale: str = None, **kwargs) -> str:
        """Format currency according to locale."""
        if locale is None:
            locale = self.default_locale
        
        try:
            babel_locale = Locale.parse(locale)
            return format_currency(value, currency, locale=babel_locale, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to format currency {value} {currency} for locale {locale}: {e}")
            return f"{value} {currency}"
    
    def format_date(self, value: Union[date, datetime], locale: str = None, **kwargs) -> str:
        """Format date according to locale."""
        if locale is None:
            locale = self.default_locale
        
        try:
            babel_locale = Locale.parse(locale)
            if isinstance(value, datetime):
                return format_datetime(value, locale=babel_locale, **kwargs)
            else:
                return format_date(value, locale=babel_locale, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to format date {value} for locale {locale}: {e}")
            return str(value)
    
    def format_time(self, value: Union[datetime, str], locale: str = None, **kwargs) -> str:
        """Format time according to locale."""
        if locale is None:
            locale = self.default_locale
        
        try:
            babel_locale = Locale.parse(locale)
            if isinstance(value, str):
                # Parse time string
                time_obj = datetime.strptime(value, "%H:%M:%S").time()
            else:
                time_obj = value.time() if hasattr(value, 'time') else value
            
            return format_time(time_obj, locale=babel_locale, **kwargs)
        except Exception as e:
            logger.warning(f"Failed to format time {value} for locale {locale}: {e}")
            return str(value)
    
    def get_available_locales(self) -> list:
        """Get list of available locales."""
        return [f.stem for f in self.translations_dir.glob("*.yaml") if f.is_file()]


# Global translator instance
_translator: Optional[Translator] = None


def get_translator(translations_dir: str = "py_reports/translations", default_locale: str = "en_US") -> Translator:
    """Get translator instance (singleton pattern)."""
    global _translator
    if _translator is None:
        _translator = Translator(translations_dir, default_locale)
    return _translator
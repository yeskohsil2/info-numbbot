# utils.py
import re
import logging
from typing import Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SUPPORTED_COUNTRIES = {
    '77': 'KZ',
    '7': 'RU',
    '380': 'UA',
    '375': 'BY',
    '996': 'KG',
    '992': 'TJ',
    '993': 'TM',
    '998': 'UZ',
    '994': 'AZ',
    '995': 'GE',
    '374': 'AM',
    '373': 'MD'
}

def normalize_phone(phone: str) -> Optional[Tuple[str, str]]:
    digits = re.sub(r'\D', '', phone)
    
    if not digits:
        return None
    
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    
    sorted_codes = sorted(SUPPORTED_COUNTRIES.keys(), key=len, reverse=True)
    
    for code in sorted_codes:
        if digits.startswith(code):
            country_code = code
            national_number = digits[len(code):]
            if len(national_number) >= 9:
                formatted = f"+{country_code}{national_number}"
                return formatted, SUPPORTED_COUNTRIES[country_code]
    
    if len(digits) == 10:
        return f"+7{digits}", 'RU'
    
    return None

def format_phone_for_url(phone: str) -> str:
    return re.sub(r'\D', '', phone)

def truncate_text(text: str, max_length: int = 150) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'

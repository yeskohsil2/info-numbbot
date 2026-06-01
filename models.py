# models.py (обновленный)
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PhoneReport:
    phone: str
    country: str
    is_valid: bool = False
    is_spam: bool = False
    spam_categories: List[str] = field(default_factory=list)
    carrier: str = ""
    line_type: str = ""
    location: str = ""
    region: str = ""
    city: str = ""
    risk_level: str = "unknown"
    is_disposable: bool = False
    total_breaches: int = 0
    breach_domains: List[str] = field(default_factory=list)
    registered_name: str = ""
    registration_type: str = ""
    international_format: str = ""
    local_format: str = ""
    country_name: str = ""
    country_prefix: str = ""
    original_carrier: str = ""
    ported: str = ""
    caller_name: str = ""
    roaming: bool = False

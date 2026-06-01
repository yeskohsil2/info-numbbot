# checkers.py
import asyncio
import aiohttp
from typing import Optional, Dict
from config import Config
from utils import logger, format_phone_for_url
from models import PhoneReport

class PhoneChecker:
    def __init__(self, phone: str, country: str):
        self.phone = phone
        self.clean_phone = format_phone_for_url(phone)
        self.country = country
        self.report = PhoneReport(phone=phone, country=country)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=Config.TIMEOUT_SECONDS)
        connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300, ssl=False)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_json(self, url: str, params: Optional[Dict] = None, method: str = "GET", json_data: Optional[Dict] = None) -> Optional[Dict]:
        for attempt in range(Config.MAX_RETRIES + 1):
            try:
                if method == "POST":
                    async with self.session.post(url, params=params, json=json_data, ssl=False) as resp:
                        if resp.status == 200:
                            return await resp.json()
                else:
                    async with self.session.get(url, params=params, ssl=False) as resp:
                        if resp.status == 200:
                            return await resp.json()
                logger.warning(f"Status {resp.status} for {url}")
                return None
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt == Config.MAX_RETRIES:
                    return None
                await asyncio.sleep(Config.RETRY_BACKOFF_FACTOR * (attempt + 1))
        return None

    async def check_spravportal(self):
        try:
            url = f"{Config.SPRAVPORTAL_API_URL}?apiKey={Config.SPRAVPORTAL_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "phones": [self.clean_phone],
                "params": {
                    "allowOrganizations": True,
                    "showPhoneInfo": True,
                    "showOrganization": True
                }
            }
            
            async with self.session.post(url, headers=headers, json=payload, ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and "phones" in data and data["phones"]:
                        phone_data = data["phones"][0]
                        if phone_data.get("action") == "Block":
                            self.report.is_spam = True
                            self.report.spam_categories = phone_data.get("categories", [])
                            
                            phone_info = phone_data.get("phoneInfo", {})
                            if phone_info and phone_info.get("operator"):
                                self.report.carrier = phone_info.get("operator")
                
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Spravportal error: {e}")

    async def check_numverify(self):
        try:
            params = {
                "access_key": Config.NUMVERIFY_API_KEY,
                "number": self.clean_phone,
                "format": 1
            }
            data = await self.fetch_json(Config.NUMVERIFY_API_URL, params)
            
            if data and isinstance(data, dict):
                self.report.is_valid = data.get("valid", False)
                self.report.international_format = data.get("international_format", "")
                self.report.local_format = data.get("local_format", "")
                self.report.country_prefix = data.get("country_prefix", "")
                self.report.country_name = data.get("country_name", "")
                self.report.location = data.get("location", "")
                self.report.carrier = self.report.carrier or data.get("carrier", "")
                self.report.line_type = data.get("line_type", "")
                
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Numverify error: {e}")

    async def check_numlookup(self):
        try:
            url = f"{Config.NUMLOOKUP_API_URL}/{self.clean_phone}?apikey={Config.NUMLOOKUP_API_KEY}"
            data = await self.fetch_json(url)
            
            if data and isinstance(data, dict):
                self.report.is_valid = self.report.is_valid or data.get("valid", False)
                self.report.international_format = self.report.international_format or data.get("international_format", "")
                self.report.local_format = self.report.local_format or data.get("local_format", "")
                self.report.country_prefix = self.report.country_prefix or data.get("country_prefix", "")
                self.report.country_name = self.report.country_name or data.get("country_name", "")
                self.report.location = self.report.location or data.get("location", "")
                self.report.carrier = self.report.carrier or data.get("carrier", "")
                self.report.line_type = self.report.line_type or data.get("line_type", "")
                
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Numlookup error: {e}")

    async def check_abstract(self):
        try:
            params = {
                "api_key": Config.ABSTRACT_API_KEY,
                "phone": self.clean_phone
            }
            data = await self.fetch_json(Config.ABSTRACT_API_URL, params)
            
            if data and isinstance(data, dict):
                validation = data.get("phone_validation")
                if validation and isinstance(validation, dict):
                    self.report.is_valid = self.report.is_valid or validation.get("is_valid", False)
                    self.report.is_disposable = validation.get("is_voip", False)
                
                phone_format = data.get("phone_format")
                if phone_format and isinstance(phone_format, dict):
                    self.report.international_format = self.report.international_format or phone_format.get("international", "")
                    self.report.local_format = self.report.local_format or phone_format.get("national", "")
                
                carrier = data.get("phone_carrier")
                if carrier and isinstance(carrier, dict):
                    self.report.carrier = self.report.carrier or carrier.get("name", "")
                    self.report.line_type = self.report.line_type or carrier.get("line_type", "")
                
                location = data.get("phone_location")
                if location and isinstance(location, dict):
                    self.report.country_name = self.report.country_name or location.get("country_name", "")
                    self.report.country_prefix = self.report.country_prefix or location.get("country_prefix", "")
                    self.report.region = location.get("region", "")
                    self.report.city = location.get("city", "")
                
                risk = data.get("phone_risk")
                if risk and isinstance(risk, dict):
                    risk_level = risk.get("risk_level")
                    if risk_level:
                        self.report.risk_level = risk_level
                    self.report.is_disposable = self.report.is_disposable or risk.get("is_disposable", False)
                
                breaches = data.get("phone_breaches")
                if breaches and isinstance(breaches, dict):
                    total = breaches.get("total_breaches")
                    if total:
                        self.report.total_breaches = total
                    breached_domains = breaches.get("breached_domains", [])
                    if breached_domains and isinstance(breached_domains, list):
                        for domain_info in breached_domains:
                            if domain_info and isinstance(domain_info, dict):
                                domain = domain_info.get("domain")
                                if domain:
                                    self.report.breach_domains.append(domain)
                
                registration = data.get("phone_registration")
                if registration and isinstance(registration, dict):
                    name = registration.get("name")
                    if name:
                        self.report.registered_name = name
                    reg_type = registration.get("type")
                    if reg_type:
                        self.report.registration_type = reg_type
                
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Abstract API error: {e}")

    async def check_vonage(self):
        try:
            params = {
                "api_key": Config.VONAGE_API_KEY,
                "api_secret": Config.VONAGE_API_SECRET,
                "number": self.clean_phone
            }
            
            data = await self.fetch_json(Config.VONAGE_API_URL, params)
            
            if data and isinstance(data, dict):
                if data.get("status") == 0:
                    self.report.international_format = self.report.international_format or data.get("international_format_number", "")
                    self.report.local_format = self.report.local_format or data.get("national_format_number", "")
                    self.report.country_name = self.report.country_name or data.get("country_name", "")
                    self.report.country_prefix = self.report.country_prefix or data.get("country_prefix", "")
                    
                    current_carrier = data.get("current_carrier")
                    if current_carrier and isinstance(current_carrier, dict):
                        carrier_name = current_carrier.get("name")
                        if carrier_name:
                            self.report.carrier = self.report.carrier or carrier_name
                        network_type = current_carrier.get("network_type")
                        if network_type:
                            self.report.line_type = self.report.line_type or network_type
                    
                    original_carrier = data.get("original_carrier")
                    if original_carrier and isinstance(original_carrier, dict):
                        self.report.original_carrier = original_carrier.get("name", "")
                    
                    ported = data.get("ported")
                    if ported:
                        self.report.ported = ported
                    
                    caller_identity = data.get("caller_identity")
                    if caller_identity and isinstance(caller_identity, dict):
                        caller_name = caller_identity.get("caller_name")
                        if caller_name:
                            self.report.caller_name = caller_name
                        caller_type = caller_identity.get("caller_type")
                        if caller_type:
                            self.report.registration_type = self.report.registration_type or caller_type
                    
                    roaming = data.get("roaming")
                    if roaming and isinstance(roaming, dict):
                        self.report.roaming = roaming.get("status") == "roaming"
                
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Vonage API error: {e}")

    async def check_all(self):
        await asyncio.gather(
            self.check_spravportal(),
            self.check_numverify(),
            self.check_numlookup(),
            self.check_abstract(),
            self.check_vonage()
        )
        return self.report

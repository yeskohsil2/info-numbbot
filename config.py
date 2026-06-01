# config.py (обновленный)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8797859344:AAHxm-JDJHgdXE_03z6M6rgycJw4gdweDnE")
    
    SPRAVPORTAL_API_KEY = "sp_test_3tScdl40"
    SPRAVPORTAL_API_URL = "https://b2b-api-stage-05.spravportal.ru/whocalls/check"
    
    NUMVERIFY_API_KEY = "4e3f608031ee4ec0d21cb54d1ebe602c"
    NUMVERIFY_API_URL = "https://apilayer.net/api/validate"
    
    NUMLOOKUP_API_KEY = "num_live_ZuRVskicHfkr5uXaU1ep5MWeAxrur2tYMR6VQXPD"
    NUMLOOKUP_API_URL = "https://api.numlookupapi.com/v1/validate"
    
    ABSTRACT_API_KEY = "a9882fa01d284ce7b12c4aa030b86773"
    ABSTRACT_API_URL = "https://phoneintelligence.abstractapi.com/v1"
    
    VONAGE_API_KEY = "2bfd3620"
    VONAGE_API_SECRET = "tGE7n$UK!cbF*B^kOq*f5N16"
    VONAGE_API_URL = "https://api.nexmo.com/ni/standard/json"
    
    TIMEOUT_SECONDS = 10
    MAX_RETRIES = 2
    RETRY_BACKOFF_FACTOR = 1.5

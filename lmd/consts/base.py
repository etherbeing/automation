
BASE_URL = "https://www.mjusticia.gob.es/"
DIOCESIS_BASE_URL = 'https://www.conferenciaepiscopal.es/'
SCRAPPING_CONCERN_EMAIL = "n4b3ts3@gmail.com"
MAX_RETRIES = 3                
USER_AGENT = f"AutomationLMD/1.0 (Contact: {SCRAPPING_CONCERN_EMAIL}, any issue regarding the requests please contact me, this is just for helping to automate the LMD law)"
TIMEWAIT = 0.25

CACHE_TIME = 60*60*60*24 # 1 day
I18N_STANDARD = {
    "dirección": "address",
    "teléfono":"phone",
    "fax": "fax",
    "localidad": "locality",
    "códigopostal": "postal_code",
    "email": "email"
}
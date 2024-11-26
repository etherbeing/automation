from django.conf import settings
import redis
from os import getenv
# Connect to our Redis instance
redis_instance = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT, 
    # password=getenv("YOUR_ENV_VARNAME"),
    db=0
)
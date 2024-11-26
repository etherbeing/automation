# storage.py
from django.core.exceptions import ImproperlyConfigured
from storages.backends.s3boto3 import S3Boto3Storage
from security.models import S3Configuration

class DynamicS3Boto3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        # Fetch the active configuration
        try:
            config = S3Configuration.objects.get(is_active=True)
        except S3Configuration.DoesNotExist:
            raise ImproperlyConfigured("No active S3 configuration found.")

        # Pass the settings dynamically
        kwargs['access_key'] = config.access_key
        kwargs['secret_key'] = config.secret_key
        kwargs['bucket_name'] = config.bucket_name
        kwargs['endpoint_url'] = config.endpoint_url

        super().__init__(*args, **kwargs)

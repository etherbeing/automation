from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group, Permission

# Create your models here.

class S3Configuration(models.Model):
    access_key = models.CharField(max_length=128, verbose_name=_("Llave de Acceso"))
    secret_key = models.CharField(max_length=128, verbose_name=_("Llave secreta"))
    bucket_name = models.CharField(max_length=128, verbose_name=_("Nombre del Bucket")) # Traducir bucket le quita calidad 😄
    endpoint_url = models.URLField(verbose_name=_("URL del servicio"))
    is_active = models.BooleanField(default=True, verbose_name=_("Está activo"))  # Use this to mark the active configuration

    def __str__(self):
        return self.bucket_name
    
    class Meta:
        verbose_name = _("S3 Configuración")
        verbose_name_plural = verbose_name

class User(AbstractUser):
    pass

class IdentityUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="identity")
    dni = models.ImageField(verbose_name=_("DNI"), null=True, blank=True, help_text=_("DNI o Carnet de Identidad"))
    dni_number = models.CharField(verbose_name=_("No. DNI"),  null=True, blank=True, help_text=_("Número de Identidad"))
    phone = models.CharField(verbose_name=_("Teléfono"),  null=True, blank=True, help_text=_("Número de teléfono"))
    
    def __str__(self) -> str:
        return f"{self.dni_number}: {self.phone}"
    
    class Meta:
        verbose_name = _("Datos de Identidad")
        verbose_name_plural = _("Datos de Identidades")

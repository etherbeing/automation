import json
import logging
from celery import Task
from django.db import models
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext as _
from crum import get_current_request
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.mail import get_connection
from lmd.tasks import send_emails
from lmd.consts.base import CACHE_TIME
from base.redis import redis_instance

User = get_user_model()

# Create your models here.
class ProvinceModel(models.Model):
    @property
    def official_link(self,):
        return f"""https://www.mjusticia.gob.es/BUSCADIR/ServletControlador?lang=es_es&apartado=buscadorMunicipios&URL_ORIGEN=&origen=G&tipo=RC&provincia={self.pk}"""
    id = models.CharField(unique=True, verbose_name=_("ID"), primary_key=True, auto_created=False)
    name = models.CharField(verbose_name=_("Nombre"))
    municipalities: models.Manager
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = _("Provincia")
        verbose_name_plural = _("Provincias")

class MunicipalityModel(models.Model):
    official_link = models.URLField(default=None, null=True, )
    id = models.CharField(unique=True, verbose_name=_("ID"), primary_key=True, auto_created=False)
    name = models.CharField(verbose_name=_("Nombre"))
    province = models.ForeignKey(
        ProvinceModel, related_name="municipalities", 
        on_delete=models.CASCADE, null=False, blank=False, 
        verbose_name=_("Provincia")
    )

    @property
    def link(self,):
        return mark_safe(f"<a href=\"{self.official_link}\" target=\"_blank\">{_('Sitio Oficial')}</a>")

    def __str__(self) -> str:
        return f"{self.name}, {self.province.name}"
    
    class Meta:
        verbose_name = _("Municipio")
        verbose_name_plural = _("Municipios")

# Note: Names in spanish are in order to be more precise in what we want for
class RegistroCivilModel(models.Model):
    locality = models.CharField(verbose_name=_("Localidad"), default=None)
    postal_code = models.CharField(verbose_name=_("Código Postal"), default=None)
    address = models.CharField(verbose_name=_("Dirección"), default=None)
    fax = models.CharField(verbose_name=_("Fax"), default=None, null=True)
    phone = models.CharField(verbose_name=_("Teléfono"), null=True)
    email = models.EmailField(verbose_name=_("Correo Electrónico"), null=True,)
    municipality = models.OneToOneField(MunicipalityModel, related_name="civil_registry", on_delete=models.PROTECT, null=False, blank=False, verbose_name=_("Municipio"))

    def __str__(self) -> str:
        return f"{self.locality}: {self.email}, {self.phone}, {self.municipality}"
    
    class Meta:
        verbose_name = _("Registro Civil")
        verbose_name_plural = _("Registros Civiles")

class DiocesisModel(models.Model):
    name = models.CharField(verbose_name=_("Nombre"))
    phone = models.CharField(verbose_name=_("Teléfono"))
    extra_phone = models.CharField(verbose_name=_("Teléfono Adicional"), null=True, blank=True)
    email = models.EmailField(verbose_name=_("Correo Eléctronico"))
    province = models.ForeignKey(ProvinceModel, on_delete=models.PROTECT, null=True, blank=False, verbose_name=_("Provincia"))
    
    @property
    def locality(self):
        return str(self.province or "")

    def __str__(self) -> str:
        return f"{self.name}: {self.email}, {self.phone}, {self.province}"
    
    class Meta:
        verbose_name = _("Diocesis")
        verbose_name_plural = _("Diocesis")

class EmailSettingsModel(models.Model):
    smtp_username = models.CharField(default=None, null=True, blank=True, verbose_name=_("Nombre de Usuario (SMTP)"))
    smtp_password = models.CharField(default=None, null=True, blank=True, verbose_name=_("Contraseña (SMTP)"))
    smtp_host = models.CharField(default=None, null=True, blank=True, verbose_name=_("Servidor (SMTP)"))
    smtp_port = models.IntegerField(default=None, null=True, blank=True, verbose_name=_("Puerto TCP (SMTP)"))
    
    imap_username = models.CharField(default=None, null=True, blank=True, verbose_name=_("Nombre de Usuario (IMAP)"))
    imap_password = models.CharField(default=None, null=True, blank=True, verbose_name=_("Contraseña (IMAP)"))
    imap_host = models.CharField(default=None, null=True, blank=True, verbose_name=_("Servidor (IMAP)"))
    imap_port = models.IntegerField(default=None, null=True, blank=True, verbose_name=_("Puerto TCP (IMAP)"))
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self) -> str:
        return self.user.email or str(self.pk)
    
    class Meta:
        verbose_name = _("Configuracion de correo")
        verbose_name_plural = _("Configuraciones de correos")

class AttachmentModel(models.Model):
    name = models.CharField(verbose_name=_("Nombre"))
    file = models.FileField(verbose_name=_("Archivo"))

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural = _("Archivos")

class Person(models.Model):
    father = models.ForeignKey("self", on_delete=models.PROTECT, verbose_name=_("Padre"), related_name="father_child")
    mother = models.ForeignKey("self", on_delete=models.PROTECT, verbose_name=_("Madre"), related_name="mother_child")
    legal_name = models.CharField(default=None, verbose_name=_("Nombre Legal"))
    family_name = models.CharField(default=None, verbose_name=_("Nombre de Familia"))
    
    def __str__(self) -> str:
        return self.legal_name
    
    class Meta:
        verbose_name = _("Persona")
        verbose_name_plural = _("Personas")

class CorreosModel(models.Model):
    PURPOSES = {
        "lmd":_("Obtención de la ciudadanía española mediante la Ley de Memoria Democrática"),
    }
    # datos del solicitante
    user = models.ForeignKey(to=get_user_model(), on_delete=models.PROTECT, default=None, auto_created=True)

    # Nacimiento
    full_name = models.CharField(
        default=None,
        verbose_name=_("Nombre completo"), help_text=_("Nombre completo de la persona de la cual se quiere solicitar su certificado")
    )
    birthday = models.DateField(
        default=None, verbose_name=_("Fecha de nacimiento"), 
        help_text=_("Fecha de nacimiento de la persona de la cual se quiere solicitar su certificado")
    )
    father_fullname = models.CharField(
        default=None,
        verbose_name=_("Nombre completo del Padre"), 
        help_text=_("Nombre completo del padre de la persona de la cual se quiere solicitar su certificado")
    )
    mother_fullname = models.CharField(
        default=None,
        verbose_name=_("Nombre completo de la Madre"), 
        help_text=_("Nombre completo de la Madre de la persona de la cual se quiere solicitar su certificado")
    )

    relationship = models.CharField(
        default=None,
        verbose_name=_("Relación"),
        help_text=_("Relación, por ejemplo, padre, madre, abuelo, abuela, bisabuelo o bisabuela")
    )
    purpose = models.CharField(
        default=None,
        verbose_name=_("Propósito"),
        help_text=_("Propósito con el cual se solicita el certificado de nacimiento actual"),
        choices=PURPOSES.items()
    )

    attachments = models.ManyToManyField(
        AttachmentModel, 
        verbose_name=_("Archivos"),
        help_text=_("Archivos extras adjuntos"),
        blank=True
    )

    municipality = models.ForeignKey(
        verbose_name=_("Municipio"),
        to=MunicipalityModel, 
        on_delete=models.SET_NULL, 
        default=None, 
        null=True, 
        blank=True
    )
    province = models.ForeignKey(
        verbose_name=_("Provincia"),
        to=ProvinceModel, 
        on_delete=models.SET_NULL, 
        default=None, 
        null=True, 
        blank=True
    )
    content_type = models.CharField(
        choices=(
            ("any", _("Todos")),
            ("diocesis", _("Diocesis")),
            ("civil", _("Registro Civil")),
        ), 
        verbose_name=_("Tipo de correo"),
        default="any"
    )

    extra_content = models.TextField(null=True, blank=True, verbose_name=_("Información Adicional"))
    
    @property
    def purpose_value(self,):
        return self.PURPOSES[self.purpose]
    
    @property
    def birthplace(self): 
        return str(
            self.municipality or self.province
        )
    
    @property
    def is_diocesis(self,):
        return self.content_type == "diocesis" or self.content_type == "any"
    
    @property
    def is_civil_registry(self,):
        return self.content_type == "civil" or self.content_type == "any"    

    @property
    def location(self):
        if self.municipality:
            location = str(self.municipality)
        else:
            location = str(self.province)
        return location

    def _get_context(self, scope: DiocesisModel|RegistroCivilModel=None):
        return {
            "email_context": self,
            "location": (scope and scope.locality) or self.location
        }

    def _get_emails(self, request: HttpRequest):
        if not request.user.is_authenticated:
            return
        redis_key = f"{self.pk}-emails"
        data = redis_instance.get(redis_key)
        if data:
            return json.loads(data)
        diocesis = DiocesisModel.objects.none()
        civil_registries = {}
        diocesis = {}
        if self.is_civil_registry:
            qs = models.Q(municipality=self.municipality)
            if self.province:
                qs = qs|models.Q(municipality__in=self.province.municipalities.all())
            for civil_model in RegistroCivilModel.objects.filter(qs):
                civil_registries[civil_model.email] = {
                    "email": civil_model.email,
                    # "object": civil_model,
                    "type": "civil",
                    "subject": _("Solicitud de certifico de nacimiento"),
                    "content": render_to_string("civil_registry.email.html", context=self._get_context(scope=civil_model), request=request)
                }
        if self.is_diocesis:
            qs = models.Q(province=self.province)
            if self.municipality:
                qs = qs|models.Q(province=self.municipality.province)
            for diocesis_model in DiocesisModel.objects.filter(qs):
                diocesis[diocesis_model.email] = {
                    "email": diocesis_model.email,
                    # "object": diocesis_model,
                    "type": "diocesis",
                    "subject": _("Solicitud de Fé de Bautismo"),
                    "content": render_to_string("diocesis.email.html", context=self._get_context(scope=diocesis_model), request=request)
                }
        res = [*civil_registries.values(), *diocesis.values()]
        redis_instance.set(redis_key, json.dumps(res), ex=CACHE_TIME)
        return res

    def _get_scoped_connection(self, ):
        redis_key = f"{self.user.pk}-connection-params"
        connection = redis_instance.get(redis_key)
        if connection:
            connection = json.loads(connection)
        else:
            email_setting = EmailSettingsModel.objects.filter(user=self.user).values()
            if email_setting:
                email_setting = email_setting[0]
                connection = {
                    "username": email_setting.get('smtp_username'),
                    "password": email_setting.get('smtp_password'),
                    "host": email_setting.get('smtp_host'),
                    "port": email_setting.get('smtp_port'),
                }
                redis_instance.set(redis_key, json.dumps(connection), ex=CACHE_TIME)
            else:
                return None
        return get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend", 
            **connection
        )

    def send(self, request: HttpRequest):
        send_emails.delay(email_model_pk=self.pk,  emails=self._get_emails(request=request))
    
    def save(self, *args, **kwargs):
        request = get_current_request()
        if not request.user.is_authenticated:
            raise ValidationError("Trying to create an email when the current user is not authenticated")
        self.user = request.user
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.full_name}, {self.content_type}, {self.municipality or self.province}"
    
    class Meta:
        verbose_name = _("Correo")
        verbose_name_plural = _("Correos")
from crum import get_current_request, get_current_user
from django.contrib import admin
from django.db.models import QuerySet, Q
from django.http import HttpRequest
from lmd.models import AttachmentModel, CorreosModel, EmailSettingsModel, MunicipalityModel, Person, ProvinceModel, RegistroCivilModel, DiocesisModel
from django.utils.translation import gettext as _
from django.contrib.messages import WARNING
from django.utils.safestring import mark_safe

# Register your models here.
class EmailSettingInline(admin.StackedInline):
    model = EmailSettingsModel
    max_num = 1
    min_num = 1
    extra = 1

class MunicipalityInline(admin.TabularInline):
    model = MunicipalityModel
    extra = 0
    fields = ("id", "name")
    sortable_by = ("id", "name")

@admin.register(RegistroCivilModel)
class RegistroCivilAdmin(admin.ModelAdmin):
    search_fields = ("locality", "postal_code", "address", "fax","phone", "email", "municipality__name",)
    list_filter = ("municipality__province", )
    sortable_by = ("municipality", )
    list_display = (
        "locality",
        "postal_code",
        "address",
        "fax",
        "phone",
        "email",
        "municipality",
    )
    actions = ("improve", "improve_step")

    @admin.action(description=_("Revisar siguiente problema"))
    def improve_step(self, request: HttpRequest, queryset: QuerySet[RegistroCivilModel]):
        for registry in queryset:
            occurrencies = queryset.filter(email=registry.email)
            count = occurrencies.count()
            if count > 1:
                self.message_user(
                    request=request, message=_("Se encontraron %s veces el elemento: %s"%(count, registry)), 
                    level=WARNING
                )
                for occurrency in occurrencies:
                    self.message_user(
                        request=request, message=mark_safe(_("Duplicado: %s, link: %s"%(occurrency, f"<a href=\"{occurrency.municipality.official_link}\">Ver más</a>"))), 
                        level=WARNING
                    )    
                break

    @admin.action(description=_("Revisar filtros"))
    def improve(self, request: HttpRequest, queryset: QuerySet[RegistroCivilModel]):
        for registry in queryset:
            occurrencies = queryset.filter(email=registry.email).count()
            if occurrencies > 1:
                self.message_user(
                    request=request, message=_("Se encontraron %s veces el elemento: %s"%(occurrencies, registry)), 
                    level=WARNING
                )

@admin.register(DiocesisModel)
class DiocesisAdmin(admin.ModelAdmin):
    list_display = ('name', "phone", "extra_phone", "email", "province")
    search_fields = ('name', 'phone', 'extra_phone', 'email', "province__name")
    actions = ("seek_data", )

    @admin.action(description=_("Rellenar datos"))
    def seek_data(self, request, queryset: QuerySet[DiocesisModel]):
        print(request, queryset)
        for diocesis in queryset.filter(province=None):
            municipality = MunicipalityModel.objects.filter(Q(name__icontains=diocesis.name)|Q(province__name__icontains=diocesis.name)).first()
            diocesis.province = municipality and municipality.province
            diocesis.save()

@admin.register(CorreosModel)
class CorreosAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Datos de la persona a buscar"), {
            "fields": ("full_name", "birthday", "father_fullname", "mother_fullname", "municipality", "province")
        }),
        (_("Datos de la persona que busca"), {
            "fields": ("relationship",)
        }),
        (_("Datos adicionales"), {
            "fields": ("purpose", "attachments", "content_type",)
        }),
    )
    list_display = ("full_name", "birthplace", "relationship", "user")
    
    @property
    def list_editable(self,):
        user = get_current_user()
        if user and user.is_superuser:
            return ["user", ]
        else:
            return []

    actions = ("send",)

    @admin.action(
        description=_("Enviar")
    )
    def send(self, request: HttpRequest, queryset: QuerySet[CorreosModel]):
        for email in queryset:
            email.send(request)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("legal_name", "family_name", "father", "mother")
    search_fields = ("legal_name", "family_name")

@admin.register(AttachmentModel)
class AttachmentsAdmin(admin.ModelAdmin):
    pass

@admin.register(MunicipalityModel)
class MunicipalityAdmin(admin.ModelAdmin):
    search_fields = ("name", "province__name", "id", "official_link", )
    list_display = ("id", "name", "province", "link",)
    list_filter = ("province", )
            

@admin.register(ProvinceModel)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    list_display_links = ("id", "name",)
    search_fields = ("id", "name", "municipalities__name__icontains")
    fields = ("id", "name",)
    inlines = (MunicipalityInline, )
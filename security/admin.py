from typing import Any
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models.query import QuerySet, EmptyQuerySet, RawQuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from solo.admin import SingletonModelAdmin
from security.models import IdentityUser, S3Configuration
from lmd.admin import EmailSettingInline

# Register your models here.
class IdentityInline(admin.StackedInline):
    model = IdentityUser
    extra = 0
    max_num = 1
    min_num = 1


@admin.register(S3Configuration)
class S3ConfigurationAdmin(SingletonModelAdmin):
    list_display = ('bucket_name', 'endpoint_url', 'is_active')
    list_filter = ('is_active',)

@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    readonly_fields = (
        "date_joined",
        "last_login"
    )
    inlines = (
        EmailSettingInline,
        IdentityInline
    )
    list_editable = (
        "is_staff",
    )

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, str] | None = None) -> TemplateResponse:
        if request.user.is_superuser:
            return super().changelist_view(request, extra_context)
        else:
            qs = self.get_queryset(request=request)
            object = qs.first() or qs.create()
            return super().changeform_view(
                request=request,
                object_id=str(object.pk), 
                extra_context=extra_context
            )
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return get_user_model().objects.filter(pk=request.user.pk)
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return super().has_add_permission(request) and request.user.is_superuser
    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return super().has_delete_permission(request, obj) and request.user.is_superuser
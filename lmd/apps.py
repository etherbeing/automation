from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class LmdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lmd'
    verbose_name = _("Ley de Memoria Democrática")
    def ready(self) -> None:
        import lmd.signals
        return super().ready()
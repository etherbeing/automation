from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps


def migrate(state: StateApps, editor: BaseDatabaseSchemaEditor, *args, **kwargs):
    old_user = state.get_model("auth", "User")
    new_user = state.get_model("security", "User")
    for user_values in old_user.objects.all().values():
        new_user.objects.create(**user_values)
    editor.delete_model(old_user)
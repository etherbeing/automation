from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(user_signed_up)
def assign_user_to_group(sender, request, user, **kwargs):
    # Replace 'YourGroupName' with the name of your desired group
    group_name = "LMD"
    try:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
    except Group.DoesNotExist:
        # Optionally handle the case where the group does not exist
        pass

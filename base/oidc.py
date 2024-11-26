from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.admin import AdminSite

class CustomOIDCAB(OIDCAuthenticationBackend):
    GROUPS_KEY = "groups"
    ADMIN_GROUP = "admin"
    
    def verify_claims(self, claims):
        verified = super().verify_claims(claims)
        is_admin = self.ADMIN_GROUP in claims.get(self.GROUPS_KEY, [])
        return verified and is_admin
    
    def create_user(self, claims):
        """Return object for a newly created user account."""
        email = claims.get("email")
        username = self.get_username(claims)

        return self.UserModel.objects.create_user(
            username, email=email,
            first_name=claims.get("given_name"),
            last_name=claims.get("family_name"),
            is_staff=True,
            is_superuser=(self.ADMIN_GROUP in claims.get(self.GROUPS_KEY))
        )
    
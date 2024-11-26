"""
URL configuration for automation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from lmd.views import preview_demo_civil_registry_pdf, preview_demo_diocesis_pdf

urlpatterns = [
    path('preview/civil-registry.email.html', preview_demo_civil_registry_pdf, name="preview_dcrp"),
    path('preview/diocesis.email.html', preview_demo_diocesis_pdf, name="preview_ddp"),
    path('admin/', admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),
]

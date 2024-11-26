import logging
from django.http import HttpRequest
from django.shortcuts import render
from django.http.response import HttpResponseBadRequest
from lmd.models import CorreosModel
from random import randint


# Create your views here.
def preview_demo_civil_registry_pdf(request: HttpRequest):
    logging.info(request.user)
    email_context = CorreosModel.objects.filter(user=request.user)
    if not email_context.exists():
        return HttpResponseBadRequest("You need to first create at least one Email intention from the admin site")
    email_context = email_context[randint(0, email_context.count()-1)]
    return render(request, "civil_registry.email.html", context=email_context._get_context())


def preview_demo_diocesis_pdf(request: HttpRequest):
    email_context = CorreosModel.objects.filter(user=request.user)
    if not email_context.exists():
        return HttpResponseBadRequest("You need to first create at least one Email intention from the admin site")
    email_context = email_context[randint(0, email_context.count()-1)]
    return render(request, "diocesis.email.html", context=email_context._get_context())
from celery import shared_task
from django.core.mail import EmailMultiAlternatives

from lmd.data.s3 import get_file


@shared_task
def send_emails(email_model_pk: str, emails: dict, *args, **kwargs):
    from lmd.models import CorreosModel
    email_instance = CorreosModel.objects.get(pk=email_model_pk)

    for email in emails:
        base = EmailMultiAlternatives()
        base.from_email = email_instance.user.email
        base.reply_to = [email_instance.user.email]
        base.connection=email_instance._get_scoped_connection()
        base.content_subtype = "html"
        if email.get("type") == "civil":
            for attachment in email_instance.attachments.all():
                base.attach(filename=attachment.file.name,content=get_file(attachment.file.url))
        base.subject = email.get("subject")
        base.body=email.get("content")
        base.to=[email.get("email")]
        base.send(fail_silently=False)
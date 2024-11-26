# Generated by Django 5.1.1 on 2024-11-26 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmd', '0029_person'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name': 'Persona', 'verbose_name_plural': 'Personas'},
        ),
        migrations.AddField(
            model_name='person',
            name='family_name',
            field=models.CharField(default=None, verbose_name='Nombre de Familia'),
        ),
        migrations.AddField(
            model_name='person',
            name='legal_name',
            field=models.CharField(default=None, verbose_name='Nombre Legal'),
        ),
    ]
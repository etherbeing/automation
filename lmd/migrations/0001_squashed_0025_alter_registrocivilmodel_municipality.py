# Generated by Django 5.1.1 on 2024-11-24 04:06

import django.contrib
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('lmd', '0001_initial'), ('lmd', '0002_alter_attachmentmodel_options_and_more'), ('lmd', '0003_alter_emailsettingsmodel_imap_host_and_more'), ('lmd', '0004_alter_attachmentmodel_file_and_more'), ('lmd', '0005_provincemodel_official_link'), ('lmd', '0006_remove_provincemodel_official_link'), ('lmd', '0007_alter_provincemodel_id'), ('lmd', '0008_remove_registrocivilmodel_name_and_more'), ('lmd', '0009_alter_registrocivilmodel_email_and_more'), ('lmd', '0010_municipalitymodel_is_singleton'), ('lmd', '0011_remove_municipalitymodel_is_singleton_and_more'), ('lmd', '0012_diocesismodel_extra_phone'), ('lmd', '0013_alter_diocesismodel_municipality'), ('lmd', '0014_correosmodel_content_type_correosmodel_municipality_and_more'), ('lmd', '0015_remove_correosmodel_object_id_and_more'), ('lmd', '0016_alter_correosmodel_content_type_and_more'), ('lmd', '0017_correosmodel_province_and_more'), ('lmd', '0018_alter_registrocivilmodel_municipality'), ('lmd', '0019_alter_registrocivilmodel_municipality'), ('lmd', '0020_remove_diocesismodel_municipality_and_more'), ('lmd', '0021_remove_correosmodel_content_and_more'), ('lmd', '0022_remove_correosmodel_birthplace_and_more'), ('lmd', '0023_alter_correosmodel_attachments'), ('lmd', '0024_alter_correosmodel_user'), ('lmd', '0025_alter_registrocivilmodel_municipality')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Nombre')),
                ('file', models.FileField(upload_to='', verbose_name='Archivo')),
            ],
            options={
                'verbose_name': 'Archivo',
                'verbose_name_plural': 'Archivos',
            },
        ),
        migrations.CreateModel(
            name='ProvinceModel',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Provincia',
                'verbose_name_plural': 'Provincias',
            },
        ),
        migrations.CreateModel(
            name='MunicipalityModel',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Nombre')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='municipalities', to='lmd.provincemodel', verbose_name='Provincia')),
                ('official_link', models.URLField(default=None, null=True)),
            ],
            options={
                'verbose_name': 'Municipio',
                'verbose_name_plural': 'Municipios',
            },
        ),
        migrations.CreateModel(
            name='EmailSettingsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imap_host', models.CharField(default=None, verbose_name='Servidor (IMAP)')),
                ('imap_password', models.CharField(default=None, verbose_name='Contraseña (IMAP)')),
                ('imap_port', models.IntegerField(default=None, verbose_name='Puerto TCP (IMAP)')),
                ('imap_username', models.CharField(default=None, verbose_name='Nombre de Usuario (IMAP)')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Configuracion de correo',
                'verbose_name_plural': 'Configuraciones de correos',
            },
        ),
        migrations.CreateModel(
            name='DiocesisModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Nombre')),
                ('phone', models.CharField(verbose_name='Teléfono')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo Eléctronico')),
                ('extra_phone', models.CharField(blank=True, null=True, verbose_name='Teléfono Adicional')),
                ('province', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='lmd.provincemodel', verbose_name='Provincia')),
            ],
            options={
                'verbose_name': 'Diocesis',
                'verbose_name_plural': 'Diocesis',
            },
        ),
        migrations.CreateModel(
            name='CorreosModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachments', models.ManyToManyField(blank=True, help_text='Archivos extras adjuntos', to='lmd.attachmentmodel', verbose_name='Archivos')),
                ('content_type', models.CharField(choices=[('any', 'Todos'), ('diocesis', 'Diocesis'), ('civil', 'Registro Civil')], default='any', verbose_name='Tipo de correo')),
                ('municipality', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lmd.municipalitymodel', verbose_name='Municipio')),
                ('province', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lmd.provincemodel', verbose_name='Provincia')),
                ('birthday', models.DateField(default=None, help_text='Fecha de nacimiento de la persona de la cual se quiere solicitar su certificado', verbose_name='Fecha de nacimiento')),
                ('father_fullname', models.CharField(default=None, help_text='Nombre completo del padre de la persona de la cual se quiere solicitar su certificado', verbose_name='Nombre completo del Padre')),
                ('full_name', models.CharField(default=None, help_text='Nombre completo de la persona de la cual se quiere solicitar su certificado', verbose_name='Nombre completo')),
                ('mother_fullname', models.CharField(default=None, help_text='Nombre completo de la Madre de la persona de la cual se quiere solicitar su certificado', verbose_name='Nombre completo de la Madre')),
                ('purpose', models.CharField(choices=[('lmd', 'Obtención de la ciudadanía española mediante la Ley de Memoria Democrática')], default=None, help_text='Propósito con el cual se solicita el certificado de nacimiento actual', verbose_name='Propósito')),
                ('relationship', models.CharField(default=None, help_text='Relación, por ejemplo, padre, madre, abuelo, abuela, bisabuelo o bisabuela', verbose_name='Relación')),
                ('user', models.ForeignKey(auto_created=True, default=None, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Correo',
                'verbose_name_plural': 'Correos',
            },
        ),
        migrations.CreateModel(
            name='RegistroCivilModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(null=True, verbose_name='Teléfono')),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='Correo Electrónico')),
                ('municipality', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='civil_registry', to='lmd.municipalitymodel', verbose_name='Municipio')),
                ('address', models.CharField(default=None, verbose_name='Dirección')),
                ('fax', models.CharField(default=None, null=True, verbose_name='Fax')),
                ('locality', models.CharField(default=None, verbose_name='Localidad')),
                ('postal_code', models.CharField(default=None, verbose_name='Código Postal')),
            ],
            options={
                'verbose_name': 'Registro Civil',
                'verbose_name_plural': 'Registros Civiles',
            },
        ),
    ]

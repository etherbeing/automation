import logging
from django.conf import settings
from django.test import TestCase
from lmd.tests.factory.main import CorreosFactory
from lmd.data.provinces import PROVINCES
from lmd.models import CorreosModel, DiocesisModel, MunicipalityModel, ProvinceModel, RegistroCivilModel
from lmd.scrappers.main import generate_all_diocesis, generate_municipalities, generate_provinces, generate_rcs, get_all_diocesis, get_all_rc_details, get_municipalities, get_provinces, get_rc_by_province, get_rc_details
from .utils.email import extract_email_info, print_extracted_email_info

# Create your tests here.
class MJusticiaScrapper(TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        # from django.apps.registry import apps
        # from django.db import DEFAULT_DB_ALIAS, connections
        # from django.conf import settings
        # for model in apps.get_models():
        #     try:
        #         print(settings.DATABASES)
        #         # Skip models that shouldn't be migrated (optional)
        #         if not model._meta.managed or model._meta.proxy:
        #             continue
        
        #         # Fetch all data from the default database
        #         rows = model.objects.using("backup").all()
        #         print(rows)
        #         continue
        #          # Clone each object to prepare for saving into the test DB
        #         cloned_rows = []
        #         for row in rows:
        #             # Clone the instance
        #             row.pk = None  # Reset the primary key to allow insertion as new record
        #             cloned_rows.append(row)

        #         # Bulk insert into the test database
        #         if cloned_rows:
        #             model.objects.using(list(self.databases)[0]).bulk_create(cloned_rows)

        #         logging.info(f"Copied {len(cloned_rows)} records for model {model._meta.model_name}")

        #     except Exception as ex:
        #         logging.error(f"Error copying data for model {model._meta.model_name}: {ex}")
        # print(ProvinceModel.objects.all().count())
        # # CorreosFactory.create_batch(3)
        return super().setUp()
    
    def test_framework(self,):
        logging.debug(list(ProvinceModel.objects.all()))
    
    def test_generate_provinces(self,):
        generate_provinces()
        self.assertEqual(ProvinceModel.objects.count(), len(PROVINCES))
        official = ProvinceModel.objects.first()
        if official:
            logging.error(official.official_link)

    def test_generate_municipalities(self,):
        generate_municipalities()
        official = MunicipalityModel.objects.first()
        if official:
            logging.error(official.official_link)
        
    def test_generate_rcs(self,):
        next(generate_rcs())
        official = RegistroCivilModel.objects.first()
        if official:
            logging.error(official.email)
        
    def test_emails_sent(self,):
        print_extracted_email_info(extract_email_info(settings.BASE_DIR/"assets/emails/20241122-184509-2054663092560.log"))

    def test_get_rc_by_province_details(self,):
        val = get_rc_by_province("25")
        for municipe in val:
            print(municipe)

    def test_get_all_rc_details(self,):
        val = get_all_rc_details()
        print(next(val))
        print(next(val))

    def test_get_rc_details(self,):
        rc_details = get_rc_details(MunicipalityModel.objects.get_or_create(pk="27018", defaults={
            "province": ProvinceModel.objects.create()
        })[0])
        logging.debug(rc_details)
    
    def test_send_correo(self,):
        for correo in CorreosModel.objects.all():
            correo.send()

    def test_get_provinces(self,):
        provinces = get_provinces()
        logging.debug(provinces)
        self.assertTrue(len(provinces) > 0)


    def test_get_municipalities(self, ):
        municipalities = get_municipalities("27")
        logging.debug(municipalities)
        self.assertTrue(len(municipalities) > 0)

    def test_get_diocesis(self, ):
        diocesis = get_all_diocesis()
        logging.debug(diocesis)
        self.assertIsNotNone(diocesis)
        self.assertTrue(len(diocesis) > 0) # type: ignore
    def test_generate_diocesis(self, ):
        for diocesis in generate_all_diocesis():
            logging.debug(diocesis)
        d = DiocesisModel.objects.first()
        logging.debug((d, DiocesisModel.objects.count()))
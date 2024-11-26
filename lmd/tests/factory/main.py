from factory import django, faker
from lmd.models import CorreosModel, MunicipalityModel, ProvinceModel

class ProvinceFactory(django.DjangoModelFactory):
    id = faker.Faker("word")
    name = faker.Faker("word")
    class Meta:
        model = ProvinceModel

class MunicipalityFactory(django.DjangoModelFactory):
    id = faker.Faker("word")
    name = faker.Faker("word")
    # province = ProvinceFactory()

    class Meta:
        model = MunicipalityModel


class CorreosFactory(django.DjangoModelFactory):
    subject = faker.Faker("word")
    content = faker.Faker("text")
    # municipality = MunicipalityFactory()
    # province = ProvinceFactory()

    class Meta:
        model = CorreosModel
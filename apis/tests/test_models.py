from django.test import TestCase

from apis.models import Sales, User,Countries,Cities,UserProfile


class TestSalesModel(TestCase):
    def setUp(self):
        sale = Sales.objects.create(product="Tape", revenue=10,sales_number=20,sales_date="2022-07-05")
        self.assertEqual(str(sale), sale.product)

class TestCountriesModel(TestCase):
    def setUp(self):
        country = Countries.objects.create(name="Europe")
        self.assertEqual(str(country), country.name)

class TestCitiesModel(TestCase):
    def setUp(self):
        city = Cities.objects.create(name="Novosibirsk")
        self.assertEqual(str(city), city.name)
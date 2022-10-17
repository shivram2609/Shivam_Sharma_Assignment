import json
from os.path import join

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from django.db.models import Sum,Max
from apis.views import SalesViewSet,StatisticsSalesViewAPI,UsersViewAPI
from apis.models import Sales
 
def sample_payload(id):
    payload = {
        "product": "Tape", 
            "revenue":10,
            "sales_number":20,
            "sales_date":"2022-07-05",
            "user_id":id
    }
    return Sales.objects.create(**payload)

class SigninTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test_user@meistery.net',
            password='trial_application',
            email='test_user@meistery.net')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        request = self.factory.get('api/v1/login/')
        force_authenticate(request, user=self.user)
        self.assertTrue((self.user is not None) and self.user.is_authenticated)

    def test_wrong_username(self):
        request = self.factory.get('api/v1/login/')
        user = force_authenticate(request,user="test")
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_password(self):
        request = self.factory.get('api/v1/login/')
        user = force_authenticate(request,user="test1")
        self.assertFalse(user is not None and user.is_authenticated)

class UsersViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='test_user@meistery.net',
            password='trial_application',
            email='test_user@meistery.net'
        )
    ### Test for GET ###
    def test_user_details(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/api/v1/users/'+str(self.user.id)+'/')
        # Check if you get a 200 back:
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SalesViewSetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='test_user@meistery.net',
            password='trial_application',
            email='test_user@meistery.net'
        )

    ### Test for GET ###
    def test_sale_list(self):
        request = self.factory.get('api/v1/sales/')
        force_authenticate(request, user=self.user)
        response = SalesViewSet.as_view({'get': 'list'})(request)
        # Check if you get a 200 back:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    ### Test for CREATE/POST ###
    def test_sale_create(self):
        payload = {
            "product": "Tape", 
            "revenue":10,
            "sales_number":20,
            "sales_date":"2022-07-05",
            "user":self.user.id
        }
        data = json.dumps(payload)
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post('/api/v1/sales/', data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check to see if Tape was created
        self.assertEqual(response.data['product'], 'Tape')

    def test_get_single_sale(self):
        sale = sample_payload(self.user.id)
        request = self.factory.get('api/v1/sales/')
        force_authenticate(request, user=self.user)
        response = SalesViewSet.as_view({'get': 'retrieve'})(request,pk=str(sale.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_single_sale(self):
        sale = sample_payload(self.user.id)
 
        payload = {
            "product" : "Tape", 
            "revenue" : 10,
            "sales_number" : 20,
            "sales_date" : "2022-07-05",
            "user" : self.user.id
        }
        data = json.dumps(payload)
        request = self.factory.put('api/v1/sales/', data=data, content_type='application/json')
        force_authenticate(request, user=self.user)
        response = SalesViewSet.as_view({'put': 'update'})(request,pk=str(sale.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


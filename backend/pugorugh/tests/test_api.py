from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from pugorugh import models


class UserTests(APITestCase):
    def setUp(self):
        User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

    def test_register_user(self):
        """
        Register a new user
        """
        url = reverse('register-user')
        data = {'username': 'new_user', 'password': 'newpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        """
        Ensure the user can login
        # """
        url = reverse('login-user')
        data = {'username': 'john', 'password': 'johnpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAuth(APITestCase):
    def test_undecided_not_auth(self):
        """
        Ensure unauthorised access is denied.
        """
        url = reverse('get-next', kwargs={'status': 'undecided', 'pk': -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetNextTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringopassword')

        self.user_prefs = models.UserPref.objects.create(
            age='b,y,a,s',
            gender='m,f',
            size='s,m,l,xl',
            user_id=self.user.id)

        self.dog1 = models.Dog.objects.create(
            name='Francesca',
            image_filename='1.jpg',
            breed="Labrador",
            age=72,
            gender='f',
            size='l')

        self.dog2 = models.Dog.objects.create(
            name='Hank',
            image_filename='2.jpg',
            breed="French Bulldog",
            age=14,
            gender='m',
            size='s')

    def test_undecided(self):
        """
        Ensure unauthorised access is denied.
        """

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('get-next', kwargs={'status': 'undecided', 'pk': -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 1,
                'name': 'Francesca',
                'image_filename': '1.jpg',
                'breed': 'Labrador',
                'age': 72,
                'gender': 'f',
                'size': 'l'
            }
        )
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


class UserPrefsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringopassword')
        self.user_2 = User.objects.create_user('george', 'harrison@thebeatles.com', 'georgepassword')
        self.user_prefs = models.UserPref.objects.create(
            age='y,a,s',
            gender='m,f',
            size='s,m,xl',
            microchipped='n',
            user_id=self.user.id)

    def test_get_prefs(self):
        """
        Ensure the User Prefs are returned as correct JSON.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('user-prefs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 1,
                'age': 'y,a,s',
                'gender': 'm,f',
                'size': 's,m,xl',
                'microchipped': 'n',
            }
        )

    def test_change_prefs(self):
        """
        Ensure the User Prefs can be edited and returned as correct JSON.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('user-prefs')
        data = {'age': 's', 'gender': 'm', 'size': 'l', 'microchipped': 'y'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 1,
                'age': 's',
                'gender': 'm',
                'size': 'l',
                'microchipped': 'y',
            }
        )

    def test_new_user_prefs(self):
        """
        Ensure the User Prefs can be set for a new user
        and returned as correct JSON.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user_2)

        url = reverse('user-prefs')
        data = {'age': 's,b,y', 'gender': 'f', 'size': 's,l', 'microchipped': 'e'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)





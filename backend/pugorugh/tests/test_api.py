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

        self.dog_1 = models.Dog.objects.create(
            name='Francesca',
            image_filename='1.jpg',
            breed="Labrador",
            age=72,
            gender='f',
            size='l')

        self.dog_2 = models.Dog.objects.create(
            name='Hank',
            image_filename='2.jpg',
            breed="French Bulldog",
            age=14,
            gender='m',
            size='s')

        self.dog_3 = models.Dog.objects.create(
            name='Muffin',
            image_filename='3.jpg',
            breed="Boxer",
            age=24,
            gender='f',
            size='xl')

        self.dog_4 = models.Dog.objects.create(
            name='Bjorn',
            image_filename='4.jpg',
            breed="Swedish Vallhund",
            age=36,
            gender='m',
            size='m')

        self.disliked_dog = models.UserDog.objects.create(
            user_id=self.user.id,
            dog_id=self.dog_2.id,
            status='d'
        )

        self.undecided_rated_dog = models.UserDog.objects.create(
            user_id=self.user.id,
            dog_id=self.dog_3.id,
            status='u'
        )

        self.liked_dog = models.UserDog.objects.create(
            user_id=self.user.id,
            dog_id=self.dog_4.id,
            status='l'
        )

    def test_undecided_not_rated(self):
        """
        Ensure that when the dog is yet to be rated the
        next undecided Dog is returned as valid JSON.
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

    def test_undecided_rated(self):
        """
        Ensure that when the dog has been rated (as 'u')
        the next undecided Dog is returned as valid JSON.
        """

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('get-next', kwargs={'status': 'undecided', 'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 3,
                'name': 'Muffin',
                'image_filename': '3.jpg',
                'breed': 'Boxer',
                'age': 24,
                'gender': 'f',
                'size': 'xl'
            }
        )

    def test_undecided_loop(self):
        """
        Ensure that when the dog is yet to be rated the
        next undecided Dog is returned as valid JSON.
        """

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('get-next', kwargs={'status': 'undecided', 'pk': 200})
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

    def test_liked(self):
        """
        Test that next liked Dog is returned as valid JSON.
        """

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('get-next', kwargs={'status': 'liked', 'pk': -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 4,
                'name': 'Bjorn',
                'image_filename': '4.jpg',
                'breed': 'Swedish Vallhund',
                'age': 36,
                'gender': 'm',
                'size': 'm'
            }
        )

    def test_disliked(self):
        """
        Test that next liked Dog is returned as valid JSON.
        """

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('get-next', kwargs={'status': 'disliked', 'pk': -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 2,
                'name': 'Hank',
                'image_filename': '2.jpg',
                'breed': 'French Bulldog',
                'age': 14,
                'gender': 'm',
                'size': 's'
            }
        )


class StatusTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringopassword')

        self.dog_1 = models.Dog.objects.create(
            name='Francesca',
            image_filename='1.jpg',
            breed="Labrador",
            age=72,
            gender='f',
            size='l')

        self.dog_2 = models.Dog.objects.create(
            name='Hank',
            image_filename='2.jpg',
            breed="French Bulldog",
            age=14,
            gender='m',
            size='s')

        self.disliked_dog = models.UserDog.objects.create(
            user_id=self.user.id,
            dog_id=self.dog_2.id,
            status='d'
        )

    def test_set_liked(self):
        """
        Ensure that the liked status is set correctly.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('set_status', kwargs={'status': 'liked', 'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 2,
                'user_id': 1,
                'dog_id': 1,
            }
        )

    def test_set_disliked(self):
        """
        Ensure that the disliked status is set correctly.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('set_status', kwargs={'status': 'disliked', 'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 2,
                'user_id': 1,
                'dog_id': 1,
            }
        )

    def test_set_undecided(self):
        """
        Ensure that the disliked status is set correctly.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('set_status', kwargs={'status': 'undecided', 'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 2,
                'user_id': 1,
                'dog_id': 1,
            }
        )

    def test_change_status(self):
        """
        Ensure that a status cane be changed correctly.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('set_status', kwargs={'status': 'liked', 'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 1,
                'user_id': 1,
                'dog_id': 2,
            }
        )

class UserPrefsTests(APITestCase):
    def setUp(self):
        pass

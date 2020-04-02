from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from pugorugh import models


class StatusTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('shaggy', 'norville.rodgers@scooby-doo.com', 'shaggypassword')

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

        url = reverse('set-status', kwargs={'status': 'liked', 'pk': 1})
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

        url = reverse('set-status', kwargs={'status': 'disliked', 'pk': 1})
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

        url = reverse('set-status', kwargs={'status': 'undecided', 'pk': 1})
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

        url = reverse('set-status', kwargs={'status': 'liked', 'pk': 2})
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
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.db.models import Q

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
            size='l',
            microchipped=True)

        self.dog_2 = models.Dog.objects.create(
            name='Hank',
            image_filename='2.jpg',
            breed="French Bulldog",
            age=14,
            gender='m',
            size='s',
            microchipped=True)

        self.disliked_dog = models.UserDog.objects.create(
            user_id=self.user.id,
            dog_id=self.dog_2.id,
            status='d'
        )

    def test_blacklist(self):
        """
        Ensure that the Dog is blacklisted correctly.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('blacklist', kwargs={'blacklist': 'true', 'pk': 2})
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
        entry = models.UserDog.objects.all().get(
            Q(user_id__exact=1) &
            Q(dog_id__exact=2))

        self.assertEqual(entry.status, 'd')
        self.assertEqual(entry.blacklist, True)

    def test_blacklist_new_entry(self):
        """
        Ensure that a new entry is created correctly in UserDog
        when the blacklist api is called if no entry exists.

        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('blacklist', kwargs={'blacklist': 'true', 'pk': 1})
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

        new_entry = models.UserDog.objects.all().get(
            Q(user_id__exact=1) &
            Q(dog_id__exact=1))

        self.assertEqual(new_entry.status, 'u')
        self.assertEqual(new_entry.blacklist, True)

    def test_remove_blacklist(self):
        """
        Ensure that the Dog is de-blacklisted correctly.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('blacklist', kwargs={'blacklist': 'false', 'pk': 2})
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
        entry = models.UserDog.objects.all().get(
            Q(user_id__exact=1) &
            Q(dog_id__exact=2))

        self.assertEqual(entry.status, 'd')
        self.assertEqual(entry.blacklist, False)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from pugorugh import models


class AddDeleteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('david', 'holmes@davidholmes.com', 'mymatepaul')

        self.dog_1 = models.Dog.objects.create(
            name='Snoopy',
            image_filename='snoopy.jpg',
            breed="Beagle",
            age=46,
            gender='m',
            size='s',
            microchipped=True
        )

    def test_add_dog(self):
        """
        Ensure that a dog can be added via the API.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('add-dog')
        data = {
            'name': 'Gnasher',
            'image_filename': 'gnasher.jpg',
            'breed': 'Wire-haired Tripehound',
            'age': 76,
            'gender': 'm',
            'size': 'm',
            'microchipped': False
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'id': 2,
                'name': 'Gnasher',
                'image_filename': 'gnasher.jpg',
                'breed': 'Wire-haired Tripehound',
                'age': 76,
                'gender': 'm',
                'size': 'm',
                'microchipped': False
            }
        )

    def test_delete_dog(self):
        """
        Ensure that a dog can be deleted via the API.
        """
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        url = reverse('delete-dog', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

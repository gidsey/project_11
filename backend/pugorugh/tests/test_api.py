from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from pugorugh import models


class GetNextTests(APITestCase):
    def test_undecided(self):
        """
        Ensure unauthorised access is denied.
        """
        url = reverse('get-next', kwargs={'status': 'undecided', 'pk': -1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


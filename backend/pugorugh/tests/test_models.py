from django.test import TestCase

from pugorugh.models import Dog


class MineralModelTests(TestCase):
    """Test the Mineral model."""
    def setUp(self):
        Dog.objects.create(
            name="Patch",
            image_filename="patch.jpg",
            breed="Border Collie",
            age=42,
            gender='m',
            size='s'
        )

    def test_new_dog(self):
        """Test Dog is set correctly"""
        new_dog = Dog.objects.get(name='Patch')
        self.assertEqual(str(new_dog), '1, Patch (m)')
        self.assertEqual(new_dog.age, 42)
        self.assertEqual(new_dog.size, 's')
        self.assertEqual(new_dog.breed, 'Border Collie')

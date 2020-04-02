import re
from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models

from .utils import clean_input


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = get_user_model()

        fields = (
            'username',
            'password',
        )


# noinspection PyMethodMayBeStatic
class DogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'image_filename',
            'breed',
            'age',
            'gender',
            'size',
            'microchipped'
        )
        model = models.Dog

    # Ensure the the image_filename ends with .jpg, .jpeg or .png
    def validate_image_filename(self, value):
        if re.match(r'^.+\.(jpg|jpeg|png)$', value):
            return value
        raise serializers.ValidationError(
            "image_filename must end with '.jpg', '.jpeg' or '.png'"
        )

    #  Ensure that Age is an integer between 1 and 200
    def validate_age(self, value):
        if value in range(1, 201):
            return value
        raise serializers.ValidationError(
            "Age must be an integer between 1 and 200"
        )

    #  Ensure that Gender is either m, f or u
    def validate_gender(self, value):
        if re.match(r'^[mfu]$', value):
            return value
        raise serializers.ValidationError(
            "Gender must be 'm' for male, 'f' for female or 'u' for unknown"
        )

    #  Ensure that size is either s, m, l or xl
    def validate_size(self, value):
        if re.match(r'^(s|m|l|xl)$', value):
            return value
        raise serializers.ValidationError(
            "Size must be 's' for small, 'm' for medium, 'l' for large or 'xl' for extra large"
        )


class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'age',
            'gender',
            'size',
            'microchipped',
        )
        model = models.UserPref

    #  Ensure that size is a comma-separated string containing only s, m, l or xl
    def validate_size(self, value):
        value, value_list = clean_input(value)
        for element in value_list:
            if not re.match(r'^(s|m|l|xl)$', element):
                raise serializers.ValidationError(
                    "Size must a comma-separated string containing only s, m, l or xl"
                )
        return value

    #  Ensure that gender is a comma-separated string containing only m, f or u
    def validate_gender(self, value):
        value, value_list = clean_input(value)
        for element in value_list:
            if not re.match(r'^(m|f)$', element):
                raise serializers.ValidationError(
                    "Gender must a comma-separated string containing only m or f"
                )
        return value

    #  Ensure that age is a comma-separated string containing only b, y, a or s
    def validate_age(self, value):
        value, value_list = clean_input(value)
        for element in value_list:
            if not re.match(r'^(b|y|a|s)$', element):
                raise serializers.ValidationError(
                    "Age must a comma-separated string containing only b, y, a or s"
                )
        return value

    #  Ensure that microchipped is a comma-separated string containing only y, n, e
    def validate_microchipped(self, value):
        if not re.match(r'^(y|n|e)$', value):
            raise serializers.ValidationError(
                "Microchipped must contain only y, n or e"
            )
        return value


class UserDogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user_id',
            'dog_id',
        )
        model = models.UserDog

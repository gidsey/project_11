import re
from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models


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
        )
        model = models.Dog

    def validate_age(self, value):
        if value in range(1, 201):
            return value
        raise serializers.ValidationError(
            "Age must be an integer between 1 and 200"
        )

    def validate_gender(self, value):
        if re.match(r'[mfu]', value):
            return value
        raise serializers.ValidationError(
            "Gender must be 'm' for male, 'f' for female or 'u' for unknown"
        )

    # def validate_size(self, value):
    #     pass



class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'age',
            'gender',
            'size',
        )
        model = models.UserPref


class UserDogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user_id',
            'dog_id',
        )
        model = models.UserDog

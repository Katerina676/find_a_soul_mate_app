from rest_framework import serializers
from .models import User, Loves


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'gender', 'avatar', 'latitude', 'longitude')


class LovesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loves
        fields = ['id_from', 'id_to']
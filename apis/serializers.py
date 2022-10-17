from rest_framework import serializers
from django.contrib.auth import authenticate,get_user_model
from django.utils.translation import gettext_lazy as _
from apis.models import *

User = get_user_model()

class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = ['id', 'product', 'revenue','sales_date','sales_number','user']

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = ('id','name')

class CountriesSerializer(serializers.ModelSerializer):
    cities = CitiesSerializer(many=True)

    class Meta:
        model = Countries
        fields = ('id','name','cities')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('gender', 'age', 'country', 'city')

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ('id','email','first_name','last_name', 'email','profile')

    def update(self, instance, validated_data):
      userprofile_data = validated_data.pop('profile',None)
      if userprofile_data is not None:

        if userprofile_data.get('gender') is not None:
          instance.profile.gender=userprofile_data['gender']

        if userprofile_data.get('age') is not None:  
          instance.profile.age=userprofile_data['age']

        if userprofile_data.get('country') is not None:
          instance.profile.country=userprofile_data['country']

        if userprofile_data.get('city') is not None:
          instance.profile.city=userprofile_data['city']
        instance.profile.save()
      instance = super().update(instance, validated_data)
      return instance

#Custom Authentication Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


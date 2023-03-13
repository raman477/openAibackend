from .models import *
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField('getToken')

    def getToken(self, obj):
        try:
            user_with_token = Token.objects.get(user=obj)
        except:
            user_with_token = None
        
        if user_with_token is None:
            token1 = Token.objects.create(user=obj)
            token = token1.key
        else:
            Token.objects.get(user=obj).delete()
            token1 = Token.objects.create(user=obj)
            token = token1.key
        return token

    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)
    class Meta:
        model=CustomUser
        fields="__all__"
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserSubscriptionSerializer(serializers.ModelSerializer):
     class Meta:
        model=UserSubscription
        fields="__all__"
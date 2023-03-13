
import openai
import os
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import stripe
from operator import attrgetter
import json
from .models import *
from .serializers import *
from common.common import *
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

stripe.api_key = "sk_test_51HuQVgDRtyZi7NAeDdwVcGQ4TPCW59tyCfzcfXPtXgmrzOThp8qdoRWmR3o2OjMjbL7khSrNU6Ipr1LbKTfwrq4600OBljMDd2"

# Create your views here.

#  user signup API


@api_view(['POST'])
def signup(request):
    # user=CustomUser.objects.create_user(first_name=request.data['first_name'],last_name=request.data['last_name'],email=request.data['email'],password=request.data['password'])
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(getFirstError(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']
    user = authenticate(username=email, password=password)

    if user:
        try:
            token = ''
            try:
                user_with_token = Token.objects.get(user=user)
            except:
                user_with_token = None

            if user_with_token is None:
                token1 = Token.objects.create(user=user)
                token = token1.key
            else:
                Token.objects.get(user=user).delete()
                token1 = Token.objects.create(user=user)
                token = token1.key
        except CustomUser.DoesNotExist:
            raise CustomValidation(
                'Please enter valid credentials.', 'error', status_code=status.HTTP_400_BAD_REQUEST)
    else:
        raise CustomValidation("Please enter valid credentials.",
                               'error', status_code=status.HTTP_400_BAD_REQUEST)
    data = {
        "id": user.id,
        'email': user.email,
        'token': token,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'sub_id': user.sub_id,
        'social_acc': user.social_acc,
    }
    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def social_login(request):
    email = request.data['email']
    sub_id = request.data['sub_id']
    social_acc = request.data.get("social_acc")
    first_name = request.data['first_name']
    last_name = request.data['last_name']
    created = False
    if email == None or email == 'null':
        return Response({"message": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        social_user = CustomUser.objects.get(sub_id=sub_id)
    except:
        created = True
        social_user = None
    if social_user is None:

        try:
            email_user = CustomUser.objects.get(email=email)
            print('emaillll', email_user)
        except:
            email_user = None

        if email_user is None:
            user = CustomUser.objects.create_user(
                email=email, first_name=first_name, last_name=last_name, sub_id=sub_id, social_acc=social_acc)
        else:
            return Response({"message": "User with this email already registered with us."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = ''
        user = CustomUser.objects.get(sub_id=sub_id)
        try:
            user_with_token = Token.objects.get(user=user)
        except:
            user_with_token = None

        if user_with_token is None:
            token1 = Token.objects.create(user=user)
            token = token1.key
        else:
            Token.objects.get(user=user).delete()
            token1 = Token.objects.create(user=user)
            token = token1.key

    except CustomUser.DoesNotExist:
        return Response({"message": 'User with given email and password does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    data = UserSerializer(user).data
    data["token"] = token
    data['created'] = created
    return Response({'data': data}, status=status.HTTP_200_OK)



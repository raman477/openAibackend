
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


@api_view(['POST'])
def textGenerator(request):
    print(api_key)
    if api_key is not None:
        # aj=openai.Model.retrieve("text-davinci-003")
        # print(aj)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=request.data['prompt'],
            max_tokens=1000,
            temperature=0.7,
            top_p=1,
            stop=None,
            frequency_penalty=1.5,
            presence_penalty=1.5

            # echo=True
        )
        print(response)
    return Response({"data": response['choices'][0]['text']})


@api_view(['GET'])
def get_subscription_packs(request,pk=None):
    products_list = stripe.Product.list()
    price_list = stripe.Price.list()
    try:
        final_list = [{"product_id": product.id, "product_name": product.name, "product_default_price": {
            "id": price.id, "amount": price.unit_amount/100}} for price in price_list for product in products_list if price.product == product.id]
        print(type(final_list))
        return Response(final_list)
    except Exception as e:
        print(e)
        return Response(e)


@api_view(['POST'])
def make_payments(req):
    email = req.data['email']
    pack_name = req.data['pack_name']
    pack_price = req.data['pack_price']
    pack_price_id = req.data['price_id']
    try:
        user = CustomUser.objects.get(email=email)
        # create customer on stripe
        stripe_customer = stripe.Customer.create(

            email=email
        )

        # card_token = stripe.Token.create(
        #     card={
        #         "number": "4242424242424242",
        #         "exp_month": 3,
        #         "exp_year": 2024,
        #         "cvc": "314",
        #     },
        # )

        # create payment method
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": "4242424242424242",
                "exp_month": 8,
                "exp_year": 2024,
                "cvc": "314",
            },
        )

        # attach payment method to customer
        attach_payment = stripe.PaymentMethod.attach(
            payment_method.id,
            customer=stripe_customer.id,
        )

        # make attched payment as default of customer
        default_method = stripe.Customer.modify(
            stripe_customer.id,
            invoice_settings={
                "default_payment_method": payment_method.id,
            }
        )

        # stripe_charge=stripe.Charge.create(
        #     amount=2000,
        #     currency="usd",
        #     source=card_token.id,
        #     description="my first payment",
        # )
        # print(stripe_charge)
        # products_list= stripe.Product.list()
        # products_list = stripe.Price.list()
        subscription = stripe.Subscription.create(
            customer=stripe_customer.id,
            
            # default_payment_method=payment_method.id,
            # collection_method="send_invoice",
            # days_until_due=1,
            items=[
                {"price": pack_price_id},
            ],
        )
        # print('hiii',subscription)
        data = {
            "user": user.id,
            "subscription_plan": pack_name,
            "subscription_plan_id": subscription.id,
            "subscription_plan_price": pack_price,
            "subscription_plan_price_id": pack_price_id,
            "subscription_status": subscription.status
        }
        user_subscription = UserSubscriptionSerializer(data=data)
        print(user_subscription)
        if user_subscription.is_valid():
            user_subscription.save()
            print(user_subscription)
        else:
            print(getFirstError(user_subscription.errors))
        return Response(subscription)
    except stripe.error.StripeError as e:
        print(e)
        return Response("fail")


@api_view(["POST"])
def cancel_susbscription(req):
    subs_id = req.data['subs_id']
    try:
        cancel_subs_obj = stripe.Subscription.modify(
            subs_id,
            cancel_at_period_end=True
        )
        return Response(cancel_subs_obj)
    except stripe.error.StripeError as e:
        print(e)
        return Response("fail")

@api_view(['GET'])
def test(request):
    return JsonResponse({"data":"hiii im response for tetsing"})
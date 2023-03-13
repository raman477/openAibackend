from django.urls import path
from abracadabra_app.views import *
urlpatterns = [
    path('signup/',signup),
    path('login/',login),
    path('social-login/',social_login),
    path('text-gen/',textGenerator),
    path('get_packs/',get_subscription_packs),
    path('make_payment/',make_payments),
    path('cancel-subscription/',cancel_susbscription),
    path('test/',test),

]

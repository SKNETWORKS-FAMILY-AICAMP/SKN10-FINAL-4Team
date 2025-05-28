from django.urls import path
from .views import homepage, landingpage

urlpatterns = [
    path('', homepage, name='homepage'),
    # path('landingpage/', landingpage, name='landingpage'),
]
from django.urls import path
from access_amherst_algo import views

urlpatterns = [
    path("", views.home, name='home'),
]
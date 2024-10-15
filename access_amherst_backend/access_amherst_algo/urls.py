from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This will render the home view when you visit the root URL
]

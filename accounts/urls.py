from django.urls import path
from .views import Register

app_name = 'accounts'

urlpatterns = [
    path('register/', Register, name='register')
]

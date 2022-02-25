from django.urls import path
from .views import RegisterUser, ConfirmUser

app_name = 'users'
urlpatterns = [
    path('clients/create', RegisterUser.as_view(), name='user-register'),
    path('clients/create/confirm', ConfirmUser.as_view(), name='user-register-confirm'),


]
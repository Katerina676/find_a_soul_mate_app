from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConfirmEmailToken
from .serializers import UserSerializer


class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'gender'}.issubset(self.request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return Response({'Status': False, 'Errors': {
                    'password': error_array}},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.id)
                    return Response({'Status': True, 'Token for email confirmation': token.key},
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({'Status': False,
                                     'Errors': user_serializer.errors},
                                    status=status.HTTP_403_FORBIDDEN)

        return Response({'Status': False,
                         'Errors': 'All necessary arguments are not specified'},
                        status=status.HTTP_400_BAD_REQUEST)


class ConfirmUser(APIView):

    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            else:
                return Response({'Status': False, 'Errors': 'The token or email is incorrectly specified'})

        return Response({'Status': False, 'Errors': 'All necessary arguments are not specified'})




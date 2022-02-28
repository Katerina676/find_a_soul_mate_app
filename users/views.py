import math
from decimal import Decimal
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import GenericViewSet
from django.db.models import Q
from find_a_soul_mate import settings
from .models import ConfirmEmailToken, User, Loves
from .serializers import UserSerializer, LovesSerializer


class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'gender', 'longitude', 'latitude'
                                        }.issubset(self.request.data):
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


class UsersLove(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        matching = get_object_or_404(User, id=id)
        context = {
            "request": self.request,
            "matching": matching
        }
        serializer = UserSerializer(matching, context=context, many=False)
        return Response(serializer.data)

    def post(self, request, id):
        matching = get_object_or_404(User, id=id)
        context = {
            "request": self.request,
            "matching": matching
        }
        serializer = LovesSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save(id_from=request.user, id_to=matching)
            if Loves.objects.filter(id_from=matching, id_to=request.user):
                user = request.user
                match = matching
                self.send_match(user, match)
                self.send_match(match, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_match(self, id_from, id_to):
        subject = 'У вас появилась пара!'
        message = f'Вы понравились {id_to.first_name}!  Почта участника: {id_to.email}'
        admin_email = settings.EMAIL_HOST_USER
        user_email = [id_from.email]
        return send_mail(subject, message, admin_email, user_email)


class LoginUser(APIView):

    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return Response({'Status': True, 'Token': token.key})

            return Response({'Status': False, 'Errors': 'Failed to authorize'}, status=status.HTTP_403_FORBIDDEN)

        return Response({'Status': False, 'Errors': 'All necessary arguments are not specified'},
                        status=status.HTTP_400_BAD_REQUEST)


class UsersView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.filter(is_staff=False, is_active=True).all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['first_name', 'last_name', 'gender']
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        dist = request.query_params.get('distance')
        if dist:
            if not dist.replace('.', '', 1).isdigit() or len(dist) > 9:
                return Response({"distance": ["Дистанция должна быть действительным числом не более 9 символов."]})
            self.queryset = self.users_nearby(request.query_params.get('distance'), queryset=self.queryset)
        return self.list(request, *args, **kwargs)

    def users_nearby(self, distance, queryset):
        distance = Decimal(distance)
        user = self.request.user
        users = queryset.filter(~Q(longitude=None), ~Q(latitude=None)).values('id', 'latitude', 'longitude')
        users_id = []
        for us in users:
            dist = self.get_distance(user.latitude, user.longitude, us['latitude'], us['longitude'])
            if dist < distance:
                users_id.append(us['id'])
        users2 = User.objects.filter(id__in=users_id)
        return users2

    @staticmethod
    def get_distance(lat1, lon1, lat2, lon2):
        lat1 *= Decimal(math.pi / 180)
        lon1 *= Decimal(math.pi / 180)
        lat2 *= Decimal(math.pi / 180)
        lon2 *= Decimal(math.pi / 180)
        d_lon = lon2 - lon1
        r = 6371.009
        delta = math.atan(
            math.sqrt((math.cos(lat2) * math.sin(d_lon)) ** 2 +
                      (math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)) ** 2) /
            (math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(d_lon))
        )
        d = delta * r
        return round(d, 6)


class UsersDistance(GenericViewSet):
    def get(self, request, *args, **kwargs):
        user1 = User.objects.filter(id=self.kwargs['id1']).first()
        user2 = User.objects.filter(id=self.kwargs['id2']).first()
        if user1 and user2:
            if user1.latitude and user1.longitude and user2.latitude and user2.longitude:
                dist = UsersView.get_distance(user1.latitude, user1.longitude, user2.latitude, user2.longitude)
                return Response({'data': f'Расстояние {dist} км'})
            return Response(f'У пользователя отсутствуют даные')
        return Response(f'Пользователя не существует')

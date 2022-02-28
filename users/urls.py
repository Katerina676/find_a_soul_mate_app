from django.urls import path
from .views import RegisterUser, ConfirmUser, UsersLove, LoginUser, UsersView, UsersDistance

app_name = 'users'
urlpatterns = [
    path('clients/create', RegisterUser.as_view(), name='user-register'),
    path('clients/create/confirm', ConfirmUser.as_view(), name='user-register-confirm'),
    path('clients/login', LoginUser.as_view(), name='user-login'),
    path('clients/<int:id>/match', UsersLove.as_view(), name= 'user-match'),
    path('list/', UsersView.as_view({'get': 'get'})),
    path('clients/distance/<int:id1>/<int:id2>/', UsersDistance.as_view({'get': 'get'}))

]
from django.urls import path
from . import views


app_name = 'login'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('approval/', views.approval_user_list, name='approval_user_list'),
    path('user/approval', views.approval_user, name='approval_user'),
    path('logout/', views.logout, name='logout'),
    path('changepasswd/', views.change_passwd, name='changepasswd'),
    path('userinfo/', views.user_info, name='userinfo'),
]

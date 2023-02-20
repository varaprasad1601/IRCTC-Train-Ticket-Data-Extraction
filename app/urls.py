from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('home',views.home,name='home'),
    path('user_login',views.user_login,name='user_login'),
    path('logout',views.logout,name='logout'),
    path('extract_files',views.extract_files,name='extract_files'),
    path('upload_file',views.upload_file,name='upload_file'),
    path('download',views.download,name='download'),
    # path('check',views.check,name='check'),
    path('register',views.register,name='register'),
    path('register_user',views.register_user,name='register_user'),
    path('check_user',views.check_user,name='check_user'),
    path('register_msg',views.register_msg,name='register_msg'),
    path('requests',views.requests,name='requests'),
    path('user/<str:uid>',views.user,name='user'),
    path('accepted/<str:uid>',views.accepted,name='accepted'),
    path('delete_user/<str:uid>',views.delete_user,name='delete_user'),
    path('forgot_password',views.forgot_password,name='forgot_password'),
    # path('change_password',views.change_password,name='change_password'),
    path('send_otp',views.send_otp,name='send_otp'),
    path('check_otp',views.check_otp,name='check_otp'),
    path('contact',views.contact,name='contact'),
    path('messages',views.messages,name='messages'),
]
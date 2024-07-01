from django.urls import path
from .views import HomePage, Register, Login, logoutuser,chatbot,index,history

urlpatterns = [
    path('', HomePage, name="home-page"), 
    path('login/', Login, name="login-page"),
    path('register/', Register, name="register-page"),
    path('logout/', logoutuser, name="logout"),
    path('chatbot/', chatbot, name="chatbot"),
    path('index/', index, name="index"),
    path('history/', history, name='history'),
]
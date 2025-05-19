from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns=[
    path('signup', views.Sign_Up, name='Sign_up'),
    path('signup2', views.Sign_Up2, name='Sign_Up2'),
    # path('signup3', views.Sign_Up3, name='Sign_Up3'),
    path('Login', views.Login, name='Login'),
    path('Logout',views.Logout,name='Logout'),
    path('login-otp', views.login_otp , name="login_otp"),
    # path('login_token', views.login_token , name="login_token"),
    path('login_token', csrf_exempt(views.login_token), name='login_token'),
    path('forget_password', views.forget_password , name="forget_password"),
    path('reset_password', views.reset_password , name="reset_password"),
    path('update_password', views.update_password , name="update_password"),
    path('verify_otp', views.verify_otp , name="verify_otp"),
    path('delete-account',views.delete_account,name='delete-account')
]
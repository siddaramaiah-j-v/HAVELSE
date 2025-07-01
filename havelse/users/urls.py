from django.urls import path
from . import views
from .views import check_phone

app_name='users'
urlpatterns = [
    path('',views.index,name='index'),
    path('edit/',views.edit,name='edit'),
    path('account/delete/',views.account_deletion,name='delete'),
    path('mail-verification/<str:email>/',views.mail_verification,name='mail_verification'),
    path('verify-email/<str:email>/',views.verify_email,name='verify_email'),
    path('api/mail-otp/<str:email>/',views.resend_verification_otp,name='mail_otp'),
    path('otp-login/<str:email>/',views.verify_login,name='verify_login'),
    path('api/login-otp/<str:email>/',views.resend_login_otp,name='login_otp'),
    path('ajax/check-username/', views.check_username, name='check_username'),
    path('ajax/check-email/', views.check_email, name='check_email'),
    path('ajax/check-phone/',views.check_phone,name='check_phone'),
]
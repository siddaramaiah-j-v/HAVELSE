from django.urls import path
from . import views

app_name='users'
urlpatterns = [
    path('',views.index,name='index'),
    path('edit/',views.edit,name='edit'),
    path('delete/',views.account_deletion,name='delete'),
    path('ajax/check-username/', views.check_username, name='check_username'),
    path('ajax/check-email/', views.check_email, name='check_email'),
]
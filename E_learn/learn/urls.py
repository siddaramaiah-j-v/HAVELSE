from django.urls import path
from . import views

app_name='learn'
urlpatterns = [
    path('',views.home,name='home'),
    path('topics/',views.topics,name='topics'),
    path('article/',views.article,name='article'),
    path('video/',views.video,name='video'),
    path('search/',views.search,name='search'),
    path('chat/',views.chat,name='chat'),
    path('code/',views.code,name='code'),
    path('chat/api/', views.chat_with_gemini, name='chat_with_gemini'),
]
from django.urls import path
from . import views

app_name = 'custom_preflight'

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('article/<int:article_id>/', views.publish_article, name='publish_article'),
]

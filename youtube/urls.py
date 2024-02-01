from django.urls import path

from . import views

urlpatterns = [
    path('youtube/', views.HomeView.as_view(), name='youtube'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.create_request, name='create_request'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('approvals/', views.approval_list, name='approval_list'),
    path('approvals/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('approvals/<int:pk>/reject/', views.reject_request, name='reject_request'),
    path('request-access/', views.public_create_request, name='public_create_request'),
]

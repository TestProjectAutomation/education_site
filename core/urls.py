# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('articles/', views.articles, name='articles'),
    path('grants/', views.grants, name='grants'),
    path('books/', views.books, name='books'),
    path('post/<str:slug>/', views.post_detail, name='post_detail'),
    path('search/', views.search, name='search'),
    
    # صفحات المستخدم
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # لوحة التحكم للمحتوى
    path('create-post/', views.create_post, name='create_post'),
    path('edit-post/<int:id>/', views.edit_post, name='edit_post'),
    
    # لوحة الإدارة
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
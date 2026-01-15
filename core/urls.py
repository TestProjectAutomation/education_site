# core/urls.py

from . import views
from django.urls import path, re_path
from django.contrib.auth import views as auth_views


urlpatterns = [
    # الصفحات الرئيسية
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('articles/', views.articles, name='articles'),
    path('grants/', views.grants, name='grants'),
    path('books/', views.books, name='books'),
    path('post/<str:slug>/', views.post_detail, name='post_detail'),
    
    path('search/', views.search, name='search'),
    path('autocomplete_search/', views.autocomplete_search, name='autocomplete_search'),
    

    
    # المصادقة
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # الملف الشخصي
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # استعادة كلمة المرور
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
            views.password_reset_confirm,
            name='password_reset_confirm'),
    
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # أدمن
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # AJAX
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),


    # لوحة التحكم للمحتوى
    path('create-post/', views.create_post, name='create_post'),
    path('edit-post/<int:id>/', views.edit_post, name='edit_post'),
    path('delete-post/<int:id>/', views.delete_post, name='delete_post'),
    
    # لوحة الإدارة
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),




        # إدارة التعليقات
    path('admin/comments/', views.manage_comments, name='manage_comments'),
    path('admin/comments/approve/<int:comment_id>/', views.approve_comment, name='approve_comment'),
    path('admin/comments/reject/<int:comment_id>/', views.reject_comment, name='reject_comment'),
    path('admin/comments/bulk-approve/', views.bulk_approve_comments, name='bulk_approve_comments'),
    path('admin/comments/bulk-delete/', views.bulk_delete_comments, name='bulk_delete_comments'),
    
    # لوحة تحكم المحتوى
    path('content/dashboard/', views.content_dashboard, name='content_dashboard'),
    path('my-posts/comments/', views.view_comments_on_my_posts, name='my_comments'),
    
    # إدارة الأدمن
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/logs/', views.system_logs, name='system_logs'),
    
    # لوحة تحكم Staff
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/posts/', views.staff_manage_posts, name='staff_manage_posts'),


]

# معالجات الأخطاء
handler404 = views.handler404
handler500 = views.handler500
handler403 = views.handler403
handler400 = views.handler400

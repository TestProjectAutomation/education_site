from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__is_content_editor')
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'مستخدم'
    get_role.short_description = 'الدور'

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'publish_date', 'views')
    list_filter = ('status', 'category', 'publish_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish_date'
    ordering = ('-publish_date',)
    raw_id_fields = ('author',)
    filter_horizontal = ()
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'slug', 'category', 'author', 'content', 'image')
        }),
        ('إعدادات الرابط', {
            'fields': ('link', 'link_delay')
        }),
        ('الإحصائيات', {
            'fields': ('views',)
        }),
        ('النشر', {
            'fields': ('status', 'publish_date')
        }),
    )

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'الموافقة على التعليقات المحددة'
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = 'رفض التعليقات المحددة'

# تسجيل النماذج
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(SiteSettings)
admin.site.register(UserProfile)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    CATEGORY_TYPES = [
        ('courses', 'الكورسات'),
        ('articles', 'المقالات'),
        ('grants', 'المنح والتدريبات'),
        ('books', 'الكتب والملخصات'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'القسم'
        verbose_name_plural = 'الأقسام'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique_for_date='publish_date')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True)
    link = models.URLField(blank=True, help_text='رابط خارجي للمنشور')
    link_delay = models.IntegerField(default=30, help_text='مدة الانتظار قبل ظهور الرابط (بالثواني)')
    views = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'
        ordering = ['-publish_date']
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        self.views += 1
        self.save()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'تعليق بواسطة {self.name} على {self.post.title}'

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='موقع التعليم')
    site_description = models.TextField(default='موقع تعليمي متكامل')
    default_link_delay = models.IntegerField(default=30)
    allow_comments = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'إعدادات الموقع'
        verbose_name_plural = 'إعدادات الموقع'
    
    def __str__(self):
        return 'إعدادات الموقع'
    
    def save(self, *args, **kwargs):
        # تأكد من وجود سجل واحد فقط
        self.id = 1
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, blank=True, default='مستخدم')
    is_content_editor = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'
    
    def __str__(self):
        return self.user.username
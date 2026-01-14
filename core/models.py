from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from ckeditor.fields import RichTextField
from PIL import Image
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

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

    def get_absolute_url(self):
        # رابط البحث مع فلتر حسب نوع القسم
        return f"{reverse('search')}?category={self.category_type}"

class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        PUBLISHED = 'published', 'منشور'
        PRIVATE = 'private', 'خاص'
        ARCHIVED = 'archived', 'مؤرشف'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')

    # القديم
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='posts/featured/%Y/%m/%d/', blank=True)

    # الجديد
    featured_image = models.ImageField(upload_to='posts/featured/%Y/%m/', blank=True)
    thumbnail = models.ImageField(upload_to='posts/thumbnails/%Y/%m/', blank=True)

    excerpt = models.TextField(max_length=300, blank=True)

    link = models.URLField(blank=True, null=True)
    link_delay = models.IntegerField(default=30, blank=True, null=True)

    views = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)

    publish_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(max_length=300, blank=True)
    seo_keywords = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title

    # slug ذكي بدون كسر القديم
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or "post"
            slug = base
            i = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

        # نشر تلقائي
        if self.status == self.Status.PUBLISHED and not self.publish_date:
            self.publish_date = timezone.now()

        super().save(*args, **kwargs)

        # إنشاء thumbnail تلقائي
        if self.featured_image and not self.thumbnail:
            self.create_thumbnail()

    def create_thumbnail(self):
        if not self.featured_image:
            return

        image = Image.open(self.featured_image.path)
        image.thumbnail((400, 300), Image.Resampling.LANCZOS)

        thumb_path = self.featured_image.path.replace("featured", "thumbnails")
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        image.save(thumb_path)

        self.thumbnail.name = thumb_path.split("media/")[-1]
        super().save(update_fields=["thumbnail"])

    # روابط وعدادات
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(views=models.F("views") + 1)

    # عرض ذكي
    @property
    def display_title(self):
        return self.seo_title or self.title

    @property
    def display_description(self):
        return self.seo_description or self.excerpt or self.content[:160]


class PostBlock(models.Model):
    class BlockType(models.TextChoices):
        TEXT = 'text', _('نص')
        IMAGE = 'image', _('صورة')

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='blocks',
        verbose_name=_("المقال")
    )

    block_type = models.CharField(
        max_length=10,
        choices=BlockType.choices,
        verbose_name=_("نوع البلوك")
    )

    text = RichTextField(blank=True, null=True, verbose_name=_("النص"))
    image = models.ImageField(upload_to='blog/blocks/%Y/%m/', blank=True, null=True, verbose_name=_("الصورة"))

    order = models.PositiveIntegerField(default=0, verbose_name=_("الترتيب"))

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.post.title} - {self.block_type} ({self.order})"

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
    """إعدادات الموقع"""
    site_name = models.CharField(max_length=200, default='موقع التعليم')
    site_description = models.TextField(blank=True, null=True)
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # إعدادات المحتوى
    default_link_delay = models.IntegerField(default=30, help_text='التأخير الافتراضي بالثواني')
    allow_comments = models.BooleanField(default=True)
    require_comment_approval = models.BooleanField(default=True)
    
    # إعدادات النظام
    maintenance_mode = models.BooleanField(default=False)
    contact_email = models.EmailField(default='contact@example.com')
    
    # وسائل التواصل الاجتماعي
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.site_name
    
    class Meta:
        verbose_name = 'إعدادات الموقع'
        verbose_name_plural = 'إعدادات الموقع'

class SystemLog(models.Model):
    """سجلات النظام"""
    LOG_TYPES = (
        ('info', 'معلومات'),
        ('warning', 'تحذير'),
        ('error', 'خطأ'),
        ('security', 'أمني'),
    )
    
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='info')
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_log_type_display()} - {self.message[:50]}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل النظام'
        verbose_name_plural = 'سجلات النظام'

# تحديث نموذج UserProfile الموجود
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # الصلاحيات
    is_content_editor = models.BooleanField(default=False, verbose_name='محرر محتوى')
    can_manage_comments = models.BooleanField(default=False, verbose_name='يمكنه إدارة التعليقات')
    can_manage_categories = models.BooleanField(default=False, verbose_name='يمكنه إدارة الأقسام')

    # الإحصائيات
    posts_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

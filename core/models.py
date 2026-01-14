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

    link = models.URLField(blank=True)
    link_delay = models.IntegerField(default=30)

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

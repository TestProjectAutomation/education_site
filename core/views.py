from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db import transaction
from .models import *
from .forms import *
import json
from datetime import datetime
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from .models import UserProfile, UserProfile
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from .models import Post, Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.utils.html import strip_tags
from django.db.models.query_utils import Q
from django.http import HttpResponse
import json
from .forms import *
from .models import UserProfile




# دالة للتحقق من أن المستخدم هو محرر محتوى
def is_content_editor(user):
    return user.is_authenticated and (
        user.is_staff or 
        (hasattr(user, 'profile') and user.profile.is_content_editor)
    )

def home(request):
    # الحصول على آخر المنشورات من كل قسم
    courses_posts = Post.objects.filter(
        category__category_type='courses', 
        status='published'
    ).order_by('-publish_date')[:6]
    
    articles_posts = Post.objects.filter(
        category__category_type='articles', 
        status='published'
    ).order_by('-publish_date')[:6]
    
    grants_posts = Post.objects.filter(
        category__category_type='grants', 
        status='published'
    ).order_by('-publish_date')[:6]
    
    books_posts = Post.objects.filter(
        category__category_type='books', 
        status='published'
    ).order_by('-publish_date')[:6]

    url_media = SiteSettings.objects.first()

    context = {
        'courses_posts': courses_posts,
        'articles_posts': articles_posts,
        'grants_posts': grants_posts,
        'books_posts': books_posts,
        'url_media': url_media,
    }
    
    return render(request, 'home.html', context)

def courses(request):
    category = get_object_or_404(Category, category_type='courses')
    posts_list = Post.objects.filter(
        category__category_type='courses',
        status='published'
    ).order_by('-publish_date')
    
    paginator = Paginator(posts_list, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'title': 'الكورسات'
    }
    
    return render(request, 'courses.html', context)

def articles(request):
    category = get_object_or_404(Category, category_type='articles')
    posts_list = Post.objects.filter(
        category__category_type='articles',
        status='published'
    ).order_by('-publish_date')
    
    paginator = Paginator(posts_list, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'title': 'المقالات'
    }
    
    return render(request, 'articles.html', context)

def grants(request):
    category = get_object_or_404(Category, category_type='grants')
    posts_list = Post.objects.filter(
        category__category_type='grants',
        status='published'
    ).order_by('-publish_date')
    
    paginator = Paginator(posts_list, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'title': 'المنح والتدريبات'
    }
    
    return render(request, 'grants.html', context)

def books(request):
    category = get_object_or_404(Category, category_type='books')
    posts_list = Post.objects.filter(
        category__category_type='books',
        status='published'
    ).order_by('-publish_date')
    
    paginator = Paginator(posts_list, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'title': 'الكتب والملخصات'
    }
    
    return render(request, 'books.html', context)


# posrt ------------------------

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # زيادة عدد المشاهدات
    post.increment_views()
    
    # الحصول على التعليقات المعتمدة فقط
    comments = post.comments.filter(is_approved=True)
    
    # الحصول على البلوكات الخاصة بالمنشور
    post_blocks = post.blocks.all().order_by('order')
    
    # معالجة نموذج التعليق
    if request.method == 'POST' and 'comment_form' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            
            # إذا كان المستخدم مسجل دخول، استخدام معلوماته
            if request.user.is_authenticated:
                comment.name = f"{request.user.first_name} {request.user.last_name}".strip()
                if not comment.name:
                    comment.name = request.user.username
                comment.email = request.user.email
            
            comment.save()
            messages.success(request, 'تم إرسال تعليقك بنجاح، سيظهر بعد المراجعة.')
            return redirect('post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    # الحصول على المنشورات المشابهة
    similar_posts = Post.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id).order_by('-publish_date')[:4]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
        'post_blocks': post_blocks,
    }
    
    return render(request, 'post_detail.html', context)


@user_passes_test(is_content_editor)
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    post = form.save(commit=False)
                    post.author = request.user
                    
                    # معالجة حالة النشر
                    if 'save_draft' in request.POST:
                        post.status = Post.Status.DRAFT
                    elif 'publish_now' in request.POST:
                        post.status = Post.Status.PUBLISHED
                        if not post.publish_date:
                            post.publish_date = timezone.now()
                    
                    # حفظ المنشور
                    post.save()
                    
                    # معالجة البلوكات إذا كانت موجودة في النموذج
                    if 'blocks_data' in request.POST:
                        try:
                            blocks_data = json.loads(request.POST.get('blocks_data'))
                            self.create_post_blocks(post, blocks_data, request.FILES)
                        except json.JSONDecodeError:
                            pass
                    
                    messages.success(request, f'تم { "نشر" if post.status == Post.Status.PUBLISHED else "حفظ" } المنشور "{post.title}" بنجاح!')
                    
                    # إعادة التوجيه حسب الحالة
                    if post.status == Post.Status.PUBLISHED:
                        return redirect('post_detail', slug=post.slug)
                    else:
                        return redirect('edit_post', id=post.id)
                        
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء حفظ المنشور: {str(e)}')
                return render(request, 'create_post.html', {'form': form})
    else:
        # تهيئة الحقول الافتراضية
        initial_data = {
            'link_delay': 30,
            'status': Post.Status.DRAFT,
        }
        
        # الحصول على إعدادات الموقع لاستخدام التأخير الافتراضي
        try:
            site_settings = SiteSettings.objects.get(id=1)
            initial_data['link_delay'] = site_settings.default_link_delay
        except SiteSettings.DoesNotExist:
            pass
            
        form = PostForm(initial=initial_data)
    
    # جلب الفئات حسب النوع لعرضها في الواجهة
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'create_post.html', {
        'form': form,
        'categories': categories,
        'post_statuses': Post.Status.choices
    })

def create_post_blocks(self, post, blocks_data, files):
    """إنشاء البلوكات الخاصة بالمنشور"""
    for i, block_data in enumerate(blocks_data):
        block_type = block_data.get('type')
        text = block_data.get('text', '')
        image_file_name = block_data.get('image', '')
        
        post_block = PostBlock(
            post=post,
            block_type=block_type,
            order=i
        )
        
        if block_type == PostBlock.BlockType.TEXT:
            post_block.text = text
        elif block_type == PostBlock.BlockType.IMAGE and image_file_name:
            # البحث عن الملف في request.FILES
            for file_key in files:
                if files[file_key].name == image_file_name:
                    post_block.image = files[file_key]
                    break
        
        post_block.save()

@user_passes_test(is_content_editor)
@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)
    
    # التحقق من صلاحية المستخدم
    if not (request.user.is_staff or post.author == request.user or 
            (hasattr(request.user, 'profile') and request.user.profile.is_content_editor)):
        return HttpResponseForbidden("ليس لديك صلاحية لتعديل هذا المنشور")
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                with transaction.atomic():
                    post = form.save(commit=False)
                    
                    # معالجة حالة النشر
                    if 'save_draft' in request.POST:
                        post.status = Post.Status.DRAFT
                    elif 'publish_now' in request.POST:
                        post.status = Post.Status.PUBLISHED
                        if not post.publish_date:
                            post.publish_date = timezone.now()
                    
                    # حفظ التغييرات
                    post.save()
                    
                    # معالجة البلوكات
                    if 'blocks_data' in request.POST:
                        try:
                            # حذف البلوكات القديمة
                            post.blocks.all().delete()
                            
                            # إنشاء البلوكات الجديدة
                            blocks_data = json.loads(request.POST.get('blocks_data'))
                            self.create_post_blocks(post, blocks_data, request.FILES)
                        except json.JSONDecodeError:
                            pass
                    
                    messages.success(request, f'تم تحديث المنشور "{post.title}" بنجاح!')
                    
                    # إعادة التوجيه حسب الحالة
                    if post.status == Post.Status.PUBLISHED:
                        return redirect('post_detail', slug=post.slug)
                    else:
                        return redirect('edit_post', id=post.id)
                        
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء تحديث المنشور: {str(e)}')
                return render(request, 'edit_post.html', {'form': form, 'post': post})
    else:
        form = PostForm(instance=post)
    
    # جلب البلوكات الحالية للمنشور
    post_blocks = post.blocks.all().order_by('order')
    
    return render(request, 'edit_post.html', {
        'form': form,
        'post': post,
        'post_blocks': post_blocks,
        'post_statuses': Post.Status.choices
    })


def search(request):
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'relevance')
    
    if query:
        # بناء استعلام البحث
        search_queries = Q(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(seo_title__icontains=query) |
            Q(seo_description__icontains=query) |
            Q(category__name__icontains=query)
        ) & Q(status='published')
        
        # تطبيق فلتر الفئة إذا موجود
        if category_filter:
            search_queries &= Q(category__category_type=category_filter)
        
        # الحصول على النتائج
        results = Post.objects.filter(search_queries).distinct()
        
        # تطبيق الترتيب
        if sort_by == 'date':
            results = results.order_by('-publish_date')
        elif sort_by == 'title':
            results = results.order_by('title')
        elif sort_by == 'popularity':
            results = results.order_by('-views')
        else:  # relevance (default)
            results = results.order_by('-publish_date')
        
        # إحصائيات البحث
        search_stats = {
            'total': results.count(),
            'courses': results.filter(category__category_type='courses').count(),
            'articles': results.filter(category__category_type='articles').count(),
            'grants': results.filter(category__category_type='grants').count(),
            'books': results.filter(category__category_type='books').count(),
        }
        
    else:
        results = Post.objects.none()
        search_stats = {
            'total': 0,
            'courses': 0,
            'articles': 0,
            'grants': 0,
            'books': 0,
        }
    
    # الترقيم
    paginator = Paginator(results, 12)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # الفئات المتاحة للفلترة
    available_categories = Category.objects.filter(
        category_type__in=['courses', 'articles', 'grants', 'books']
    ).order_by('category_type').distinct()
    
    context = {
        'query': query,
        'results': page_obj,
        'search_stats': search_stats,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'available_categories': available_categories,
        'suggestions': get_search_suggestions(query) if query else [],
        'paginator': paginator,
        'popular_terms': ['Python', 'تعلم الآلة', 'منح دراسية', 'برمجة', 'تعليم مجاني', 'كورسات أونلاين'],

    }
    
    return render(request, 'search/search_results.html', context)

def get_search_suggestions(query):
    """
    الحصول على اقتراحات البحث المشابهة
    """
    if len(query) < 2:
        return []
    
    suggestions = Post.objects.filter(
        Q(title__icontains=query[:3])
    ).values_list('title', flat=True).distinct()[:5]
    
    return list(suggestions)


def autocomplete_search(request):
    term = request.GET.get('term', '').strip()
    results = []

    if term:
        posts = Post.objects.filter(
            Q(title__icontains=term) | Q(content__icontains=term),
            status='published'
        )[:10]

        for post in posts:
            results.append({
                'title': post.title,
                'url': post.get_absolute_url(),
            })

        categories = Category.objects.filter(name__icontains=term)[:5]
        for cat in categories:
            results.append({
                'title': cat.name,
                'url': cat.get_absolute_url(),
            })

    return JsonResponse(results, safe=False)


# API لمعالجة البلوكات
@login_required
@user_passes_test(is_content_editor)
def api_upload_block_image(request):
    """رفع صورة للبلوك"""
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # حفظ الصورة مؤقتاً
        # في الواقع، يجب حفظها في مكان مؤقت أو معالجتها مباشرة
        
        return JsonResponse({
            'success': True,
            'filename': image_file.name,
            'message': 'تم رفع الصورة بنجاح'
        })
    
    return JsonResponse({'success': False, 'error': 'لم يتم رفع صورة'})

# دالة مساعدة لجلب المنشورات حسب الفئة
def get_category_posts(request, category_type):
    category = get_object_or_404(Category, category_type=category_type)
    posts_list = Post.objects.filter(
        category__category_type=category_type,
        status='published'
    ).order_by('-publish_date')
    
    paginator = Paginator(posts_list, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # إحصائيات إضافية لكل صفحة
    if category_type == 'courses':
        title = 'الكورسات'
    elif category_type == 'articles':
        title = 'المقالات'
    elif category_type == 'grants':
        title = 'المنح والتدريبات'
    elif category_type == 'books':
        title = 'الكتب والملخصات'
    
    context = {
        'category': category,
        'posts': posts,
        'title': title
    }
    
    return context

@login_required
@user_passes_test(is_content_editor)
def my_posts(request):


    """صفحة عرض منشورات المستخدم"""
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # الترقيم
    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'title': 'منشوراتي'
    }
    
    return render(request, 'my_posts.html', context)

@user_passes_test(is_content_editor)
@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    post.delete()
    messages.success(request, 'تم حذف المنشور بنجاح!')

    return redirect('dashboard')




# ============ VIEWS إدارة التعليقات ============

@staff_member_required
def manage_comments(request):
    """
    صفحة إدارة جميع التعليقات
    """
    comments = Comment.objects.all().select_related('post', 'user').order_by('-created_at')
    
    # الترقيم
    paginator = Paginator(comments, 20)
    page = request.GET.get('page', 1)
    
    try:
        comments_page = paginator.page(page)
    except PageNotAnInteger:
        comments_page = paginator.page(1)
    except EmptyPage:
        comments_page = paginator.page(paginator.num_pages)
    
    context = {
        'comments': comments_page,
        'title': 'إدارة التعليقات',
        'total_comments': comments.count(),
        'approved_comments': Comment.objects.filter(is_approved=True).count(),
        'pending_comments': Comment.objects.filter(is_approved=False).count(),
    }
    return render(request, 'admin/manage_comments.html', context)

@staff_member_required
def approve_comment(request, comment_id):
    """
    قبول تعليق معين
    """
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        comment.is_approved = True
        comment.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'تم قبول التعليق بنجاح'})
        
        messages.success(request, 'تم قبول التعليق بنجاح')
        return redirect('manage_comments')
    
    return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

@staff_member_required
def reject_comment(request, comment_id):
    """
    رفض وحذف تعليق
    """
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        
        # تخزين المعلومات قبل الحذف للإشعارات
        comment_email = comment.email
        comment_name = comment.name
        
        comment.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'تم رفض التعليق بنجاح'})
        
        messages.success(request, 'تم رفض التعليق بنجاح')
        return redirect('manage_comments')
    
    return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صحيحة'})

@staff_member_required
def bulk_approve_comments(request):
    """
    قبول مجموعة من التعليقات دفعة واحدة
    """
    if request.method == 'POST':
        comment_ids = request.POST.getlist('comment_ids')
        
        if comment_ids:
            Comment.objects.filter(id__in=comment_ids).update(is_approved=True)
            messages.success(request, f'تم قبول {len(comment_ids)} تعليق')
        else:
            messages.warning(request, 'لم يتم تحديد أي تعليق')
        
        return redirect('manage_comments')
    
    return redirect('manage_comments')

@staff_member_required
def bulk_delete_comments(request):
    """
    حذف مجموعة من التعليقات دفعة واحدة
    """
    if request.method == 'POST':
        comment_ids = request.POST.getlist('comment_ids')
        
        if comment_ids:
            deleted_count, _ = Comment.objects.filter(id__in=comment_ids).delete()
            messages.success(request, f'تم حذف {deleted_count} تعليق')
        else:
            messages.warning(request, 'لم يتم تحديد أي تعليق')
        
        return redirect('manage_comments')
    
    return redirect('manage_comments')

# ============ VIEWS إدارة المحتوى (للstaff و المحررين) ============

@login_required
def content_dashboard(request):
    """
    لوحة تحكم المحتوى (للstaff والمحررين)
    """
    user = request.user
    is_staff_or_editor = user.is_staff or (hasattr(user, 'profile') and user.profile.is_content_editor)
    
    if not is_staff_or_editor:
        return redirect('dashboard')
    
    # إحصائيات حسب صلاحيات المستخدم
    if user.is_superuser or user.is_staff:
        # الأدمن يمكنه رؤية كل شيء
        total_posts = Post.objects.count()
        published_posts = Post.objects.filter(status='published').count()
        draft_posts = Post.objects.filter(status='draft').count()
        
        # المنشورات الأخيرة
        recent_posts = Post.objects.all().order_by('-created_at')[:5]
        
        # التعليقات الجديدة
        new_comments = Comment.objects.filter(is_approved=False).count()
        
    else:
        # المحرر العادي يرى فقط منشوراته
        total_posts = Post.objects.filter(author=user).count()
        published_posts = Post.objects.filter(author=user, status='published').count()
        draft_posts = Post.objects.filter(author=user, status='draft').count()
        
        # المنشورات الأخيرة الخاصة به
        recent_posts = Post.objects.filter(author=user).order_by('-created_at')[:5]
        
        # التعليقات الجديدة على منشوراته
        new_comments = Comment.objects.filter(
            post__author=user,
            is_approved=False
        ).count()
    
    # إحصائيات المشاهدات
    if user.is_superuser or user.is_staff:
        total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
        posts_by_type = {
            'courses': Post.objects.filter(category__category_type='courses').count(),
            'articles': Post.objects.filter(category__category_type='articles').count(),
            'grants': Post.objects.filter(category__category_type='grants').count(),
            'books': Post.objects.filter(category__category_type='books').count(),
        }
    else:
        total_views = Post.objects.filter(author=user).aggregate(total_views=Sum('views'))['total_views'] or 0
        posts_by_type = {
            'courses': Post.objects.filter(author=user, category__category_type='courses').count(),
            'articles': Post.objects.filter(author=user, category__category_type='articles').count(),
            'grants': Post.objects.filter(author=user, category__category_type='grants').count(),
            'books': Post.objects.filter(author=user, category__category_type='books').count(),
        }
    
    context = {
        'title': 'لوحة تحكم المحتوى',
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': recent_posts,
        'new_comments': new_comments,
        'total_views': total_views,
        'posts_by_type': posts_by_type,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    
    return render(request, 'content_dashboard.html', context)

@login_required
def edit_my_post(request, post_id):
    """
    تعديل منشور (للمحرر أو الأدمن)
    """
    post = get_object_or_404(Post, id=post_id)
    
    # التحقق من الصلاحيات
    user = request.user
    if not (user.is_staff or post.author == user or 
            (hasattr(user, 'profile') and user.profile.is_content_editor)):
        messages.error(request, 'ليس لديك صلاحية لتعديل هذا المنشور')
        return redirect('my_posts')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                with transaction.atomic():
                    post = form.save()
                    
                    # معالجة حالة النشر
                    if 'save_draft' in request.POST:
                        post.status = Post.Status.DRAFT
                    elif 'publish_now' in request.POST:
                        post.status = Post.Status.PUBLISHED
                        if not post.publish_date:
                            post.publish_date = timezone.now()
                    
                    post.save()
                    
                    messages.success(request, f'تم تحديث المنشور "{post.title}" بنجاح!')
                    
                    if post.status == Post.Status.PUBLISHED:
                        return redirect('post_detail', slug=post.slug)
                    else:
                        return redirect('edit_my_post', post_id=post.id)
                        
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء تحديث المنشور: {str(e)}')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'title': f'تعديل: {post.title}'
    }
    
    return render(request, 'edit_post.html', context)

@login_required
def view_comments_on_my_posts(request):
    """
    عرض التعليقات على منشورات المستخدم
    """
    user = request.user
    
    if user.is_staff or (hasattr(user, 'profile') and user.profile.is_content_editor):
        if user.is_superuser:
            # الأدمن يمكنه رؤية جميع التعليقات
            comments = Comment.objects.all().select_related('post')
        elif user.is_staff:
            # الـstaff يرى التعليقات على منشوراته ومنشورات المحررين الآخرين
            comments = Comment.objects.filter(
                Q(post__author=user) | Q(is_approved=False)
            ).select_related('post')
        else:
            # المحرر العادي يرى فقط التعليقات على منشوراته
            comments = Comment.objects.filter(post__author=user).select_related('post')
    else:
        messages.error(request, 'ليس لديك صلاحية لعرض التعليقات')
        return redirect('dashboard')
    
    # الترقيم
    paginator = Paginator(comments.order_by('-created_at'), 20)
    page = request.GET.get('page', 1)
    
    try:
        comments_page = paginator.page(page)
    except PageNotAnInteger:
        comments_page = paginator.page(1)
    except EmptyPage:
        comments_page = paginator.page(paginator.num_pages)
    
    context = {
        'comments': comments_page,
        'title': 'التعليقات على منشوراتي',
        'total_comments': comments.count(),
        'approved_comments': comments.filter(is_approved=True).count(),
        'pending_comments': comments.filter(is_approved=False).count(),
    }
    
    return render(request, 'my_comments.html', context)

# ============ VIEWS الأدمن الخاصة بالموقع ============

@user_passes_test(lambda u: u.is_superuser)
def admin_settings(request):
    """
    إعدادات الأدمن المتقدمة
    """
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = SiteSettings.objects.create()
    
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=site_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('admin_settings')
    else:
        form = SiteSettingsForm(instance=site_settings)
    
    context = {
        'form': form,
        'title': 'إعدادات الموقع المتقدمة',
        'site_settings': site_settings,
    }
    
    return render(request, 'admin/admin_settings.html', context)

@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    """
    إدارة المستخدمين
    """
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    # الترقيم
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    context = {
        'users': users_page,
        'title': 'إدارة المستخدمين',
        'total_users': users.count(),
        'staff_users': users.filter(is_staff=True).count(),
        'superusers': users.filter(is_superuser=True).count(),
        'content_editors': UserProfile.objects.filter(is_content_editor=True).count(),
    }
    
    return render(request, 'admin/manage_users.html', context)

@user_passes_test(lambda u: u.is_superuser)
def edit_user_role(request, user_id):
    """
    تعديل دور المستخدم
    """
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            
            # تحديث صلاحيات Django الأساسية
            user.is_staff = profile.is_content_editor
            user.save()
            
            messages.success(request, f'تم تحديث صلاحيات المستخدم {user.username}')
            return redirect('manage_users')
    else:
        form = UserRoleForm(instance=profile)
    
    context = {
        'form': form,
        'user': user,
        'title': f'تعديل صلاحيات المستخدم: {user.username}'
    }
    
    return render(request, 'admin/edit_user_role.html', context)

@user_passes_test(lambda u: u.is_superuser)
def system_logs(request):
    """
    عرض سجلات النظام
    """
    logs = SystemLog.objects.all().order_by('-created_at')[:100]
    
    context = {
        'logs': logs,
        'title': 'سجلات النظام',
        'log_count': logs.count(),
        'error_count': logs.filter(log_type='error').count(),
        'warning_count': logs.filter(log_type='warning').count(),
        'info_count': logs.filter(log_type='info').count(),
    }
    
    return render(request, 'admin/system_logs.html', context)

# ============ VIEWS للـ Staff فقط (ليست للأدمن) ============

@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    """
    لوحة تحكم الـ Staff (ليسوا أدمن)
    """
    user = request.user
    
    # إحصائيات للـ Staff
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    draft_posts = Post.objects.filter(status='draft').count()
    
    # المنشورات الأخيرة (الـ Staff يرى الجميع)
    recent_posts = Post.objects.all().order_by('-created_at')[:5]
    
    # التعليقات الجديدة (الـ Staff يرى الجميع)
    new_comments = Comment.objects.filter(is_approved=False).count()
    
    # إحصائيات المشاهدات
    total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
    
    context = {
        'title': 'لوحة تحكم Staff',
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': recent_posts,
        'new_comments': new_comments,
        'total_views': total_views,
        'user': user,
    }
    
    return render(request, 'staff/dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def staff_manage_posts(request):
    """
    إدارة المنشورات للـ Staff
    """
    posts = Post.objects.all().select_related('author', 'category').order_by('-created_at')
    
    # الترقيم
    paginator = Paginator(posts, 20)
    page = request.GET.get('page', 1)
    
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts_page,
        'title': 'إدارة المنشورات',
        'total_posts': posts.count(),
        'published_posts': posts.filter(status='published').count(),
        'draft_posts': posts.filter(status='draft').count(),
    }
    
    return render(request, 'staff/manage_posts.html', context)

# ============ تحديث admin_dashboard لعرض محتوى مختلف حسب الصلاحيات ============


# admin and superuser views ------------

# @staff_member_required
# def admin_dashboard(request):
#     # إحصائيات عامة
#     total_posts = Post.objects.count()
#     total_comments = Comment.objects.count()
#     total_users = User.objects.count()
#     total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
    
#     # المنشورات الأخيرة
#     recent_posts = Post.objects.all().select_related('category', 'author').order_by('-created_at')[:10]
    
#     # التعليقات الجديدة
#     new_comments = Comment.objects.filter(is_approved=False).select_related('post').order_by('-created_at')[:10]
    
#     # إحصائيات إضافية
#     published_posts = Post.objects.filter(status='published').count()
#     draft_posts = Post.objects.filter(status='draft').count()
#     private_posts = Post.objects.filter(status='private').count()
#     archived_posts = Post.objects.filter(status='archived').count()
    
#     published_percentage = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
#     approved_comments = Comment.objects.filter(is_approved=True).count()
#     pending_comments = Comment.objects.filter(is_approved=False).count()
#     approved_comments_percentage = (approved_comments / total_comments * 100) if total_comments > 0 else 0
    
#     # إحصائيات المستخدمين
#     active_editors = UserProfile.objects.filter(is_content_editor=True).count()
#     staff_users = User.objects.filter(is_staff=True).count()
#     superusers = User.objects.filter(is_superuser=True).count()
#     non_editor_users = total_users - active_editors
    
#     active_editors_percentage = (active_editors / total_users * 100) if total_users > 0 else 0
    
#     # إحصائيات المشاهدات
#     days_since_start = max((timezone.now() - timezone.make_aware(datetime.datetime(2024, 1, 1))).days, 1)
#     average_views_per_day = total_views / days_since_start
#     average_views_per_post = total_views / total_posts if total_posts > 0 else 0

#     # المقالات الأعلى مشاهدة
#     top_viewed_posts = Post.objects.filter(status='published').order_by('-views')[:5]
    
#     # إحصائيات اليوم
#     today = timezone.now().date()
#     yesterday = today - timezone.timedelta(days=1)
    
#     posts_today = Post.objects.filter(created_at__date=today).count()
#     posts_yesterday = Post.objects.filter(created_at__date=yesterday).count()
#     posts_change = ((posts_today - posts_yesterday) / posts_yesterday * 100) if posts_yesterday > 0 else 0
    
#     comments_today = Comment.objects.filter(created_at__date=today).count()
#     comments_yesterday = Comment.objects.filter(created_at__date=yesterday).count()
#     comments_change = ((comments_today - comments_yesterday) / comments_yesterday * 100) if comments_yesterday > 0 else 0
    
#     users_today = User.objects.filter(date_joined__date=today).count()
#     users_yesterday = User.objects.filter(date_joined__date=yesterday).count()
#     users_change = ((users_today - users_yesterday) / users_yesterday * 100) if users_yesterday > 0 else 0
    
#     views_today = Post.objects.filter(publish_date__date=today).aggregate(Sum('views'))['views__sum'] or 0
#     views_yesterday = Post.objects.filter(publish_date__date=yesterday).aggregate(Sum('views'))['views__sum'] or 0
#     views_change = ((views_today - views_yesterday) / views_yesterday * 100) if views_yesterday > 0 else 0

#     # إحصائيات حسب النوع
#     posts_by_type = {
#         'courses': Post.objects.filter(category__category_type='courses').count(),
#         'articles': Post.objects.filter(category__category_type='articles').count(),
#         'grants': Post.objects.filter(category__category_type='grants').count(),
#         'books': Post.objects.filter(category__category_type='books').count(),
#     }
    
#     # إحصائيات الشهر
#     this_month = timezone.now().month
#     this_year = timezone.now().year
#     posts_this_month = Post.objects.filter(
#         created_at__year=this_year,
#         created_at__month=this_month
#     ).count()
    
#     comments_this_month = Comment.objects.filter(
#         created_at__year=this_year,
#         created_at__month=this_month
#     ).count()
    
#     users_this_month = User.objects.filter(
#         date_joined__year=this_year,
#         date_joined__month=this_month
#     ).count()
    
#     # نسبة التفاعل (متوسط المشاهدات لكل مقال)
#     average_views_per_post = (total_views / total_posts) if total_posts > 0 else 0
    
#     # إحصائيات المنشورات حسب حالة النشر
#     posts_by_status = {
#         'published': published_posts,
#         'draft': draft_posts,
#         'private': private_posts,
#         'archived': archived_posts,
#     }
    
#     # الأقسام الأكثر نشاطاً
#     categories_with_counts = Category.objects.annotate(
#         post_count=Count('posts')
#     ).order_by('-post_count')[:5]
    
#     # المؤلفون الأكثر نشاطاً
#     top_authors = User.objects.annotate(
#         post_count=Count('posts'),
#         total_views=Sum('posts__views')
#     ).filter(post_count__gt=0).order_by('-post_count')[:5]
    
#     context = {
#         # الإحصائيات الأساسية
#         'total_posts': total_posts,
#         'total_comments': total_comments,
#         'total_users': total_users,
#         'total_views': total_views,

#         # المنشورات والتعليقات
#         'recent_posts': recent_posts,
#         'new_comments': new_comments,
        
#         # إحصائيات المنشورات
#         'published_posts': published_posts,
#         'draft_posts': draft_posts,
#         'private_posts': private_posts,
#         'archived_posts': archived_posts,
#         'published_percentage': round(published_percentage, 1),
#         'posts_by_status': posts_by_status,
        
#         # إحصائيات التعليقات
#         'approved_comments': approved_comments,
#         'pending_comments': pending_comments,
#         'approved_comments_percentage': round(approved_comments_percentage, 1),
        
#         # إحصائيات المستخدمين
#         'active_editors': active_editors,
#         'staff_users': staff_users,
#         'superusers': superusers,
#         'non_editor_users': non_editor_users,
#         'active_editors_percentage': round(active_editors_percentage, 1),
        
#         # إحصائيات المشاهدات
#         'average_views_per_day': round(average_views_per_day, 1),
#         'average_views_per_post': round(average_views_per_post, 1),
#         'top_viewed_posts': top_viewed_posts,
#         'average_views_per_post': round(average_views_per_post, 0),
        
#         # إحصائيات اليوم
#         'posts_today': posts_today,
#         'posts_yesterday': posts_yesterday,
#         'posts_change': round(posts_change, 1),
        
#         'comments_today': comments_today,
#         'comments_yesterday': comments_yesterday,
#         'comments_change': round(comments_change, 1),
        
#         'users_today': users_today,
#         'users_yesterday': users_yesterday,
#         'users_change': round(users_change, 1),
        
#         'views_today': views_today,
#         'views_yesterday': views_yesterday,
#         'views_change': round(views_change, 1),
        
#         # إحصائيات حسب النوع
#         'posts_by_type': posts_by_type,
        
#         # إحصائيات الشهر
#         'posts_this_month': posts_this_month,
#         'comments_this_month': comments_this_month,
#         'users_this_month': users_this_month,
        
#         # إحصائيات إضافية
#         'categories_with_counts': categories_with_counts,
#         'top_authors': top_authors,
        
#         # للقالب
#         'days_since_start': days_since_start,
#         'this_month': this_month,
#         'this_year': this_year,
#     }
    
#     return render(request, 'admin_dashboard.html', context)



@login_required
def admin_dashboard(request):
    """
    لوحة تحكم الإدارة (مختلفة حسب صلاحيات المستخدم)
    """
    user = request.user
    
    if not user.is_staff and not (hasattr(user, 'profile') and user.profile.is_content_editor):
        return redirect('dashboard')
    
    # تحديد نوع لوحة التحكم
    if user.is_superuser:
        template_name = 'admin_dashboard.html'
        is_superuser = True
    elif user.is_staff:
        template_name = 'staff_dashboard.html'
        is_superuser = False
    else:
        template_name = 'content_dashboard.html'
        is_superuser = False
    
    # إحصائيات عامة (تختلف حسب الصلاحيات)
    if user.is_superuser:
        # الأدمن يرى كل شيء
        total_posts = Post.objects.count()
        total_comments = Comment.objects.count()
        total_users = User.objects.count()
        total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
        
        recent_posts = Post.objects.all().select_related('category', 'author').order_by('-created_at')[:10]
        new_comments = Comment.objects.filter(is_approved=False).select_related('post').order_by('-created_at')[:10]
        
    elif user.is_staff:
        # الـ Staff يرى كل شيء لكن بإمكانيات محدودة
        total_posts = Post.objects.count()
        total_comments = Comment.objects.count()
        total_users = User.objects.count()
        total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
        
        recent_posts = Post.objects.all().select_related('category', 'author').order_by('-created_at')[:10]
        new_comments = Comment.objects.filter(is_approved=False).select_related('post').order_by('-created_at')[:10]
        
    else:
        # المحرر العادي يرى فقط إحصائياته
        total_posts = Post.objects.filter(author=user).count()
        total_comments = Comment.objects.filter(post__author=user).count()
        total_users = 0  # لا يرى إحصائيات المستخدمين
        total_views = Post.objects.filter(author=user).aggregate(total_views=Sum('views'))['total_views'] or 0
        
        recent_posts = Post.objects.filter(author=user).select_related('category', 'author').order_by('-created_at')[:10]
        new_comments = Comment.objects.filter(
            post__author=user,
            is_approved=False
        ).select_related('post').order_by('-created_at')[:10]
    
    # حسابات النسب
    published_posts = Post.objects.filter(status='published').count()
    published_percentage = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
    approved_comments = Comment.objects.filter(is_approved=True).count()
    approved_comments_percentage = (approved_comments / total_comments * 100) if total_comments > 0 else 0
    
    # إحصائيات إضافية للأدمن فقط
    if user.is_superuser:
        active_editors = UserProfile.objects.filter(is_content_editor=True).count()
        non_editor_users = total_users - active_editors
        active_editors_percentage = (active_editors / total_users * 100) if total_users > 0 else 0
        
        # إحصائيات اليوم
        today = timezone.now().date()
        views_today = Post.objects.filter(publish_date__date=today).aggregate(Sum('views'))['views__sum'] or 0
        
        # إحصائيات حسب النوع
        posts_by_type = {
            'courses': Post.objects.filter(category__category_type='courses').count(),
            'articles': Post.objects.filter(category__category_type='articles').count(),
            'grants': Post.objects.filter(category__category_type='grants').count(),
            'books': Post.objects.filter(category__category_type='books').count(),
        }
        
        # متوسط المشاهدات
        days_since_start = max((timezone.now() - timezone.make_aware(datetime.datetime(2024, 1, 1))).days, 1)
        average_views_per_day = total_views / days_since_start
        
        # إضافة البيانات الإضافية للأدمن
        admin_context = {
            'active_editors': active_editors,
            'non_editor_users': non_editor_users,
            'active_editors_percentage': round(active_editors_percentage, 1),
            'views_today': views_today,
            'posts_by_type': posts_by_type,
            'average_views_per_day': round(average_views_per_day, 1),
            'posts_today': Post.objects.filter(created_at__date=today).count(),
            'comments_today': Comment.objects.filter(created_at__date=today).count(),
            'users_today': User.objects.filter(date_joined__date=today).count(),
            'average_views_per_post': round(total_views / total_posts, 0) if total_posts > 0 else 0,
        }
    else:
        admin_context = {}
    
    context = {
        # الإحصائيات الأساسية
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_users': total_users,
        'total_views': total_views,
        'recent_posts': recent_posts,
        'new_comments': new_comments,
        'published_posts': published_posts,
        'published_percentage': round(published_percentage, 1),
        'approved_comments': approved_comments,
        'approved_comments_percentage': round(approved_comments_percentage, 1),
        
        # معلومات المستخدم
        'user': user,
        'is_superuser': is_superuser,
        
        # سياق الأدمن الإضافي
        **admin_context,
    }
    
    return render(request, template_name, context)


@login_required
def dashboard(request):
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-created_at')[:10]
    
    # إحصائيات للمستخدم
    total_posts = Post.objects.filter(author=user).count()
    published_posts = Post.objects.filter(author=user, status='published').count()
    draft_posts = Post.objects.filter(author=user, status='draft').count()
    
    # إحصائيات المشاهدات
    total_views = Post.objects.filter(author=user).aggregate(total_views=Sum('views'))['total_views'] or 0
    
    context = {
        'user': user,
        'posts': posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_views': total_views,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    """
    صفحة الملف الشخصي للمستخدم
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('profile')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = UserProfileForm(instance=user_profile)

    # حساب عدد المنشورات المنشورة
    published_posts_count = request.user.posts.filter(status='published').count()
    
    context = {
        'title': 'ملفي الشخصي',
        'user': request.user,
        'profile': user_profile,
        'form': form,
        'published_posts_count': published_posts_count,
    }
    return render(request, 'auth/profile.html', context)

# login and register views  ------------


def login_view(request):
    """
    عرض تسجيل الدخول
    """
    # إذا كان المستخدم مسجل دخوله بالفعل، توجيهه للصفحة الرئيسية
    if request.user.is_authenticated:
        messages.info(request, 'أنت مسجل الدخول بالفعل!')
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # إذا لم يختار "تذكرني"، ضبط الجلسة لتكون مؤقتة
                if not remember_me:
                    request.session.set_expiry(0)  # انتهاء الجلسة عند إغلاق المتصفح
                else:
                    request.session.set_expiry(1209600)  # أسبوعين
                
                messages.success(request, f'مرحباً بك {user.username}! تم تسجيل دخولك بنجاح.')
                
                # التوجيه إلى الصفحة المطلوبة الأصلية أو الصفحة الرئيسية
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة!')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'تسجيل الدخول - موقع التعليم'
    }
    return render(request, 'auth/login.html', context)


# @csrf_exempt
def register(request):
    """
    عرض إنشاء حساب جديد
    """
    if request.user.is_authenticated:
        messages.info(request, 'أنت مسجل الدخول بالفعل!')
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # حفظ المستخدم أولاً
            user = form.save()

            # إنشاء UserProfile فقط إذا لم يكن موجود
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": f"{form.cleaned_data.get('first_name','')} {form.cleaned_data.get('last_name','')}".strip()
                }
            )

            # تسجيل دخول المستخدم تلقائياً
            login(request, user)
            messages.success(request, f'مرحباً بك {user.username}! تم إنشاء حسابك بنجاح.')
            return redirect('home')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {
        'form': form,
        'title': 'إنشاء حساب - موقع التعليم'
    })



@login_required
def logout_view(request):

    if request.method == 'POST':
        logout(request)
        messages.success(request, 'تم تسجيل خروجك بنجاح. نراك قريباً!')
        return redirect('home')
    
    # إذا كان GET، عرض صفحة تأكيد تسجيل الخروج
    context = {
        'title': 'تسجيل الخروج - موقع التعليم'
    }
    return render(request, 'auth/logout.html', context)

# ============ VIEWS الملف الشخصي ============


@login_required
def change_password(request):
    """
    تغيير كلمة المرور للمستخدم الحالي
    """
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # تحديث الجلسة
            messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('profile')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ChangePasswordForm(request.user)
    
    context = {
        'title': 'تغيير كلمة المرور',
        'form': form
    }
    return render(request, 'auth/change_password.html', context)

# ============ VIEWS استعادة كلمة المرور ============

def password_reset_request(request):
    """
    طلب إعادة تعيين كلمة المرور
    """
    # إذا كان المستخدم مسجل دخوله بالفعل، توجيهه للصفحة الرئيسية
    if request.user.is_authenticated:
        messages.info(request, 'أنت مسجل الدخول بالفعل!')
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # البحث عن المستخدمين بهذا البريد
            associated_users = User.objects.filter(Q(email__iexact=email))
            
            if associated_users.exists():
                for user in associated_users:
                    if user.is_active:
                        # إعداد بيانات البريد الإلكتروني
                        subject = "إعادة تعيين كلمة المرور - موقع التعليم"
                        
                        # إنشاء الرمز المميز
                        token = default_token_generator.make_token(user)
                        uid = urlsafe_base64_encode(force_bytes(user.pk))
                        
                        # إنشاء رابط إعادة التعيين
                        reset_url = request.build_absolute_uri(
                            f'/reset/{uid}/{token}/'
                        )
                        
                        # إعداد محتوى البريد الإلكتروني
                        context = {
                            'email': user.email,
                            'username': user.username,
                            'reset_url': reset_url,
                            'site_name': 'موقع التعليم',
                            'user': user,
                        }
                        
                        # إنشاء محتوى البريد
                        html_message = render_to_string('emails/password_reset_email.html', context)
                        plain_message = strip_tags(html_message)
                        
                        try:
                            # إرسال البريد الإلكتروني
                            send_mail(
                                subject=subject,
                                message=plain_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                                html_message=html_message,
                                fail_silently=False,
                            )
                            
                            messages.success(request, f'تم إرسال رابط إعادة التعيين إلى {email}.')
                            return render(request, 'auth/password_reset_done.html', {'email': email})
                            
                        except Exception as e:
                            messages.error(request, f'حدث خطأ أثناء إرسال البريد: {str(e)}')
                    else:
                        messages.error(request, 'هذا الحساب غير مفعل.')
            else:
                messages.error(request, 'لا يوجد حساب مرتبط بهذا البريد الإلكتروني.')
        else:
            messages.error(request, 'يرجى إدخال بريد إلكتروني صحيح.')
    else:
        form = CustomPasswordResetForm()
    
    context = {
        'form': form,
        'title': 'استعادة كلمة المرور - موقع التعليم'
    }
    return render(request, 'auth/password_reset.html', context)

def password_reset_confirm(request, uidb64, token):
    """
    تأكيد إعادة تعيين كلمة المرور وتعيين كلمة مرور جديدة
    """
    # إذا كان المستخدم مسجل دخوله بالفعل، توجيهه للصفحة الرئيسية
    if request.user.is_authenticated:
        messages.info(request, 'أنت مسجل الدخول بالفعل!')
        return redirect('home')
    
    try:
        # فك تشفير uid
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # التحقق من الرمز المميز
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                
                # إرسال إشعار تغيير كلمة المرور
                subject = "تم تغيير كلمة المرور - موقع التعليم"
                context = {
                    'username': user.username,
                    'site_name': 'موقع التعليم'
                }
                
                html_message = render_to_string('emails/password_changed_email.html', context)
                plain_message = strip_tags(html_message)
                
                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                except:
                    pass  # تجاهل أي خطأ في إرسال البريد الإلكتروني
                
                messages.success(request, 'تم تعيين كلمة المرور الجديدة بنجاح! يمكنك الآن تسجيل الدخول.')
                return redirect('password_reset_complete')
            else:
                messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
        else:
            form = CustomSetPasswordForm(user)
        
        context = {
            'form': form,
            'title': 'تعيين كلمة مرور جديدة - موقع التعليم',
            'validlink': True
        }
        return render(request, 'auth/password_reset_confirm.html', context)
    else:
        messages.error(request, 'رابط إعادة التعيين غير صالح أو منتهي الصلاحية!')
        context = {
            'title': 'رابط غير صالح - موقع التعليم',
            'validlink': False
        }
        return render(request, 'auth/password_reset_confirm.html', context)

def password_reset_complete(request):
    """
    عرض تأكيد اكتمال إعادة تعيين كلمة المرور
    """
    context = {
        'title': 'تم تعيين كلمة المرور - موقع التعليم'
    }
    return render(request, 'auth/password_reset_complete.html', context)



# ============ VIEWS إضافية ============

@login_required
def delete_account(request):
    """
    حذف حساب المستخدم
    """
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        # التحقق من كلمة المرور
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            # حذف الحساب
            user.delete()
            logout(request)
            messages.success(request, 'تم حذف حسابك بنجاح. نأسف لرحيلك!')
            return redirect('home')
        else:
            messages.error(request, 'كلمة المرور غير صحيحة!')
    
    context = {
        'title': 'حذف الحساب - موقع التعليم'
    }
    return render(request, 'auth/delete_account.html', context)

def check_username(request):
    """
    التحقق من توفر اسم المستخدم (AJAX)
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.GET.get('username', '')
        
        if username:
            exists = User.objects.filter(username__iexact=username).exists()
            return HttpResponse(json.dumps({'exists': exists}), content_type='application/json')
    
    return HttpResponse(json.dumps({'error': 'Invalid request'}), content_type='application/json')

def check_email(request):
    """
    التحقق من توفر البريد الإلكتروني (AJAX)
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.GET.get('email', '')
        
        if email:
            exists = User.objects.filter(email__iexact=email).exists()
            return HttpResponse(json.dumps({'exists': exists}), content_type='application/json')
    
    return HttpResponse(json.dumps({'error': 'Invalid request'}), content_type='application/json')




# ============ VIEWS الأخطاء ============

def handler404(request, exception):
    """
    معالج صفحة 404
    """
    context = {
        'title': '404 - الصفحة غير موجودة'
    }
    return render(request, 'errors/404.html', context, status=404)

def handler500(request):
    """
    معالج صفحة 500
    """
    context = {
        'title': '500 - خطأ في الخادم'
    }
    return render(request, 'errors/500.html', context, status=500)

def handler403(request, exception):
    """
    معالج صفحة 403
    """
    context = {
        'title': '403 - غير مصرح بالوصول'
    }
    return render(request, 'errors/403.html', context, status=403)

def handler400(request, exception):
    """
    معالج صفحة 400
    """
    context = {
        'title': '400 - طلب غير صالح'
    }
    return render(request, 'errors/400.html', context, status=400)

# ============ VIEWS الأدمن ============

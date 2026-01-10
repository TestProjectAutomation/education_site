from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .models import *
from .forms import *


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
    
    context = {
        'courses_posts': courses_posts,
        'articles_posts': articles_posts,
        'grants_posts': grants_posts,
        'books_posts': books_posts,
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

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # زيادة عدد المشاهدات
    post.increment_views()
    
    # الحصول على التعليقات المعتمدة فقط
    comments = post.comments.filter(is_approved=True)
    
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
    }
    
    return render(request, 'post_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # تسجيل دخول المستخدم تلقائياً
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح!')
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-created_at')[:10]
    
    # إحصائيات للمستخدم
    total_posts = Post.objects.filter(author=user).count()
    published_posts = Post.objects.filter(author=user, status='published').count()
    
    context = {
        'user': user,
        'posts': posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@user_passes_test(is_content_editor)
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # إذا لم يتم تحديد تاريخ النشر، استخدم الوقت الحالي
            if not post.publish_date:
                post.publish_date = timezone.now()
            
            post.save()
            messages.success(request, 'تم إنشاء المنشور بنجاح!')
            return redirect('dashboard')
    else:
        form = PostForm()
    
    return render(request, 'create_post.html', {'form': form})

@user_passes_test(is_content_editor)
@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنشور بنجاح!')
            return redirect('dashboard')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'edit_post.html', {'form': form, 'post': post})

@staff_member_required
def admin_dashboard(request):
    # إحصائيات عامة
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_users = User.objects.count()
    total_views = Post.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
    
    # المنشورات الأخيرة
    recent_posts = Post.objects.all().order_by('-created_at')[:10]
    
    # التعليقات الجديدة
    new_comments = Comment.objects.filter(is_approved=False).order_by('-created_at')[:10]
    
    # إحصائيات إضافية
    published_posts = Post.objects.filter(status='published').count()
    published_percentage = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
    approved_comments = Comment.objects.filter(is_approved=True).count()
    approved_comments_percentage = (approved_comments / total_comments * 100) if total_comments > 0 else 0
    
    active_editors = UserProfile.objects.filter(is_content_editor=True).count()
    total_editors = UserProfile.objects.filter(user__is_staff=True).count()
    active_editors_percentage = (active_editors / total_editors * 100) if total_editors > 0 else 0
    
    # إحصائيات اليوم
    today = timezone.now().date()
    posts_today = Post.objects.filter(created_at__date=today).count()
    comments_today = Comment.objects.filter(created_at__date=today).count()
    users_today = User.objects.filter(date_joined__date=today).count()
    views_today = Post.objects.filter(publish_date__date=today).aggregate(Sum('views'))['views__sum'] or 0
    
    context = {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_users': total_users,
        'total_views': total_views,
        'recent_posts': recent_posts,
        'new_comments': new_comments,
        'published_percentage': round(published_percentage, 1),
        'approved_comments_percentage': round(approved_comments_percentage, 1),
        'active_editors_percentage': round(active_editors_percentage, 1),
        'posts_today': posts_today,
        'comments_today': comments_today,
        'users_today': users_today,
        'views_today': views_today,
    }
    
    return render(request, 'admin_dashboard.html', context)

    # إحصائيات عامة
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_users = User.objects.count()
    
    # المنشورات الأخيرة
    recent_posts = Post.objects.all().order_by('-created_at')[:10]
    
    # التعليقات الجديدة
    new_comments = Comment.objects.filter(is_approved=False).order_by('-created_at')[:10]
    
    context = {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_users': total_users,
        'recent_posts': recent_posts,
        'new_comments': new_comments,
    }
    
    return render(request, 'admin_dashboard.html', context)

def search(request):


    query = request.GET.get('q', '')
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(category__name__icontains=query),
            status='published'
        ).order_by('-publish_date')
        
        # تقسيم النتائج حسب النوع
        results_by_type = []
        for cat_type in ['courses', 'articles', 'grants', 'books']:
            category_results = results.filter(category__category_type=cat_type)
            if category_results.exists():
                results_by_type.append((cat_type, category_results))
    else:
        results = Post.objects.none()
        results_by_type = []
    
    # الترقيم
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'results': page_obj,
        'query': query,
        'count': results.count(),
        'results_by_type': results_by_type,
        'courses_count': results.filter(category__category_type='courses').count(),
        'articles_count': results.filter(category__category_type='articles').count(),
        'grants_count': results.filter(category__category_type='grants').count(),
        'books_count': results.filter(category__category_type='books').count(),
    }
    
    return render(request, 'search.html', context)

    query = request.GET.get('q', '')
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(category__name__icontains=query),
            status='published'
        ).order_by('-publish_date')
    else:
        results = Post.objects.none()
    
    return render(request, 'search.html', {
        'results': results,
        'query': query,
        'count': results.count()
    })


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

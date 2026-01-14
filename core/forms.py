from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    AuthenticationForm, 
    UserCreationForm, 
    PasswordResetForm, 
    SetPasswordForm,
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
    UsernameField

)
from .models import *






# ======== وظيفة مساعدة لتطبيق التنسيق التلقائي ========
def apply_field_styling(field, field_type, label=None):
    """
    تطبيق تنسيق تلقائي على حقل مع إعدادات متقدمة
    """
    # الحصول على نوع Widget
    widget_type = type(field.widget).__name__
    
    # إعدادات أساسية لكل الحقول
    if not field.widget.attrs:
        field.widget.attrs = {}
    
    # إضافة class عام
    if 'class' not in field.widget.attrs:
        field.widget.attrs['class'] = 'form-control'
    
    # حسب نوع الحقل
    if field_type in ['CharField', 'EmailField', 'URLField', 'SlugField']:
        # تطبيق max_length تلقائياً
        if hasattr(field, 'max_length') and field.max_length:
            field.widget.attrs['maxlength'] = str(field.max_length)
            
            # إضافة error message لـ max_length
            if not field.error_messages.get('max_length'):
                field.error_messages['max_length'] = f'هذا الحقل لا يمكن أن يتجاوز {field.max_length} حرف.'
        
        # إضافة placeholder تلقائي
        if not field.widget.attrs.get('placeholder') and label:
            field.widget.attrs['placeholder'] = f'أدخل {label.lower()}'
    
    elif field_type == 'TextField':
        if not field.widget.attrs.get('rows'):
            field.widget.attrs['rows'] = 4
        if not field.widget.attrs.get('placeholder') and label:
            field.widget.attrs['placeholder'] = f'أدخل {label.lower()}'
    
    elif field_type == 'IntegerField':
        field.widget.attrs['type'] = 'number'
        if not field.widget.attrs.get('placeholder') and label:
            field.widget.attrs['placeholder'] = f'أدخل {label.lower()}'
    
    elif field_type == 'DateField':
        field.widget.attrs['type'] = 'date'
    
    elif field_type == 'DateTimeField':
        field.widget.attrs['type'] = 'datetime-local'
    
    elif field_type == 'BooleanField':
        field.widget.attrs['class'] = 'form-check-input'
    
    # حسب نوع Widget
    if widget_type == 'Textarea':
        if not field.widget.attrs.get('rows'):
            field.widget.attrs['rows'] = 3
    
    elif widget_type == 'Select':
        field.widget.attrs['class'] = 'form-select'
    
    elif widget_type in ['PasswordInput', 'EmailInput', 'URLInput', 'NumberInput']:
        if not field.widget.attrs.get('placeholder') and label:
            field.widget.attrs['placeholder'] = f'أدخل {label.lower()}'
    
    return field


def auto_style_form(form_class):
    """
    decorator لتطبيق التنسيق التلقائي على جميع حقول الفورم
    """
    class AutoStyledForm(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # تطبيق التنسيق على جميع الحقول
            for field_name, field in self.fields.items():
                field_type = type(field).__name__
                label = field.label or field_name.replace('_', ' ').title()
                
                # تجاهل بعض الحقول الخاصة
                if field_name in ['password', 'password1', 'password2', 'old_password']:
                    continue
                
                # تطبيق التنسيق
                field = apply_field_styling(field, field_type, label)
    
    return AutoStyledForm


# ======== فئة أساسية لجميع الفورمس ========
class StyledForm(forms.Form):
    """
    فئة أساسية مع تنسيق تلقائي لجميع الفورمس
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_all_fields()
    
    def style_all_fields(self):
        """تطبيق التنسيق على جميع الحقول"""
        for field_name, field in self.fields.items():
            field_type = type(field).__name__
            label = field.label or field_name.replace('_', ' ').title()
            
            # تجاهل بعض الحقول الخاصة
            if field_name in ['password', 'password1', 'password2', 'old_password']:
                continue
            
            # تطبيق التنسيق
            field = apply_field_styling(field, field_type, label)


class StyledModelForm(forms.ModelForm):
    """
    فئة أساسية مع تنسيق تلقائي لجميع ModelForms
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_all_fields()
    
    def style_all_fields(self):
        """تطبيق التنسيق على جميع الحقول"""
        for field_name, field in self.fields.items():
            field_type = type(field).__name__
            label = field.label or field_name.replace('_', ' ').title()
            
            # تجاهل بعض الحقول الخاصة
            if field_name in ['password', 'password1', 'password2', 'old_password']:
                continue
            
            # تطبيق التنسيق
            field = apply_field_styling(field, field_type, label)









# # ======== Login Form ========
# class LoginForm(AuthenticationForm):
#     username = forms.CharField(
#         label='اسم المستخدم أو البريد الإلكتروني',
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'أدخل اسم المستخدم أو البريد الإلكتروني'
#         })
#     )
#     password = forms.CharField(
#         label='كلمة المرور',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'أدخل كلمة المرور'
#         })
#     )
#     remember_me = forms.BooleanField(
#         required=False,
#         label='تذكرني',
#         widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
#     )

# # ======== Registration Form ========
# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(
#         required=True,
#         label='البريد الإلكتروني',
#         widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'أدخل بريدك الإلكتروني'})
#     )
#     first_name = forms.CharField(
#         required=False,
#         max_length=30,
#         label='الاسم الأول',
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'})
#     )
#     last_name = forms.CharField(
#         required=False,
#         max_length=30,
#         label='اسم العائلة',
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العائلة'})
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'اختر اسم مستخدم فريد'})
#         self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'أدخل كلمة المرور'})
#         self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'أعد إدخال كلمة المرور'})

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل!')
#         return email

# # ======== Password Forms ========
# class CustomPasswordResetForm(PasswordResetForm):
#     email = forms.EmailField(
#         label='البريد الإلكتروني',
#         max_length=254,
#         widget=forms.EmailInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'أدخل بريدك الإلكتروني المسجل',
#             'autocomplete': 'email'
#         })
#     )

# class CustomSetPasswordForm(SetPasswordForm):
#     new_password1 = forms.CharField(
#         label='كلمة المرور الجديدة',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'أدخل كلمة المرور الجديدة',
#             'autocomplete': 'new-password'
#         }),
#         help_text="""
#         <ul class="text-xs text-gray-600 space-y-1 mt-1">
#             <li>• يجب أن تحتوي على 8 أحرف على الأقل</li>
#             <li>• يجب أن تحتوي على حروف وأرقام</li>
#             <li>• يجب أن لا تكون شائعة الاستخدام</li>
#             <li>• يجب أن لا تتشابه مع معلوماتك الشخصية</li>
#         </ul>
#         """
#     )
#     new_password2 = forms.CharField(
#         label='تأكيد كلمة المرور',
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'أعد إدخال كلمة المرور',
#             'autocomplete': 'new-password'
#         })
#     )

# class ChangePasswordForm(PasswordChangeForm):
#     old_password = forms.CharField(
#         label='كلمة المرور الحالية',
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور الحالية'})
#     )
#     new_password1 = forms.CharField(
#         label='كلمة المرور الجديدة',
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور الجديدة'})
#     )
#     new_password2 = forms.CharField(
#         label='تأكيد كلمة المرور',
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أعد إدخال كلمة المرور الجديدة'})
#     )

# # ======== UserProfile Form ========
# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = [
#             'full_name',
#             'bio',
#             'profile_image',
#             'phone',
#             'birth_date',
#             'is_content_editor',
#             'can_manage_comments',
#             'can_manage_categories',
#         ]

#         widgets = {
#             'full_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'phone': forms.TextInput(attrs={'class': 'form-control'}),
#             'birth_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['profile_image'].widget.attrs.update({'class': 'form-control-file'})

# # ======== Comment Form ========
# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['name', 'email', 'content']
#         widgets = {'content': forms.Textarea(attrs={'rows': 4})}

# # ======== Post Form ========
# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = [
#             'title', 'category', 'content', 'image',  # استخدم 'image' وليس 'featured_image'
#             'excerpt', 'link', 'link_delay', 'status',
#             'seo_title', 'seo_description', 'seo_keywords',
#             'publish_date'
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'أدخل عنوان المنشور',
#                 'required': True
#             }),
#             'category': forms.Select(attrs={
#                 'class': 'form-control',
#                 'required': True
#             }),
#             'content': forms.Textarea(attrs={
#                 'class': 'form-control d-none',
#                 'rows': 5,
#                 'id': 'post_content_field'
#             }),
#             'image': forms.FileInput(attrs={  # استخدم 'image' هنا
#                 'class': 'form-control-file d-none',
#                 'accept': 'image/*'
#             }),
#             'excerpt': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'ملخص مختصر للمنشور'
#             }),
#             'link': forms.URLInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'https://example.com'
#             }),
#             'link_delay': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': 0,
#                 'max': 300
#             }),
#             'status': forms.Select(attrs={
#                 'class': 'form-control d-none'
#             }),
#             'seo_title': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'عنوان لمحركات البحث'
#             }),
#             'seo_description': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 2,
#                 'placeholder': 'وصف لمحركات البحث'
#             }),
#             'seo_keywords': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'كلمات مفتاحية مفصولة بفواصل'
#             }),
#             'publish_date': forms.DateTimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'datetime-local'
#             }),
#         }
#         excerpt = forms.CharField(
#             widget=forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'ملخص مختصر للمنشور',
#                 'maxlength': '300'
#             }),
#             max_length=300,
#             required=False,
#             error_messages={
#                 'max_length': 'الملخص لا يمكن أن يتجاوز 300 حرف.'
#             }
#         )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # تعيين قيمة افتراضية للفئة إذا كانت فارغة
#         if not self['category'].value():
#             self.fields['category'].empty_label = "-- اختر الفئة --"
        
#         # جعل بعض الحقول مطلوبة
#         self.fields['title'].required = True
#         self.fields['category'].required = True
        
# # ======== User Update Form ========
# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']

# # ======== UserRole Form ========
# class UserRoleForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = [
#             'is_content_editor',
#             'can_manage_comments',
#             'can_manage_categories',
#         ]

#         widgets = {
#             'is_content_editor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'can_manage_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'can_manage_categories': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
























# ======== Login Form ========
@auto_style_form
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='اسم المستخدم أو البريد الإلكتروني'
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput()
    )
    remember_me = forms.BooleanField(
        required=False,
        label='تذكرني',
        widget=forms.CheckboxInput()
    )


# ======== Registration Form ========
@auto_style_form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='البريد الإلكتروني',
        max_length=254
    )
    first_name = forms.CharField(
        required=False,
        max_length=30,
        label='الاسم الأول'
    )
    last_name = forms.CharField(
        required=False,
        max_length=30,
        label='اسم العائلة'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة placeholders مخصصة لبعض الحقول
        self.fields['username'].widget.attrs.update({'placeholder': 'اختر اسم مستخدم فريد'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'أدخل كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'أعد إدخال كلمة المرور'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل!')
        return email


# ======== Password Forms ========
@auto_style_form
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='البريد الإلكتروني',
        max_length=254
    )


@auto_style_form
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(),
        help_text="""
        <ul class="text-xs text-gray-600 space-y-1 mt-1">
            <li>• يجب أن تحتوي على 8 أحرف على الأقل</li>
            <li>• يجب أن تحتوي على حروف وأرقام</li>
            <li>• يجب أن لا تكون شائعة الاستخدام</li>
            <li>• يجب أن لا تتشابه مع معلوماتك الشخصية</li>
        </ul>
        """
    )
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput()
    )


@auto_style_form
class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='كلمة المرور الحالية',
        widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput()
    )


# ======== UserProfile Form ========
@auto_style_form
class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        max_length=1000
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'full_name',
            'bio',
            'profile_image',
            'phone',
            'birth_date',
            'is_content_editor',
            'can_manage_comments',
            'can_manage_categories',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إعدادات خاصة لبعض الحقول
        self.fields['profile_image'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['birth_date'].widget.attrs.update({'type': 'date'})


# ======== Comment Form ========
@auto_style_form
class CommentForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        label='الاسم'
    )
    email = forms.EmailField(
        max_length=254,
        label='البريد الإلكتروني'
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        max_length=1000,
        label='التعليق'
    )
    
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']


# ======== Post Form ========
@auto_style_form
class PostForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        label='عنوان المنشور',
        required=True
    )
    
    excerpt = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=300,
        required=False,
        label='ملخص المنشور',
        error_messages={
            'max_length': 'الملخص لا يمكن أن يتجاوز 300 حرف.'
        }
    )
    
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control d-none', 'id': 'post_content_field'}),
        label='المحتوى',
        required=False
    )
    
    seo_title = forms.CharField(
        max_length=200,
        required=False,
        label='عنوان SEO'
    )
    
    seo_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        max_length=300,
        required=False,
        label='وصف SEO'
    )
    
    seo_keywords = forms.CharField(
        max_length=200,
        required=False,
        label='كلمات مفتاحية'
    )
    
    link_delay = forms.IntegerField(
        min_value=0,
        max_value=300,
        initial=30,
        label='تأخير الرابط (ثواني)'
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'category', 'content', 'image',
            'excerpt', 'link', 'link_delay', 'status',
            'seo_title', 'seo_description', 'seo_keywords',
            'publish_date'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # إعدادات خاصة لبعض الحقول
        self.fields['image'].widget.attrs.update({
            'class': 'form-control-file d-none',
            'accept': 'image/*'
        })
        
        self.fields['publish_date'].widget.attrs.update({
            'type': 'datetime-local'
        })
        
        self.fields['status'].widget.attrs.update({
            'class': 'form-control d-none'
        })
        
        # تعيين placeholder مخصص
        self.fields['title'].widget.attrs.update({'placeholder': 'أدخل عنوان المنشور'})
        self.fields['excerpt'].widget.attrs.update({'placeholder': 'ملخص مختصر للمنشور'})
        self.fields['link'].widget.attrs.update({'placeholder': 'https://example.com'})
        self.fields['seo_title'].widget.attrs.update({'placeholder': 'عنوان لمحركات البحث'})
        self.fields['seo_description'].widget.attrs.update({'placeholder': 'وصف لمحركات البحث'})
        self.fields['seo_keywords'].widget.attrs.update({'placeholder': 'كلمات مفتاحية مفصولة بفواصل'})
        
        # تعيين قيمة افتراضية للفئة إذا كانت فارغة
        if not self['category'].value():
            self.fields['category'].empty_label = "-- اختر الفئة --"


# ======== User Update Form ========
@auto_style_form
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='الاسم الأول'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='اسم العائلة'
    )
    email = forms.EmailField(
        max_length=254,
        label='البريد الإلكتروني'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# ======== UserRole Form ========
@auto_style_form
class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'is_content_editor',
            'can_manage_comments',
            'can_manage_categories',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إعداد خاص لحقول BooleanField
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})
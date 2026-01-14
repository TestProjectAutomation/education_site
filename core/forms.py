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

# ======== Login Form ========
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='اسم المستخدم أو البريد الإلكتروني',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم أو البريد الإلكتروني'
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='تذكرني',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


# ======== Registration Form ========
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'أدخل بريدك الإلكتروني'})
    )
    first_name = forms.CharField(
        required=False,
        max_length=30,
        label='الاسم الأول',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'})
    )
    last_name = forms.CharField(
        required=False,
        max_length=30,
        label='اسم العائلة',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العائلة'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'اختر اسم مستخدم فريد'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'أدخل كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'أعد إدخال كلمة المرور'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل!')
        return email


# ======== Password Forms ========
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='البريد الإلكتروني',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني المسجل',
            'autocomplete': 'email'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور الجديدة',
            'autocomplete': 'new-password'
        }),
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
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور',
            'autocomplete': 'new-password'
        })
    )


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='كلمة المرور الحالية',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور الحالية'})
    )
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور الجديدة'})
    )
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أعد إدخال كلمة المرور الجديدة'})
    )


# ======== UserProfile Form ========
class UserProfileForm(forms.ModelForm):
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

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_image'].widget.attrs.update({'class': 'form-control-file'})


# ======== Comment Form ========
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {'content': forms.Textarea(attrs={'rows': 4})}


# ======== Post Form ========
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'image', 'link', 'link_delay', 'status']
        widgets = {'content': forms.Textarea(attrs={'rows': 10})}


# ======== User Update Form ========
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



# ======== UserRole Form ========
class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'is_content_editor',
            'can_manage_comments',
            'can_manage_categories',
        ]

        widgets = {
            'is_content_editor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_categories': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
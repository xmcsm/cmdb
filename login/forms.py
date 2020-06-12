from django import forms
from .models import User


class LoginForm(forms.Form):
    # captcha = CaptchaField(error_messages={"invalid": "验证码错误"})
    username = forms.CharField(label="用户名", min_length=1, max_length=64)
    password = forms.CharField(label="密码", min_length=6, max_length=256, widget=forms.PasswordInput)

    # class Meta:
    #    model = User
    #    fields = ['name', 'email', 'url', 'text', 'captcha']

class RegisterForm(forms.Form):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )

    username = forms.CharField(label="用户名", min_length=1, max_length=64,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '请输入用户名'}
        ))
    password = forms.CharField(label="密码", min_length=6, max_length=256,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入密码'}
        )
    )
    passwordagain = forms.CharField(
        label='确认密码',
        min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入确认密码'}
        )
    )
    nickname = forms.CharField(label="昵称", min_length=1, max_length=64,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '请输入昵称'}
        ))
    email = forms.EmailField(label="邮箱", min_length=1, max_length=64,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}
        ))
    sex = forms.ChoiceField(label="性别",choices=SEX_CHOICES)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在！')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        print(email)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在！')
        return email

    def clean_passwordagain(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['passwordagain']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致！')
        return password_again

class ChangePasswdForm(forms.Form):
    oldpasswd = forms.CharField(label="当前密码", min_length=6, max_length=256, widget=forms.PasswordInput)
    newpasswd = forms.CharField(label="新密码", min_length=6, max_length=256, widget=forms.PasswordInput)
    newpasswdagain = forms.CharField(label="确认新密码", min_length=6, max_length=256, widget=forms.PasswordInput)

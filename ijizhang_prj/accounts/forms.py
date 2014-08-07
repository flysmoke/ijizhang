#coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Register your models here.


class RegisterForm(forms.Form):
    username=forms.CharField(label=_(u"昵称"),max_length=20,widget=forms.TextInput(attrs={'size': 20,'class':"form-control"}))
    email=forms.EmailField(label=_(u"邮件"),max_length=20,widget=forms.EmailInput(attrs={'size': 20,'class':"form-control"}))    
    password=forms.CharField(label=_(u"密码"),max_length=20,widget=forms.PasswordInput(attrs={'size': 20,'class':"form-control"}))
    re_password=forms.CharField(label=_(u"重复密码"),max_length=20,widget=forms.PasswordInput(attrs={'size': 20,'class':"form-control"}))

    def clean_username(self):
        '''验证重复昵称'''
        users = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not users:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_(u"该昵称已经被使用请使用其他的昵称"))
        
    def clean_email(self):
        '''验证重复email'''
        emails = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not emails:
            return self.cleaned_data["email"]
        raise forms.ValidationError(_(u"该邮箱已经被使用请使用其他的"))
		
    def clean(self):
        """验证其他非法"""
        cleaned_data = super(RegisterForm, self).clean()

        if cleaned_data.get("password") == cleaned_data.get("username"):
            raise forms.ValidationError(_(u"用户名和密码不能一样"))
        if cleaned_data.get("password") != cleaned_data.get("re_password"):
            raise forms.ValidationError(_(u"两次输入密码不一致"))

        return cleaned_data

			
class LoginForm(forms.Form):
    username=forms.CharField(label=_(u"昵称"),max_length=20,widget=forms.TextInput(attrs={'size': 20,'class':"form-control"}))
    password=forms.CharField(label=_(u"密码"),max_length=20,widget=forms.PasswordInput(attrs={'size': 20,'class':"form-control"}))


	
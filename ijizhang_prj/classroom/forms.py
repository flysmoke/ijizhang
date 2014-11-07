#coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget

# Register your models here.
from classroom.models import Room


class RoomForm(ModelForm):

    class Meta:
        model = Room
        fields = ['name']
	
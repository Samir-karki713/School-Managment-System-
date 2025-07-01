from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models

class AdminSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

class TeacherUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

class TeacherExtraForm(forms.ModelForm):
    class Meta:
        model = models.TeacherExtra
        fields = ['salary', 'mobile', 'status']

class StudentUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

class StudentExtraForm(forms.ModelForm):
    class Meta:
        model = models.StudentExtra
        fields = ['roll', 'mobile', 'fee', 'cl', 'status']

class AttendanceForm(forms.Form):
    date = forms.DateField()

class AskDateForm(forms.Form):
    date = forms.DateField()

class NoticeForm(forms.ModelForm):
    class Meta:
        model = models.Notice
        fields = ['message']

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))
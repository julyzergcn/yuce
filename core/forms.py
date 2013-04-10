from django import forms
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.utils.translation import ugettext_lazy as _

from core.models import *


class UserChangeForm(AuthUserChangeForm):
    class Meta:
        model = User

class UserCreationForm(AuthUserCreationForm):
    class Meta:
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

class TopicCreationForm(forms.Form):
    subject = forms.CharField()
    subject_english = forms.CharField(required=False)
    content = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:400px', 'rows': 4}))
    content_english = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:400px', 'rows': 4}), required=False)
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datetime'}))
    end_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datetime'}))
    yes = forms.BooleanField(required=False)
    coins = forms.IntegerField(min_value=0, required=False)
    
    def save(self, request):
        pass
    

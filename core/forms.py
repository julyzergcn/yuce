from django import forms
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime
from django.forms.extras.widgets import SelectDateWidget

from core.models import User


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
    content = forms.CharField(widget=forms.Textarea)
    content_english = forms.CharField(widget=forms.Textarea, required=False)
    deadline = forms.DateTimeField(widget=AdminSplitDateTime)
    end_date = forms.DateTimeField(widget=AdminSplitDateTime)
    yes = forms.BooleanField(required=False)
    coins = forms.IntegerField(min_value=0, required=False)
    

from django import forms
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.utils.translation import ugettext_lazy as _

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

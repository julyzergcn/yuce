from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _


def update_last_login_ip(sender, request, user, **kwargs):
    '''
    A signal receiver which updates the last_login_ip for
    the user logging in.
    '''
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.save(update_fields=['last_login_ip'])

user_logged_in.connect(update_last_login_ip)

class User(AbstractUser):
    last_login_ip = models.CharField(_('last login ip'), max_length=20)


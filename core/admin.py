from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from core.models import User
from core.forms import UserCreationForm, UserChangeForm


class UserAdmin(AuthUserAdmin):
    list_display = AuthUserAdmin.list_display + ('last_login_ip',)
    form = UserChangeForm
    add_form = UserCreationForm

admin.site.register(User, UserAdmin)

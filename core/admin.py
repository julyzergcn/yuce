from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from core.models import User, Action, Activity, Status, Tag, Topic, Bet
from core.forms import UserCreationForm, UserChangeForm


class UserAdmin(AuthUserAdmin):
    list_display = AuthUserAdmin.list_display + ('last_login_ip', 'coins')
    form = UserChangeForm
    add_form = UserCreationForm

admin.site.register(User, UserAdmin)

admin.site.register(Action,
    list_display = ('short_text', 'text')
)

admin.site.register(Activity)
admin.site.register(Status)
admin.site.register(Tag)
admin.site.register(Topic,
    list_display = ('subject', 'status', 'created_date', 'deadline', 'close_date')
)
admin.site.register(Bet)

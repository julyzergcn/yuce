from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator

from core.models import *
from core.forms import UserCreationForm, UserChangeForm


class UserAdmin(AuthUserAdmin):
    list_display = AuthUserAdmin.list_display + ('score', )
    form = UserChangeForm
    add_form = UserCreationForm

admin.site.register(User, UserAdmin)

def target_field(activity):
    if activity.target is None:
        return ''
    return u'<a href="/admin/%s/%s/%s">%s</a>' % (
        activity.target._meta.app_label,
        activity.target._meta.module_name,
        activity.target.id,
        unicode(activity.target)
    )
target_field.allow_tags = True
target_field.short_description = _('target')

admin.site.register(Activity,
    list_display = ('action_date', 'user', 'action', 'text', target_field),
    list_filter = ('action', )
)

admin.site.register(Tag)

#~ def approve_action(self, request, queryset):
    #~ topic_list = list(queryset)
    #~ for topic in topic_list:
        #~ with transaction.commit_on_success():
            #~ topic.status = 'open'
            #~ topic.save(update_fields=['status'])
            #~ Activity(
                #~ user = request.user,
                #~ action = 'approve topic',
                #~ content_type = ContentType.objects.get_for_model(Topic),
                #~ object_id = topic.id,
            #~ ).save()
#~ approve_action.short_description = _('Approve the selected topics')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'created_date', 'deadline', 'event_close_date', 'complete_date')
    list_editable = ('status', )
    list_filter = ('status', )
    
    @method_decorator(transaction.commit_on_success)
    def save_model(self, request, obj, form, change):
        if change:
            action = 'modify topic'
            original_status = Topic.objects.get(id=obj.id).status
            new_status = obj.status
            if new_status != original_status:
                if original_status == 'pending' and new_status == 'open':
                    action = 'approve topic'
                elif original_status == 'pending' and new_status == 'rejected':
                    action = 'reject topic'
                elif original_status == 'event closed' and new_status == 'completed':
                    action = 'close topic'
                elif new_status == 'cancelled':
                    action = 'cancel topic'
            Activity(
                user = request.user,
                action = action,
                content_type = ContentType.objects.get_for_model(Topic),
                object_id = obj.id,
            ).save()
        obj.save()

admin.site.register(Topic, TopicAdmin)

admin.site.register(Bet,
    list_display = ('created_date', 'user', 'yesno', 'topic', 'score', 'weight'),
)

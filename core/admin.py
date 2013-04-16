from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator

from core.models import *
from core.forms import UserCreationForm, UserChangeForm


#~ admin.site.register(Permission)

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

class TopicAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'created_date', 'deadline', 'event_close_date', 'complete_date')
    list_filter = ('status', )
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TopicAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        request = kwargs.pop("request", None)
        if db_field.name == 'status' and request:
            id = request.path.rsplit('/', 2)[1]
            if id.isdigit():
                current_status = Topic.objects.get(id=id).status
                if current_status == 'pending':
                    formfield.choices = (('pending', _('pending')), ('open', _('open')), ('rejected', _('rejected')),)
                elif current_status == 'open':
                    formfield.choices = (('open', _('open')), ('cancelled', _('cancelled')),)
                else:
                    formfield.choices = ((current_status, _(current_status)),)
        return formfield
    
    def save_form(self, request, form, change):
        return form.save(commit=False)
    
    @method_decorator(transaction.commit_on_success)
    def save_model(self, request, obj, form, change):
        if change:
            action = 'modify topic'
            topic = Topic.objects.get(id=obj.id)
            original_status = topic.status
            new_status = obj.status
            if new_status != original_status:
                if original_status == 'pending' and new_status == 'open':
                    action = 'approve topic'
                elif original_status == 'pending' and new_status == 'rejected':
                    action = 'reject topic'
                    #~ if obj.text == topic.text:
                        #~ raise forms.ValidationError(_('Input why you reject the topic'))
                    # TODO: give back score to the joined users
                
                #~ elif original_status == 'event closed' and new_status == 'completed':
                    #~ action = 'close topic'
                elif new_status == 'cancelled':
                    action = 'cancel topic'
                    #~ if obj.text == topic.text:
                        #~ raise forms.ValidationError(_('Input why you cancel the topic'))
                    # TODO: give back score to the joined users
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

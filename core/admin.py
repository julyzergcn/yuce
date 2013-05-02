from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django import http

from core.models import *
from core.forms import *
from core.util import *

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
    list_display = ('subject', 'status', 'created_date', 'deadline', 'event_close_date', 'complete_date', 'yesno')
    list_filter = ('status', )
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TopicAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        request = kwargs.pop("request", None)
        if request and request.path.rsplit('/', 2)[1].isdigit():
            topic_id = request.path.rsplit('/', 2)[1]
            current_status = Topic.objects.get(id=topic_id).status
            if db_field.name == 'status':
                if current_status == 'pending':
                    formfield.choices = (('pending', _('pending')), ('open', _('open')), ('rejected', _('rejected')),)
                elif current_status == 'open':
                    formfield.choices = (('open', _('open')), ('cancelled', _('cancelled')),)
                else:
                    formfield.choices = ((current_status, _(current_status)),)
            elif db_field.name == 'yesno':
                formfield = MyBooleanField(required=False, label=_('Yes/No'))
                if current_status != 'event closed':
                    formfield.widget.attrs['disabled'] = 'disabled'
                    
        return formfield
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        topic = Topic.objects.select_related().get(id=object_id)
        status = topic.status
        text = topic.text
        yesno = topic.yesno
        if request.method == 'POST':
            new_status = request.POST.get('status')
            new_text = request.POST.get('text')
            new_yesno = request.POST.get('yesno')
            new_yesno = {'1': True, '0': False}.get(new_yesno)
            if status == 'pending' and new_status == 'rejected':
                if new_text == text:
                    self.message_user(request, _('Error! Leave a note why you reject the topic'), level=messages.ERROR)
                    return http.HttpResponseRedirect(request.get_full_path())
            if status != 'cancelled' and new_status == 'cancelled':
                if new_text == text:
                    self.message_user(request, _('Error! Leave a note why you cancel the topic'), level=messages.ERROR)
                    return http.HttpResponseRedirect(request.get_full_path())
            if yesno is None and new_yesno is not None:
                if status == 'event closed':
                    self.should_be_completed = True
                else:
                    self.message_user(request, _('Error! Cannot close the topic'), level=messages.ERROR)
                    return http.HttpResponseRedirect(request.get_full_path())
            elif yesno is not None and new_yesno is not None:
                self.message_user(request, _('Error! Topic was already closed'), level=messages.ERROR)
                return http.HttpResponseRedirect(request.get_full_path())
        return super(TopicAdmin, self).change_view(request, object_id, form_url, extra_context)
    
    @transaction.commit_on_success
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
                    # give back score to the topic submitter
                    give_back_score(obj)
                elif new_status == 'cancelled':
                    action = 'cancel topic'
                    # Not give back score to the joined users
                    #~ give_back_score(obj)
            elif hasattr(self, 'should_be_completed') and self.should_be_completed:
                obj.status = 'completed'
                obj.complete_date = timezone.now()
                action = 'close topic'
                # give divided profit to joined users
                divide_profit(obj)
            
            Activity(
                user = request.user,
                action = action,
                content_type = ContentType.objects.get_for_model(Topic),
                object_id = obj.id,
            ).save()
        
        obj.save()

admin.site.register(Topic, TopicAdmin)

admin.site.register(Bet,
    list_display = ('created_date', 'user', 'yesno', 'topic', 'score', 'weight', 'profit'),
)

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from core.models import *
from core.util import *


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
    tags = forms.CharField(required=False)
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datetime'}))
    close_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datetime'}))
    yes = forms.BooleanField(required=False)
    coins = forms.IntegerField(min_value=0, required=False)
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if tags:
            return tags.split()
        return []
    
    def clean(self):
        data = self.cleaned_data
        if data['deadline'] < timezone.now():
            raise forms.ValidatorError(_('Deadline not valid'))
        if data['close_date'] < data['deadline']:
            raise forms.ValidationError(_('Close data should be after deadline'))
        return data
    
    def save(self, request):
        data = self.cleaned_data
        topic = Topic(
            subject = data['subject'],
            subject_english = data['subject_english'],
            content = data['content'],
            content_english = data['content_english'],
            deadline = data['deadline'],
            close_date = data['close_date'],
            end_weight = getattr(settings, 'TOPIC_END_WEIGHT', 0),
        )
        topic.save()
        for tag in data['tags']:
            a_tag, created = Tag.objects.get_or_create(tag=tag)
            topic.tags.add(a_tag)
        if data['coins'] is not None:
            bet = Bet(
                user = request.user,
                topic = topic,
                coins = data['coins'],
                weight = get_current_weight(topic),
                yesno = data['yes'],
            )
            bet.save()
    

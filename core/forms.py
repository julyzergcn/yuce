from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, decorators
from django.db import transaction
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

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

YESNO_CHOICES = (
    ('1', _('Yes')), 
    ('0', _('No'))
)

class MyBooleanField(forms.BooleanField):
    widget = forms.RadioSelect(choices=YESNO_CHOICES)
    
    def to_python(self, value):
        if str(value).strip() == '0':
            return False
        elif str(value).strip() == '1':
            return True

class TopicCreationForm(forms.Form):
    subject = forms.CharField(label=_('subject'))
    subject_english = forms.CharField(label=_('subject in English'), required=False)
    content = forms.CharField(label=_('content'), widget=forms.Textarea(attrs={'style': 'width:400px', 'rows': 4}))
    content_english = forms.CharField(label=_('content in English'), widget=forms.Textarea(attrs={'style': 'width:400px', 'rows': 4}), required=False)
    tags = forms.MultipleChoiceField(label=_('tags'), widget=forms.CheckboxSelectMultiple, required=False)
    event_close_date = forms.DateTimeField(label=_('event close date'))
    deadline = forms.DateTimeField(label=_('deadline'))
    end_weight = forms.IntegerField(label=_('end weight'), min_value=0, initial=getattr(settings, 'TOPIC_END_WEIGHT', 0))
    yesno = MyBooleanField(label=_('Yes/No'), required=False)
    score = forms.DecimalField(label=_('score'), min_value=0, required=False, max_digits=20, decimal_places=8)
    
    def __init__(self, request=None, **kwargs):
        super(TopicCreationForm, self).__init__(**kwargs)
        self.fields['tags'].choices = [(t.id, t.tag) for t in Tag.objects.all()]
        self.request = request
    
    def clean(self):
        if self.request and self.request.user.is_staff:
            raise forms.ValidationError(_('Admin cannot submit topic'))
        data = self.cleaned_data
        if 'deadline' in data and data['deadline'] < timezone.now():
            raise forms.ValidatorError(_('Deadline is not valid'))
        if 'event_close_date' in data and data['event_close_date'] < data['deadline']:
            raise forms.ValidationError(_('Event close date should be after deadline'))
        if self.request and 'score' in data and data['score'] > self.request.user.score:
            raise forms.ValidationError(_('You donot have enough score to bet'))
        return data
    
    @decorators.method_decorator(transaction.commit_on_success)
    def save(self, request):
        data = self.cleaned_data
        topic = Topic(
            user = request.user,
            subject = data['subject'],
            subject_english = data['subject_english'],
            content = data['content'],
            content_english = data['content_english'],
            deadline = data['deadline'],
            event_close_date = data['event_close_date'],
            end_weight = data['end_weight'],
        )
        topic.save()
        user_pay_topic_post(request.user)
        Activity(
            user = request.user,
            action = 'submit topic',
            content_type = ContentType.objects.get_for_model(Topic),
            object_id = topic.id,
        ).save()
        
        for tag in data['tags']:
            topic.tags.add(tag)
        
        if 'score' in data and 'yesno' in data:
            bet = Bet(
                user = request.user,
                topic = topic,
                score = data['score'],
                weight = get_current_weight(topic),
                yesno = data['yesno'],
            )
            bet.save()
            user_pay_bet(request.user, bet)
            Activity(
                user = request.user,
                action = 'bet',
                content_type = ContentType.objects.get_for_model(Topic),
                object_id = topic.id,
                text = ('yes' if data['yesno'] else 'no') + ' ' + str(data['score'])
            ).save()

class BetForm(forms.Form):
    yesno = MyBooleanField(label=_('Yes/No'))
    score = forms.DecimalField(min_value=0, max_digits=20, decimal_places=8)
    
    def __init__(self, request=None, **kwargs):
        super(BetForm, self).__init__(**kwargs)
        self.request = request
    
    def clean(self):
        if self.request and self.request.user.is_staff:
            raise forms.ValidationError(_('Admin cannot bet'))
        data = self.cleaned_data
        if self.request and 'score' in data and data['score'] > self.request.user.score:
            raise forms.ValidationError(_('You donot have enough score to bet'))
        return data
    
    @decorators.method_decorator(transaction.commit_on_success)
    def save(self, request, topic):
        data = self.cleaned_data
        bet = Bet(
            user = request.user,
            topic = topic,
            score = data['score'],
            weight = get_current_weight(topic),
            yesno = data['yesno'],
        )
        bet.save()
        user_pay_bet(request.user, bet)
        Activity(
            user = request.user,
            action = 'bet',
            content_type = ContentType.objects.get_for_model(Topic),
            object_id = topic.id,
            text = ('yes' if data['yesno'] else 'no') + ' ' + str(data['score'])
        ).save()

    
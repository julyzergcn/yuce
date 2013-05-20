from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import Q

from core.models import User, Topic, Bet, Activity, Tag
from core.util import (get_current_weight, can_bet, pay_bet, pay_topic_post,
                        topic_search_filter)


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


class MyRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        value = {True: '1', False: '0'}.get(value)
        return self.get_renderer(name, value, attrs, choices).render()


class MyBooleanField(forms.BooleanField):
    # widget = MyRadioSelect(choices=YESNO_CHOICES)

    def __init__(self, *args, **kwargs):
        super(MyBooleanField, self).__init__(*args, **kwargs)
        self.widget = MyRadioSelect(choices=YESNO_CHOICES)

    def to_python(self, value):
        if value == '1':
            return True
        elif value == '0':
            return False
        else:
            return None


class TopicCreationForm(forms.Form):
    subject = forms.CharField(label=_('subject'))
    subject_english = forms.CharField(label=_('subject in English'),
                                      required=False)
    content = forms.CharField(label=_('content'),
                              widget=forms.Textarea(attrs={
                                  'style': 'width:400px', 'rows': 4}))
    content_english = forms.CharField(label=_('content in English'),
                                      widget=forms.Textarea(attrs={
                                          'style': 'width:400px', 'rows': 4}),
                                      required=False)
    tags = forms.MultipleChoiceField(label=_('tags'),
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)
    event_close_date = forms.DateTimeField(label=_('event close date'))
    deadline = forms.DateTimeField(label=_('deadline'))
    end_weight = forms.IntegerField(label=_('end weight'), min_value=0,
                                    initial=getattr(
                                        settings, 'TOPIC_END_WEIGHT', 0))
    yesno = MyBooleanField(label=_('Yes/No'), required=False)
    score = forms.DecimalField(label=_('score'), min_value=0, required=False,
                               max_digits=20, decimal_places=8)

    def __init__(self, request=None, **kwargs):
        super(TopicCreationForm, self).__init__(**kwargs)
        self.fields['tags'].choices = [(t.id, t.tag) for t in
                                       Tag.objects.all()]
        self.request = request

    def clean(self):
        data = self.cleaned_data
        if 'deadline' in data and data['deadline'] < timezone.now():
            raise forms.ValidationError(_('Deadline is not valid'))
        if 'event_close_date' in data and \
           data['event_close_date'] < data['deadline']:
            raise forms.ValidationError(
                _('Event close date should be after deadline'))

        if self.request and data.get('yesno') and data.get('score'):
            can, reason = can_bet(self.request.user, bet_score=data['score'])
            if not can:
                raise forms.ValidationError(reason)

        return data

    @transaction.commit_on_success
    def save(self, request):
        data = self.cleaned_data
        topic = Topic(
            user=request.user,
            subject=data['subject'],
            subject_english=data['subject_english'],
            content=data['content'],
            content_english=data['content_english'],
            deadline=data['deadline'],
            event_close_date=data['event_close_date'],
            end_weight=data['end_weight'],
        )
        topic.save()
        pay_topic_post(request.user)
        Activity(
            user=request.user,
            action='submit topic',
            content_type=ContentType.objects.get_for_model(Topic),
            object_id=topic.id,
        ).save()

        for tag in data['tags']:
            topic.tags.add(tag)

        if data.get('yesno') is not None and data.get('score'):
            bet = Bet(
                user=request.user,
                topic=topic,
                score=data['score'],
                weight=get_current_weight(topic),
                yesno=data['yesno'],
            )
            bet.save()
            pay_bet(request.user, bet.score)
            Activity(
                user=request.user,
                action='bet',
                content_type=ContentType.objects.get_for_model(Topic),
                object_id=topic.id,
                text=('yes' if data['yesno'] else 'no') + ' ' +
                str(data['score'])
            ).save()

        return topic


class BetForm(forms.Form):
    yesno = MyBooleanField(label=_('Yes/No'))
    score = forms.DecimalField(min_value=0, max_digits=20, decimal_places=8)

    def __init__(self, request=None, topic=None, **kwargs):
        super(BetForm, self).__init__(**kwargs)
        self.request = request
        self.topic = topic

    def clean(self):
        data = self.cleaned_data
        if self.request:
            can, reason = can_bet(self.request.user, self.topic,
                                  data.get('score'))
            if not can:
                raise forms.ValidationError(reason)

        return data

    @transaction.commit_on_success
    def save(self, request, topic):
        data = self.cleaned_data
        bet = Bet(
            user=request.user,
            topic=topic,
            score=data['score'],
            weight=get_current_weight(topic),
            yesno=data['yesno'],
        )
        bet.save()
        pay_bet(request.user, bet.score)

        Activity(
            user=request.user,
            action='bet',
            content_type=ContentType.objects.get_for_model(Topic),
            object_id=topic.id,
            text=('yes' if data['yesno'] else 'no') + ' ' +
            str(data['score'])
        ).save()


class SearchForm(forms.Form):
    keywords = forms.CharField(label=_('Search'), required=False)
    category = forms.ChoiceField(label=_('Category'), required=False)
    status = forms.ChoiceField(label=_('Status'), required=False,
                               initial='open')

    def __init__(self, **kwargs):
        super(SearchForm, self).__init__(**kwargs)
        self.fields['category'].choices = [('all', _('All'))] + [
            (t.tag, t.tag) for t in Tag.objects.all()]
        self.fields['status'].choices = [('all', _('All')),
                                         ('open', _('open')),
                                         ('deadline', _('deadline')),
                                         ('event closed', _('event closed')),
                                         ('completed', _('completed'))]

    def search(self, user):
        data = self.cleaned_data

        keywords = data.get('keywords', '')
        query = Q()
        for kw in keywords.split():
            query |= Q(subject__icontains=kw)
            query |= Q(subject_english__icontains=kw)
            query |= Q(content__icontains=kw)
            query |= Q(content_english__icontains=kw)

        category = data.get('category', 'all')
        if category != 'all':
            query &= Q(tags__tag=category)

        status = data.get('status', 'open')
        if status != 'all':
            query &= Q(status=status)

        self.search_results = Topic.objects.filter(query)
        self.search_results = topic_search_filter(self.search_results, user)
        return self.search_results


class EmailChangeForm(forms.Form):
    email = forms.EmailField(label=_('New Email'))

    def save(self, user):
        user.email = self.cleaned_data['email']
        user.save(update_fields=['email'])

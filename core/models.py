from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

from core.util import *


class User(AbstractUser):
    score = models.DecimalField(_('score'), max_digits=20, decimal_places=8, default=getattr(settings, 'DEFAULT_USER_SCORE', 1000))
    last_login_ip = models.CharField(max_length=20, blank=True)
    
    @classmethod
    def super_user(cls):
        try:
            return cls.objects.filter(is_superuser=True).order_by('id')[0]
        except IndexError:
            return None

ACTIONS = (
    ('login', _('login')),
    ('change password', _('change password')),
    ('change fund password', _('change fund password')),
    ('change email', _('change email')),
    ('bet', _('bet')),
    ('submit topic', _('submit topic')),
    ('deposit', _('deposit')),
    ('withdraw', _('withdraw')),
    
    # below are for admin user only
    ('approve topic', _('approve topic')),
    ('reject topic', _('reject topic')),
    ('close topic', _('close topic')),
    ('cancel topic', _('cancel topic')),
    ('modify topic', _('modify topic')),
    ('modify user', _('modify user')),
)

class Activity(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=20, choices=ACTIONS)
    action_date = models.DateTimeField(default=timezone.now)
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = generic.GenericForeignKey('content_type', 'object_id')
    
    text = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name_plural = _('Activities')
    
    def __unicode__(self):
        return u'[%s] %s %s %s'%(self.action_date, self.user, _(self.action), self.target or self.text)

def on_user_login(sender, request, user, **kwargs):
    login_ip = request.META.get('REMOTE_ADDR')
    if login_ip != user.last_login_ip:
        user.last_login_ip = login_ip
        user.save(update_fields=['last_login_ip'])
        activity = Activity(user=user, action='login', text=login_ip)
        activity.save()

# when user login, django send out a signal `user_logged_in`, we save the login ip here
user_logged_in.connect(on_user_login)

STATUSES = (
    ('pending', _('pending')),
    ('open', _('open')),
    ('deadline', _('deadline')),
    ('event closed', _('event closed')),
    ('completed', _('completed')),
    ('cancelled', _('cancelled')),
    ('rejected', _('rejected')),
)

class Tag(models.Model):
    tag = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.tag

class Topic(models.Model):
    user = models.ForeignKey(User)
    subject = models.CharField(_('subject'), max_length=200)
    subject_english = models.CharField(_('subject in english'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    content_english = models.TextField(_('content in english'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUSES, default='pending')
    tags = models.ManyToManyField(Tag, null=True, blank=True, verbose_name=_('tags'))
    created_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(_('deadline'))
    event_close_date = models.DateTimeField(_('event close date'))
    complete_date = models.DateTimeField(blank=True, null=True)
    end_weight = models.PositiveIntegerField(_('end weight'))
    text = models.TextField(_('note'), blank=True)
    yesno = models.NullBooleanField(_('Yes/No'), blank=True, null=True)
    
    def __unicode__(self):
        return self.subject
    
    @models.permalink
    def get_absolute_url(self):
        return ('topic_detail', [self.id])
    
    def score_for_bet(self, yesno):
        yesno = True if yesno.lower() == 'yes' else False
        return sum(self.bet_set.filter(yesno=yesno).values_list('score', flat=True))
    
    def yes_score(self):
        return self.score_for_bet('yes')
    
    def no_score(self):
        return self.score_for_bet('no')
    
    def current_weight(self):
        return get_current_weight(self)
    
    def save(self, **kwargs):
        super(Topic, self).save(**kwargs)
        
        if self.event_close_date < timezone.now():
            mark_event_closed(self)
        elif self.deadline < timezone.now():
            mark_deadline(self)
    
    def can_bet(self):
        if self.status != 'open':
            return False, _(self.status)
        
        if self.event_close_date < timezone.now():
            mark_event_closed(self)
            return False, _(self.status)
        elif self.deadline < timezone.now():
            mark_deadline(self)
            return False, _(self.status)
        
        return True, ''
    
    def can_bet_without_reason(self):
        can, reason = self.can_bet()
        return can

class Bet(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
    score = models.DecimalField(_('score'), max_digits=20, decimal_places=8)
    weight = models.PositiveIntegerField(_('weight'))
    yesno = models.BooleanField(_('Yes/No'))
    created_date = models.DateTimeField(default=timezone.now)
    
    def __unicode__(self):
        return u'%s %s %s %s'%(self.user, self.topic, self.yesno, self.score)

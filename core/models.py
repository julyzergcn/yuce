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
    score = models.DecimalField(max_digits=20, decimal_places=8, default=getattr(settings, 'DEFAULT_USER_SCORE', 1000))
    
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
    subject = models.CharField(max_length=200)
    subject_english = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    content_english = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    event_close_date = models.DateTimeField()
    complete_date = models.DateTimeField(blank=True, null=True)
    end_weight = models.PositiveIntegerField()
    
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

class Bet(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
    score = models.DecimalField(max_digits=20, decimal_places=8)
    weight = models.PositiveIntegerField()
    yesno = models.BooleanField()
    created_date = models.DateTimeField(default=timezone.now)
    
    def __unicode__(self):
        return u'%s %s %s %s'%(self.user, self.topic, self.yesno, self.score)

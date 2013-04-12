from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


def update_last_login_ip(sender, request, user, **kwargs):
    '''
    A signal receiver which updates the last_login_ip for
    the user logging in.
    '''
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.save(update_fields=['last_login_ip'])

user_logged_in.connect(update_last_login_ip)

class User(AbstractUser):
    last_login_ip = models.CharField(_('last login ip'), max_length=20)
    coins = models.PositiveIntegerField(default=0)

class Action(models.Model):
    short_text = models.CharField(max_length=20)
    text = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.short_text

class Activity(models.Model):
    user = models.ForeignKey(User)
    action = models.ForeignKey(Action)
    created_date = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = generic.GenericForeignKey('content_type', 'object_id')
    text = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name_plural = _('Activities')
    
    def __unicode__(self):
        return u'[%s]%s %s %s'%(self.date, self.user, self.action.text, self.target or self.text)

###################

class Status(models.Model):
    PENDING = 1
    OPEN = 2
    short_text = models.CharField(max_length=20)
    text = models.CharField(max_length=20)
    
    class Meta:
        verbose_name_plural = _('Statuses')
    
    def __unicode__(self):
        return self.text

class Tag(models.Model):
    tag = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.tag

class Topic(models.Model):
    subject = models.CharField(max_length=200)
    subject_english = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    content_english = models.TextField(blank=True)
    status = models.ForeignKey(Status, default=Status.PENDING)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    close_date = models.DateTimeField()
    end_weight = models.PositiveIntegerField()
    
    def __unicode__(self):
        return self.subject

class Bet(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
    coins = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()
    yesno = models.BooleanField()
    created_date = models.DateTimeField(default=timezone.now)
    status = models.ForeignKey(Status, default=Status.OPEN)
    status_date = models.DateTimeField(default=timezone.now)
    
    def __unicode__(self):
        return u'%s %s'%(self.user, self.topic)

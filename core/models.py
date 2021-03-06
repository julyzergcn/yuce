
import decimal
from jsonrpc.proxy import ServiceProxy
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from core.util import (get_current_weight, mark_deadline, mark_event_closed,
                       site_profit_from_topic, submitter_profit_from_topic)


class User(AbstractUser):
    score = models.DecimalField(_('score'), max_digits=20, decimal_places=8,
                                default=getattr(settings, 'DEFAULT_USER_SCORE',
                                                1000))
    last_login_ip = models.CharField(max_length=20, blank=True)

    @classmethod
    def super_user(cls):
        try:
            return cls.objects.filter(is_superuser=True).order_by('id')[0]
        except IndexError:
            raise ImproperlyConfigured(_('Need at least one super user.'))

    @classmethod
    def score_user(cls):
        try:
            return cls.objects.get(id=2)
        except ObjectDoesNotExist:
            raise ImproperlyConfigured(_('Need at least one score user(id=2).'))
    
    def bitcoin_address(self, username=None):
        s = ServiceProxy(settings.BITCOIN_SERVER_URL)
        lst = s.getaddressesbyaccount(username or self.username)['result']
        if lst: return lst[0]
        return s.getnewaddress(self.username)['result']
    
    def bitcoin_balance(self, username=None):
        s = ServiceProxy(settings.BITCOIN_SERVER_URL)
        balance = s.getbalance(username or self.username)['result']
        
        # force set score == balance
        if username is None:
            self.score = balance
            self.save(update_fields=['score'])
        
        return balance
    
    def bitcoin_pay(self, amount=0.0, frm=None, to=None):
        s = ServiceProxy(settings.BITCOIN_SERVER_URL)
        to_address = self.bitcoin_address(to)
        if isinstance(amount, decimal.Decimal):
            amount = float(amount)
        return s.sendfrom(frm or self.username, to_address, amount)['result']
    
    def bitcoin_withdraw(self, addr):
        s = ServiceProxy(settings.BITCOIN_SERVER_URL)
        return s.sendfrom(self.username, addr, self.bitcoin_balance())

ACTIONS = (
    ('login', _('login')),
    ('change password', _('change password')),
    ('change fund password', _('change fund password')),
    ('change email', _('change email')),
    ('bet', _('bet')),
    ('submit topic', _('submit topic')),
    ('deposit', _('deposit')),
    ('withdraw', _('withdraw')),

    # for admins
    ('approve topic', _('approve topic')),
    ('reject topic', _('reject topic')),
    ('close topic', _('close topic')),
    ('cancel topic', _('cancel topic')),
    ('change deadline', _('change deadline')),
    ('modify topic', _('modify topic')),
    ('modify user', _('modify user')),

    # for users
    ('topic is rejected', _('topic is rejected')),
    ('bet is rejected', _('bet is rejected')),
    ('topic is cancelled', _('topic is cancelled')),
    ('bet is cancelled', _('bet is cancelled')),
    ('submitter win', _('submitter win')),
    ('topic is completed', _('topic is completed')),
    ('bet is completed', _('bet is completed')),
    ('bet deadline is changed', _('bet deadline is changed')),
)


class Activity(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=20, choices=ACTIONS)
    action_date = models.DateTimeField(default=timezone.now)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = generic.GenericForeignKey('content_type', 'object_id')

    text = models.CharField(max_length=200, blank=True)
    score = models.DecimalField(_('score'), max_digits=20, decimal_places=8,
                                default=0)
    current_score = models.DecimalField(_('score'), max_digits=20,
                                decimal_places=8, default=0)

    class Meta:
        verbose_name_plural = _('Activities')

    def __unicode__(self):
        return u'[%s] %s %s %s' % (self.action_date,
                                   self.user,
                                   _(self.action),
                                   self.target or self.text)

    def save(self, **kwargs):
        if self.score != 0:
            self.current_score = self.user.score
        super(Activity, self).save(**kwargs)


def on_user_login(sender, request, user, **kwargs):
    login_ip = request.META.get('REMOTE_ADDR')
    if login_ip != user.last_login_ip:
        user.last_login_ip = login_ip
        user.save(update_fields=['last_login_ip'])
        activity = Activity(user=user, action='login', text=login_ip)
        activity.save()

# when user login, django send out a signal `user_logged_in`,
# we save the login ip here
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
    user = models.ForeignKey(User, verbose_name=_('Submitter'))
    subject = models.CharField(_('subject'), max_length=200)
    subject_english = models.CharField(_('subject in english'),
                                       max_length=200, blank=True)
    content = models.TextField(_('content'))
    content_english = models.TextField(_('content in english'), blank=True)
    status = models.CharField(_('status'), max_length=20,
                              choices=STATUSES, default='pending')
    tags = models.ManyToManyField(Tag, null=True, blank=True,
                                  verbose_name=_('tags'))

    created_date = models.DateTimeField(default=timezone.now)    # then pending
    approved_date = models.DateTimeField(blank=True, null=True)   # then open
    rejected_date = models.DateTimeField(blank=True, null=True)
    cancelled_date = models.DateTimeField(blank=True, null=True)

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
        return sum(self.bet_set.filter(yesno=yesno)
                   .values_list('score', flat=True))

    def yes_score(self):
        return self.score_for_bet('yes')

    def no_score(self):
        return self.score_for_bet('no')

    def yes_score_plus_weight(self):
        return sum([b.score * b.weight for b in
                    self.bet_set.filter(yesno=True)])

    def no_score_plus_weight(self):
        return sum([b.score * b.weight for b in
                    self.bet_set.filter(yesno=False)])

    def bet_score(self):
        return self.yes_score() + self.no_score()

    def current_weight(self):
        return get_current_weight(self)

    def save(self, **kwargs):
        super(Topic, self).save(**kwargs)
        self.update_status(for_save_method=True)

    def update_status(self, for_save_method=False):
        if self.status in ('open', 'deadline'):
            if self.event_close_date < timezone.now():
                mark_event_closed(self)
            elif self.deadline < timezone.now():
                if self.status == 'open':
                    mark_deadline(self)
            elif for_save_method:
                mark_deadline.apply_async((self, ), eta=self.deadline)
                mark_event_closed.apply_async((self, ),
                                              eta=self.event_close_date)

    def can_bet(self):
        self.update_status()
        return (True, '') if self.status == 'open' else(False, _(self.status))

    def can_bet_without_reason(self):
        can, reason = self.can_bet()
        return can

    def site_profit(self):
        if self.status == 'completed':
            return site_profit_from_topic(self)
        return 0

    def submitter_profit(self):
        if self.status == 'completed':
            profit = submitter_profit_from_topic(self)
            return float('%.2f' % profit)
        return 0

    def yes_bets_score(self):
        return sum(self.bet_set.filter(yesno=True).values_list('score',
                                                               flat=True))

    def no_bets_score(self):
        return sum(self.bet_set.filter(yesno=False).values_list('score',
                                                                flat=True))

    def submitter_win_rate(self):
        return getattr(settings, 'SUBMITTER_WIN_RATE', 0.1)


class Bet(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
    score = models.DecimalField(_('score'), max_digits=20, decimal_places=8)
    weight = models.PositiveIntegerField(_('weight'))
    yesno = models.BooleanField(_('Yes/No'))
    created_date = models.DateTimeField(default=timezone.now)
    profit = models.DecimalField(_('profit'), max_digits=20, decimal_places=8,
                                 default=0)

    def __unicode__(self):
        return u'%s(%s%s)' % (self.topic, ('Y' if self.yesno else 'N'),
                    self.score)

    def weight_all(self):
        return self.weight * self.score

    def pay_back_score(self):
        if self.topic.status=='completed' and self.yesno==self.topic.yesno:
            return self.profit + self.score
        return 0

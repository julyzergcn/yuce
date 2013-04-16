from django.conf import settings
from django.utils import timezone
from django.db import transaction, models
from django.utils.translation import ugettext_lazy as _


seconds_delta = lambda time_delta: time_delta.days * 86400 + time_delta.seconds
minutes_delta = lambda time_delta: seconds_delta(time_delta) / 60

def get_current_weight(topic):
    if timezone.now() > topic.deadline:
        # if time is over deadline, the weight should be zero
        return 0
    start_weight = getattr(settings, 'TOPIC_START_WEIGHT', 100000)
    end_weight = topic.end_weight
    time_delta1 = minutes_delta(topic.deadline - timezone.now())
    time_delta2 = minutes_delta(topic.deadline - topic.created_date)
    current_weight = (start_weight - end_weight) * time_delta1 * 1.0 / time_delta2 + end_weight
    return int(current_weight)

def can_post_topic(user):
    if user.is_staff:
        return False, _('Admin cannot submit topic')
    if user.score < getattr(settings, 'TOPIC_SUBMITTED_COST', 10):
        return False, _('No enough score to post topic')
    return True, ''

def pay_topic_post(user):
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    if user.score > cost:
        with transaction.commit_on_success():
            # user pay the cost
            user.score -= cost
            user.save(update_fields=['score'])
            
            # the super user(site super admin) earn the cost
            super_user = models.get_model('core', 'User').super_user()
            super_user.score += cost
            super_user.save(update_fields=['score'])
        return cost
    return 0

def can_bet(user, topic=None, bet_score=None):
    if user.is_staff:
        return False, _('Admin cannot bet')
    if bet_score and user.score < bet_score:
        return False, _('No enough score to bet')
    if topic:
        can, reason = topic.can_bet()
        if not can:
            return False, reason
    return True, ''

def pay_bet(user, bet_score):
    if user.score > bet_score:
        with transaction.commit_on_success():
            user.score -= bet_score
            user.save(update_fields=['score'])
            
            super_user = models.get_model('core', 'User').super_user()
            super_user.score += bet_score
            super_user.save(update_fields=['score'])
    return 0

def mark_deadline(topic):
    if topic.status != 'open':
        return
    topic.status = 'deadline'
    topic.save(update_fields=['status'])

def mark_event_closed(topic):
    if topic.status not in ('open', 'deadline'):
        return
    topic.status = 'event closed'
    topic.save(update_fields=['status'])
    # TODO: send alert email to admin(s)

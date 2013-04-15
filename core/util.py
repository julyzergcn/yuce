from django.conf import settings
from django.utils import timezone
from django.db import transaction, models


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

def user_can_post_topic(user):
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    if user.score > cost:
        return True
    return False

def user_pay_topic_post(user):
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

def user_pay_bet(user, bet):
    bet_score = bet.score
    if user.score > bet_score:
        with transaction.commit_on_success():
            user.score -= bet_score
            user.save(update_fields=['score'])
            
            super_user = models.get_model('core', 'User').super_user()
            super_user.score += bet_score
            super_user.save(update_fields=['score'])
    return 0


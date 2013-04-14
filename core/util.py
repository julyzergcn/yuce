from django.conf import settings
from django.utils import timezone

seconds = lambda delta: delta.days * 86400 + delta.seconds
minutes = lambda delta: seconds(delta) / 60

def get_current_weight(topic):
    if topic.deadline < timezone.now():
        return 0
    start_weight = getattr(settings, 'TOPIC_START_WEIGHT', 10**5)
    end_weight = topic.end_weight
    time_delta1 = minutes(topic.deadline - timezone.now())
    time_delta2 = minutes(topic.deadline - topic.created_date)
    current_weight = (start_weight - end_weight) * time_delta1 * 1.0 / time_delta2 + end_weight
    return int(current_weight)

def user_can_post_topic(user):
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    if user.coins > cost:
        return True
    return False

def user_pay_topic_post(user):
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    if user.coins > cost:
        user.coins -= cost
        #TODO: our site earn this cost, how?
        return cost
    return 0

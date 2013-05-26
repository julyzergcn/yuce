from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction, models
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from celery import task


seconds_delta = lambda time_delta: time_delta.days * 86400 + time_delta.seconds
minutes_delta = lambda time_delta: seconds_delta(time_delta) / 60


def get_super_user():
    return models.get_model('core', 'User').super_user()


def get_score_user():
    return models.get_model('core', 'User').score_user()


def get_current_weight(topic):
    if timezone.now() > topic.deadline:
        # if time is over deadline, the weight should be zero
        return 0
    start_weight = getattr(settings, 'TOPIC_START_WEIGHT', 100000)
    end_weight = topic.end_weight
    time_delta1 = minutes_delta(topic.deadline - timezone.now())
    time_delta2 = minutes_delta(topic.deadline - topic.created_date)
    if time_delta2 == 0:
        time_delta2 = 1
    current_weight = (start_weight - end_weight) * (time_delta1 * 1.0 /
                                                    time_delta2 + end_weight)
    return int(current_weight)


def can_post_topic(user):
    if user.is_staff:
        return False, _('Admin cannot submit topic')
    if user.score < getattr(settings, 'TOPIC_SUBMITTED_COST', 10):
        return False, _('No enough score to post topic')
    return True, ''


VIEWABLE_STATUSES = ('open', 'deadline', 'event closed',
                     'completed', 'cancelled')


def can_view_topic(topic, user):
    if topic.user == user or user.is_staff:
        return True
    else:
        if topic.status in VIEWABLE_STATUSES:
            return True
    return False


def topic_search_filter(queryset, user):
    if user.is_staff:
        return queryset
    query = Q(user__pk=user.pk)
    query |= Q(status__in=VIEWABLE_STATUSES)
    return queryset.filter(query)


def pay_topic_post(topic):
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    user = topic.user
    if user.score > cost:
        with transaction.commit_on_success():
            # user pay the cost
            user.score -= cost
            user.save(update_fields=['score'])

            # site(super user) get the cost
            super_user = get_super_user()
            super_user.score += cost
            super_user.save(update_fields=['score'])

            models.get_model('core', 'Activity')(
                user=user,
                action = 'submit topic',
                content_type=ContentType.objects.get_by_natural_key(
                    'core', 'topic'),
                object_id=topic.id,
                score=-cost,
            ).save()
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


def pay_bet(bet):
    user = bet.user
    bet_score = bet.score
    if user.score > bet_score:
        with transaction.commit_on_success():
            user.score -= bet_score
            user.save(update_fields=['score'])

            score_user = get_score_user()
            score_user.score += bet_score
            score_user.save(update_fields=['score'])

            models.get_model('core', 'Activity')(
                user=user,
                action = 'bet',
                content_type=ContentType.objects.get_by_natural_key(
                    'core', 'bet'),
                object_id=bet.id,
                text='yes' if bet.yesno else 'no',
                score=-bet_score,
            ).save()
        return bet_score
    return 0


@task
def send_event_closed_emails(topic):
    if topic.status != 'event closed':
        return
    recipient_list = getattr(settings, 'TOPIC_EVENT_CLOSED_EMAILS', [])
    recipient_list.insert(0, settings.DEFAULT_FROM_EMAIL)
    from_email = settings.DEFAULT_FROM_EMAIL
    domain = Site.objects.get_current().domain
    subject = _('Event closed') + ': ' + topic.subject
    message = subject + '\n\n' + 'http://%s/admin/core/topic/%s/' % (
        domain, topic.id)
    send_mail(subject, message, from_email, recipient_list)


@task
def mark_deadline(topic):
    if topic.status == 'open':
        topic.status = 'deadline'
        topic.save(update_fields=['status'])


@task
def mark_event_closed(topic):
    if topic.status in ('open', 'deadline'):
        topic.status = 'event closed'
        topic.save(update_fields=['status'])
        send_event_closed_emails.delay(topic)


def divide_profit(topic):
    all_bets = models.get_model('core', 'Bet').objects.filter(topic=topic)
    yesno = topic.yesno
    win_bets = all_bets.filter(yesno=yesno)
    lose_bets = all_bets.filter(yesno=(not yesno))
    lose_bets_score = sum(lose_bets.values_list('score', flat=True))

    # submitter profit
    submitter_win_rate = Decimal(getattr(settings, 'SUBMITTER_WIN_RATE', 0.1))
    submitter = topic.user
    submitter_profit = lose_bets_score * submitter_win_rate
    submitter.score += submitter_profit
    models.get_model('core', 'Activity')(
        user=submitter,
        action = 'submitter win',
        content_type=ContentType.objects.get_by_natural_key('core', 'topic'),
        object_id=topic.id,
        score=submitter_profit,
    ).save()

    # submitter post cost back
    topic_submitted_cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    submitter.score += topic_submitted_cost
    submitter.save(update_fields=['score'])
    models.get_model('core', 'Activity')(
        user=submitter,
        action = 'topic is completed',
        content_type=ContentType.objects.get_by_natural_key('core', 'topic'),
        object_id=topic.id,
        score=topic_submitted_cost,
    ).save()

    # site(super user)
    super_user = get_super_user()
    super_user.score -= topic_submitted_cost

    site_win_rate = Decimal(getattr(settings, 'SITE_WIN_RATE', 0.1))
    site_profit = lose_bets_score * site_win_rate
    super_user.score += site_profit
    super_user.save(update_fields=['score'])

    # score_user pay back to submitter and site
    score_user = get_score_user()
    score_user.score -= submitter_profit
    score_user.score -= site_profit

    # all winners profit
    all_profit = lose_bets_score - submitter_profit - site_profit
    all_bet_weight = sum([b.score * b.weight for b in all_bets])
    for bet in win_bets:
        bet.profit = all_profit * bet.score * bet.weight / all_bet_weight
        bet.save(update_fields=['profit'])
        winner = bet.user
        winner.score += bet.profit
        winner.score += bet.score
        winner.save(update_fields=['score'])
        models.get_model('core', 'Activity')(
            user=winner,
            action = 'bet is completed',
            content_type=ContentType.objects.get_by_natural_key(
                'core', 'bet'),
            object_id=bet.id,
            score=bet.profit + bet.score,
        ).save()

        score_user.score -= bet.profit
        score_user.score -= bet.score

    score_user.save(update_fields=['score'])


def site_profit_from_topic(topic):
    bets = models.get_model('core', 'Bet').objects.filter(topic=topic)
    lose_bets = bets.filter(yesno=(not topic.yesno))
    lose_bets_score = sum(lose_bets.values_list('score', flat=True))
    site_win_rate = Decimal(getattr(settings, 'SITE_WIN_RATE', 0.1))
    return lose_bets_score * site_win_rate


def submitter_profit_from_topic(topic):
    bets = models.get_model('core', 'Bet').objects.filter(topic=topic)
    lose_bets = bets.filter(yesno=(not topic.yesno))
    lose_bets_score = sum(lose_bets.values_list('score', flat=True))
    submitter_win_rate = Decimal(getattr(settings, 'SUBMITTER_WIN_RATE', 0.1))
    return lose_bets_score * submitter_win_rate


def reject_topic(topic):
    '''give back scores(submitted & betted score) to the topic submitter'''
    submitter = topic.user
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    super_user = get_super_user()
    score_user = get_score_user()
    with transaction.commit_on_success():
        submitter.score += cost
        submitter.save(update_fields=['score'])

        models.get_model('core', 'Activity')(
            user=submitter,
            action = 'topic is rejected',
            content_type=ContentType.objects.get_by_natural_key(
                'core', 'topic'),
            object_id=topic.id,
            score=cost,
        ).save()

        super_user.score -= cost
        super_user.save(update_fields=['score'])
        for bet in models.get_model('core', 'Bet').objects.filter(topic=topic):
            assert bet.user == submitter, 'bet user should be submitter'
            bet_score = bet.score
            submitter.score += bet_score
            submitter.save(update_fields=['score'])

            models.get_model('core', 'Activity')(
                user=submitter,
                action = 'bet is rejected',
                content_type=ContentType.objects.get_by_natural_key(
                    'core', 'bet'),
                object_id=bet.id,
                score=bet_score,
            ).save()

            score_user.score -= bet_score
            score_user.save(update_fields=['score'])


def cancel_topic(topic):
    '''give back score to the betted users'''
    submitter = topic.user
    cost = getattr(settings, 'TOPIC_SUBMITTED_COST', 10)
    super_user = get_super_user()
    score_user = get_score_user()
    with transaction.commit_on_success():
        submitter.score += cost
        submitter.save(update_fields=['score'])

        models.get_model('core', 'Activity')(
            user=submitter,
            action = 'topic is cancelled',
            content_type=ContentType.objects.get_by_natural_key(
                'core', 'topic'),
            object_id=topic.id,
            score=cost,
        ).save()

        super_user.score -= cost
        super_user.save(update_fields=['score'])
        for bet in models.get_model('core', 'Bet').objects.filter(topic=topic):
            bet_score = bet.score
            bet.user.score += bet_score
            bet.user.save(update_fields=['score'])

            models.get_model('core', 'Activity')(
                user=submitter,
                action = 'bet is cancelled',
                content_type=ContentType.objects.get_by_natural_key(
                    'core', 'bet'),
                object_id=bet.id,
                score=bet_score,
            ).save()

            score_user.score -= bet_score
            score_user.save(update_fields=['score'])


# TODO: regenerate weight
def change_deadline(topic):
    pass

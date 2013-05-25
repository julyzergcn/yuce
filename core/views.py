from django.shortcuts import render, redirect, get_object_or_404
from django import http
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from core.models import Topic, Bet, User
from core.forms import BetForm, TopicCreationForm, SearchForm, EmailChangeForm
from core.util import can_post_topic, can_view_topic


def index(request):
    open_topics = Topic.objects.filter(status='open')
    hot_topics = sorted(list(open_topics), key=lambda t: t.bet_score(),
                        reverse=True)
    context = {
        'deadline_topics': open_topics.order_by('deadline'),
        'hot_topics': hot_topics,
        'new_topics': open_topics.order_by('-created_date'),
        'new_bets': Bet.objects.filter(topic__status='open'
                                       ).order_by('-created_date'),
        'profit_bets': Bet.objects.all().order_by('-profit').exclude(profit=0),
    }
    return render(request, 'index.html', context)


def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
    if not can_view_topic(topic, request.user):
        raise http.Http404
    if request.method == 'POST':
        form = BetForm(data=request.POST, request=request, topic=topic)
        if form.is_valid():
            form.save(request, topic)
            return redirect('topic_detail', id)
    else:
        form = BetForm(request=request, topic=topic)
    context = {
        'topic': topic,
        'form': form,
    }
    return render(request, 'core/topic_detail.html', context)


@login_required
def new_topic(request):
    can, reason = can_post_topic(request.user)
    if not can:
        messages.error(request, reason)
        return redirect('home')
    if request.method == 'POST':
        form = TopicCreationForm(data=request.POST, request=request)
        if form.is_valid():
            topic = form.save(request)
            return redirect('topic_detail', topic.id)
    else:
        form = TopicCreationForm(request=request)
    context = {
        'form': form
    }
    return render(request, 'core/new_topic.html', context)


def archived_topics(request):
    topics = Topic.objects.filter(status='completed')

    order = request.REQUEST.get('o', 'desc')
    column = request.REQUEST.get('c', 'cd')
    if column == 'bt':  # bet scores
        topics = sorted(list(topics),
                        key=lambda t: t.bet_score(),
                        reverse={'asc': False, 'desc': True}.get(order, True))
    else:
        order_by = {'asc': '', 'desc': '-'}.get(order, '-') + {
            'cd': 'created_date',
            'dd': 'deadline',
            'ed': 'event_close_date'
        }.get(column, 'created_date')
        topics = topics.order_by(order_by)

    context = {
        'topics': topics,
        'o': {'asc': 'desc', 'desc': 'asc'}.get(order, 'desc'),
        'c': column,
        'arrow': {'asc': '&uarr;', 'desc': '&darr;'}.get(order, '&darr;'),
    }
    return render(request, 'core/archived_topics.html', context)


def search(request):
    context = {
        'form': search_form(request),
    }
    return render(request, 'core/search.html', context)


@csrf_exempt
def search_form(request):
    form = SearchForm(request)
    if form.is_valid():
        form.search()
    return form


def dumpdata(request):
    response = http.HttpResponse()
    response['Content-Type'] = 'text/plain; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=dump.json'
    lst = []
    for model in (User, Topic, Bet):
        lst += list(model.objects.all())
    json = serialize('json', lst, indent=4)
    response.write(json)
    return response




@login_required
def profile_info(request):
    user = request.user
    password_form = PasswordChangeForm(user)
    email_form = EmailChangeForm(user)

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _('Password is changed'))
                return redirect('profile_info')
        elif 'change_email' in request.POST:
            email_form = EmailChangeForm(user, data=request.POST)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, _('Email is changed'))
                return redirect('profile_info')

    context = {
        'user': user,
        'password_form': password_form,
        'email_form': email_form,
    }
    return render(request, 'profile/profile_info.html', context)


@login_required
def profile_topics(request):
    status = request.REQUEST.get('status', 'pending')
    template_name = 'profile/topics/%s.html' % status
    context = {
        'form': search_form(request),
    }
    return render(request, template_name, context)


def profile_bets(request):
    query = Q()
    if request.REQUEST.get('kw'):
        for kw in request.REQUEST['kw'].strip().split():
            query |= Q(topic__subject__icontains=kw)
            query |= Q(topic__subject_english__icontains=kw)
            query |= Q(topic__content__icontains=kw)
            query |= Q(topic__content_english__icontains=kw)
            query |= Q(topic__id=kw)
            query |= Q(id=kw)
    query &= Q(user=request.user)
    return Bet.objects.filter(query).order_by('-id')


@login_required
def profile_bets_open(request):
    bets = profile_bets(request).filter(topic__status='open')
    return render(request, 'profile/bets/open.html', {'bets': bets})


@login_required
def profile_bets_closed(request):
    bets = profile_bets(request).filter(topic__status='deadline')
    return render(request, 'profile/bets/deadline.html', {'bets': bets})


@login_required
def profile_bets_completed(request):
    bets = profile_bets(request).filter(topic__status='completed')
    return render(request, 'profile/bets/completed.html', {'bets': bets})


@login_required
def profile_score(request):
    pass

from django.shortcuts import render, redirect, get_object_or_404
from django import http
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.contrib.auth.forms import PasswordChangeForm

from core.models import Topic, Bet, User
from core.forms import BetForm, TopicCreationForm, SearchForm, EmailChangeForm
from core.utils import can_post_topic


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


def topic_list(request):
    context = {
        'topics': Topic.objects.filter(status='open'),
    }
    return render(request, 'core/topic_list.html', context)


def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
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
    if request.method == 'POST':
        form = SearchForm(data=request.POST)
        if form.is_valid():
            topics = form.search()
    else:
        form = SearchForm()
        topics = Topic.objects.filter(status='open')

    order = request.REQUEST.get('o', 'desc')
    column = request.REQUEST.get('c', 'cd')
    if column == 'bt':  # bet scores
        topics = sorted(list(topics), key=lambda t: t.bet_score(), reverse={
            'asc': False, 'desc': True}.get(order, True))
    else:
        order_by = {'asc': '', 'desc': '-'}.get(order, '-') + {
            'cd': 'created_date',
            'dd': 'deadline',
            'ed': 'event_close_date'
        }.get(column, 'created_date')
        topics = topics.order_by(order_by)

    context = {
        'form': form,
        'topics': topics,
        'o': {'asc': 'desc', 'desc': 'asc'}.get(order, 'desc'),
        'c': column,
        'arrow': {'asc': '&uarr;', 'desc': '&darr;'}.get(order, '&darr;'),
    }
    return render(request, 'core/search.html', context)


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
def profile(request):
    if request.method == 'POST':
        if request.POST.get('change_type') == 'email':
            email_form = EmailChangeForm(request.POST)
            password_form = PasswordChangeForm(request.user)
            if email_form.is_valid():
                email_form.save(request.user)
                messages.success(request, _('Email is changed'))
                return redirect('my_profile')
        elif request.POST.get('change_type') == 'password':
            email_form = EmailChangeForm(initial={'email': request.user.email})
            password_form = PasswordChangeForm(request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _('password is changed'))
                return redirect('my_profile')
    else:
        email_form = EmailChangeForm(initial={'email': request.user.email})
        password_form = PasswordChangeForm(request.user)
    context = {
        'email_form': email_form,
        'password_form': password_form,
        'my_topics': Topic.objects.filter(user=request.user),
        'my_bets': Bet.objects.filter(user=request.user),
    }
    return render(request, 'core/profile.html', context)

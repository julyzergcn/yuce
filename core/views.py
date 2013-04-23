from django.shortcuts import render, redirect, get_object_or_404
from django import http
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

from core.models import *
from core.forms import *
from core.util import *


def index(request):
    open_topics = Topic.objects.filter(status='open')
    hot_topics = sorted(list(open_topics), key=lambda t: t.bet_score(), reverse=True)
    context = {
        'deadline_topics': open_topics.order_by('deadline'),
        'hot_topics': hot_topics,
        'new_topics': open_topics.order_by('-created_date'),
        'new_bets': Bet.objects.filter(topic__status='open').order_by('-created_date'),
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
    context = {
        'topics': Topic.objects.filter(status='completed'),
    }
    return render(request, 'core/archived_topics.html', context)

def search(request):
    return redirect('home')

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

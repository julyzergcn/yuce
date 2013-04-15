from django.shortcuts import render, redirect, get_object_or_404
from django import http
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from core.models import *
from core.forms import *
from core.util import *


def index(request):
    return render(request, 'index.html')

def topic_list(request):
    context = {
        'topics': Topic.objects.filter(status='open'),
    }
    return render(request, 'core/topic_list.html', context)

def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
    if request.method == 'POST':
        form = BetForm(data=request.POST, request=request)
        if form.is_valid():
            form.save(request, topic)
            return redirect('topic_list')
    else:
        form = BetForm(request=request)
    context = {
        'topic': topic,
        'form': form,
    }
    return render(request, 'core/topic_detail.html', context)

@login_required
def new_topic(request):
    if not user_can_post_topic(request.user):
        messages.error(request, _(u'You do not have enough score to post topic'))
        return redirect('home')
    if request.method == 'POST':
        form = TopicCreationForm(data=request.POST, request=request)
        if form.is_valid():
            form.save(request)
            return redirect('home')
    else:
        form = TopicCreationForm(request=request)
    context = {
        'form': form,
        'tags': Tag.objects.all(),
    }
    return render(request, 'core/new_topic.html', context)

def archived_topics(request):
    context = {
        'topics': Topic.objects.filter(status='completed'),
    }
    return render(request, 'core/archived_topics.html', context)

def search(request):
    return redirect('home')

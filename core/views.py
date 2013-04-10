from django.shortcuts import render
from django import http

from core.models import *
from core.forms import *


def index(request):
    return render(request, 'index.html')

def topics(request):
    return render(request, 'core/topics.html')

def new_topic(request):
    if request.method == 'POST':
        form = TopicCreationForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
    else:
        form = TopicCreationForm()
    context = {
        'form': form,
        'tags': Tag.objects.all(),
    }
    return render(request, 'core/new_topic.html', context)

def archived_topics(request):
    return render(request, 'core/archived_topics.html')

def search(request):
    return http.HttpResponseRedirect('/')

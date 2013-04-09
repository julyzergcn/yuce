from django.shortcuts import render
from django import http


def index(request):
    return render(request, 'index.html')

def topics(request):
    return render(request, 'core/topics.html')

def new_topic(request):
    return render(request, 'core/new_topic.html')

def archived_topics(request):
    return render(request, 'core/archived_topics.html')

def search(request):
    return http.HttpResponseRedirect('/')

from django.conf.urls import patterns, include, url


urlpatterns = patterns('core.views',
    url(r'^$', 'index', name='home'),
    url(r'^topics/$', 'topics', name='topics'),
    url(r'^topics/new/$', 'new_topic', name='new_topic'),
    url(r'^topics/archived/$', 'archived_topics', name='archived_topics'),
    url(r'^search/$', 'search', name='search'),
    
)

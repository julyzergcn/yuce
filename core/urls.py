from django.conf.urls import patterns, include, url


urlpatterns = patterns('core.views',
    url(r'^$', 'index', name='home'),
    url(r'^topic/$', 'topic_list', name='topic_list'),
    url(r'^topic/(\d+)/$', 'topic_detail', name='topic_detail'),
    url(r'^topic/new/$', 'new_topic', name='new_topic'),
    url(r'^topic/archived/$', 'archived_topics', name='archived_topics'),
    url(r'^search/$', 'search', name='search'),
    url(r'^dumpdata/$', 'dumpdata'),
)

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'core.views',
    url(r'^$', 'index', name='home'),
    url(r'^topic/$', 'search', name='topic_list'),
    url(r'^topic/(\d+)/$', 'topic_detail', name='topic_detail'),
    url(r'^topic/new/$', 'new_topic', name='new_topic'),
    url(r'^topic/archived/$', 'archived_topics', name='archived_topics'),
    url(r'^search/$', 'search', name='search'),

    # for backup data
    #~ url(r'^dumpdata/$', 'dumpdata'),

    #~ url(r'^accounts/profile/$', 'profile', name='my_profile'),
    url(r'^accounts/profile/$', 'profile_info', name='my_profile'),
    url(r'^accounts/profile/info/$', 'profile_info', name='profile_info'),
    url(r'^accounts/profile/topics/$', 'profile_topics',
        name='profile_topics'),
    url(r'^accounts/profile/bets/$', 'profile_bets', name='profile_bets'),
    url(r'^accounts/profile/score/$', 'profile_score', name='profile_score'),
)

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    
    url(r'^accounts/', include('registration.backends.default.urls')),
    #~ url(r'^accounts/profile/$', RedirectView.as_view(url='/'), name='my_profile'),
    
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'), name='contact'),
    url(r'^faq/$', TemplateView.as_view(template_name='faq.html'), name='faq'),
    
    url(r'^', include('core.urls')),
)

from django.conf import settings as s

urlpatterns += patterns('django.views.static',
    (r'^static/(?P<path>.*)$', 'serve', {'document_root': s.STATIC_ROOT}),
    (r'^media/(?P<path>.*)$', 'serve', {'document_root': s.MEDIA_ROOT}),
)

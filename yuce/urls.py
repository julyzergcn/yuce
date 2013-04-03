from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/')),
    url(r'^$', 'core.views.index', name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'), name='contact'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

from django.conf import settings as s

urlpatterns += patterns('django.views.static',
    (r'^static/(?P<path>.*)$', 'serve', {'document_root': s.STATIC_ROOT}),
    (r'^media/(?P<path>.*)$', 'serve', {'document_root': s.MEDIA_ROOT}),
)

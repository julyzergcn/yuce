from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'),
        name='contact'),
    url(r'^faq/$', TemplateView.as_view(template_name='faq.html'), name='faq'),

    url(r'^', include('core.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

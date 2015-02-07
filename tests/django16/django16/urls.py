from django.conf.urls import patterns, include, url

from django.contrib import admin

import test_app.views

admin.autodiscover()


urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', test_app.views.index),
)

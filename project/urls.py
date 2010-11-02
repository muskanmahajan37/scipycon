from django.conf import settings
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to


admin.autodiscover()

PROGRAM_PATTERN_CORE = r'[a-z](?:[0-9a-z]|_[0-9a-z])*'
EVENT_PATTERN_CORE =r'(?:[0-9a-z]|_[0-9a-z])*' 
SCOPE_ARG_PATTERN = r'(?P<scope>%s/%s)' % (
    PROGRAM_PATTERN_CORE, EVENT_PATTERN_CORE) 

sitemaps = {}

# Admin
urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^robots\.txt$', include('robots.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^$', redirect_to, {'url': '/%s/' % (settings.CURRENT_SCOPE)}),
    url(r'^%s/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "home.html"}, name='home'),
)

# Talks, etc.
urlpatterns += patterns('project.scipycon.talk.views',
    url(r'^%s/talks/$' % (SCOPE_ARG_PATTERN),
        'list_talks', name='list_talks'),
    url(r'^%s/my-talks/$' % (SCOPE_ARG_PATTERN),
        'list_my_talks', name='list_my_talks'),
    url(r'^%s/talks/talk/(?P<id>\d+)/$' % (SCOPE_ARG_PATTERN),
        'talk', name='talk_detail'),
    url(r'^%s/submit-talk/$' % (SCOPE_ARG_PATTERN),
        'submit_talk', name='scipycon_submit_talk'),
    url(r'^%s/edit-talk/(?P<id>\d+)/$' % (SCOPE_ARG_PATTERN),
        'edit_talk', name='scipycon_edit_talk'),
    url(r'^%s/list-talks/(?P<id>\d+)/$' % (SCOPE_ARG_PATTERN),
        'list_talks', name='scipycon_list_talk'),
    )

# Registration
urlpatterns += patterns('project.scipycon.registration.views',
    url(r'^%s/registrations/$' % (SCOPE_ARG_PATTERN), 'registrations',
        name='scipycon_registrations'),
    url(r'^%s/submit-registration/$' % (SCOPE_ARG_PATTERN),
        'submit_registration', name='scipycon_submit_registration'),
    url(r'^%s/edit-registration/(?P<id>\d+)/$' % (SCOPE_ARG_PATTERN),
        'edit_registration', name='scipycon_edit_registration'),
    url(r'^%s/regstats/'% (SCOPE_ARG_PATTERN),
        'regstats', name="scipycon_regstats"),
    )

# Authentication and Profile
urlpatterns += patterns('project.scipycon.user.views',
    url(r'^%s/login/$' % (SCOPE_ARG_PATTERN),
        'login', name='scipycon_login'),
    url(r'^%s/logout/$' % (SCOPE_ARG_PATTERN),
        'logout', name='scipycon_logout'),
    url(r'^%s/account/$' % (SCOPE_ARG_PATTERN),
        'account', name='scipycon_account'),
    url(r'^%s/password/$' % (SCOPE_ARG_PATTERN),
        'password', name='scipycon_password'), # change pwd
    url(r'^%s/username/$' % (SCOPE_ARG_PATTERN),
        'username', name='scipycon_username'), # change uname
    url(r'^%s/edit-profile/$' % (SCOPE_ARG_PATTERN),
        'edit_profile', name='scipycon_edit_profile'),
    url(r'^%s/get-usernames/$' % (SCOPE_ARG_PATTERN),
        'get_usernames', name='scipycon_get_usernames'),
    )

# Proceedings
urlpatterns += patterns('project.scipycon.proceedings.views',
    url(r'^%s/proceedings/submit/$' % (SCOPE_ARG_PATTERN), 'submit',
        name='scipycon_submit_proceedings'),
    url(r'^%s/proceedings/submit/(?P<id>\d+)/$' % (SCOPE_ARG_PATTERN),
        'submit', name='scipycon_submit_proceedings'),
    url(r'^%s/proceedings/show_paper/(?P<id>\d+)/$' % (SCOPE_ARG_PATTERN),
        'show_paper', name='scipycon_show_paper'),
    )

# About pages and all other static html pages
urlpatterns += patterns('',
    url(r'^%s/about/accommodation/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/accommodation.html"},
        name='scipycon_accommodation'),
    url(r'^%s/about/food/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/food.html"},
        name='scipycon_food'),
    url(r'^%s/about/venue/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/venue.html"},
        name='scipycon_venue'),
    url(r'^%s/about/reaching/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/reaching.html"},
        name='scipycon_reaching'),
    url(r'^%s/about/city/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/city.html"},
        name='scipycon_city'),
    url(r'^%s/talks-cfp/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "talk/talks-cfp.html"},
        name='scipycon_talks_cfp'),
    url(r'^%s/talks-cfp/schedule/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "talk/schedule.html"},
        name='scipycon_schedule'),
    url(r'^%s/talks-cfp/tutorial/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "talk/tutorial-schedule.html"},
        name='scipycon_tutorial_schedule'),
    url(r'^%s/talks-cfp/sprint/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "talk/sprint-schedule.html"},
        name='scipycon_sprint_schedule'),
    url(r'^%s/talks-cfp/speakers/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "talk/speakers.html"},
        name='scipycon_speakers'),
    url(r'^%s/publicity/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/publicity.html"},
        name='scipycon_publicity'),
    url(r'^%s/about/fees/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/fees.html"},
        name='scipycon_fees'),
    url(r'^%s/organizers/$' % (SCOPE_ARG_PATTERN),
        direct_to_template, {"template": "about/organizers.html"},
        name='scipycon_organizers'),

    )

# Password reset
urlpatterns += patterns('django.contrib.auth.views',
     url(r'^password-reset/$', 'password_reset', name='scipycon_password_reset'),
     url(r'^password-reset-done/$', 'password_reset_done'),
     url(r'^password-reset-confirm/(?P<uidb36>[-\w]*)/(?P<token>[-\w]*)$', 'password_reset_confirm'),
     url(r'^password-reset-complete/$', 'password_reset_complete'),
)

# Serve static files in DEBUG = True mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
    )

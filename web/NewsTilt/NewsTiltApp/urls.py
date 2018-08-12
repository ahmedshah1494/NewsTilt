"""NewsTilt URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signup$', views.signup_new_user, name='signup'),
    url(r'^get_categories$', views.get_categories, name='get_categories'),
    url(r'^profile$', views.get_user_profile, name='profile'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^change_password$', views.change_password, name='change_password'),
    url(r'^feed/(?P<start_idx>[0-9]+)/(?P<n_items>[0-9]+)$', views.get_feed, name='get_feed'),
    url(r'^like/(?P<article_id>[0-9]+)$', views.like_article, name='like'),
    url(r'^swipe/(?P<article_id>[0-9]+)/(?P<direction>[l,r]+)$', views.swipe_article, name='swipe'),
    url(r'^view/(?P<article_id>[0-9]+)$', views.view_article, name='view'),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]

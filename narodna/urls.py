from django.conf.urls import include, url
from django.contrib import admin

from narodna import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<driversecret>\w{32})', views.drive),
    url(r'^stream', views.stream),
    url(r'^check', views.checkSecret),
    url(r'^signup', views.signup),
    url(r'^time', views.checkTime),
    url(r'^remind', views.sendEmailReminder),
    url(r'^testdrive', views.testDrive),
    url(r'^list', views.listDriversandFuras),
    url(r'^getTime', views.getTime),
    url(r'^getSpots', views.getSpots),
    url(r'^postImage', views.postImage),
    url(r'^maintenance/$', views.maintenance),
    url(r'^maintenance(?P<status_>\d+)/$', views.maintenance),
]

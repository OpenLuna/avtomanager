from django.conf.urls import include, url
from django.contrib import admin

from signups import views

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
]
from django.conf.urls import patterns, url
from llamalandmine import views


urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^register/$', views.register, name='register'),)

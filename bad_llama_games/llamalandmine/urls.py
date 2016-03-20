from django.conf.urls import patterns, url
from llamalandmine import views


urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^register/$', views.register, name='register'),
                       url(r'^play/$', views.play, name='play'),
                       url(r'^game/(?P<level>[\w\-]+)/$', views.game, name='game'),
                       url(r'^get_grid_data/$', views.get_grid_data, name='get_grid_data'),
                       url(r'^end_game/$', views.end_game, name='end_game'),
                       url(r'^game_over/$', views.game_over, name='game_over'),
                       url(r'^view_profile/$', views.view_profile, name='view_profile'),
                       url(r'^profile/(?P<profile_username>[\w\-]+)/$', views.profile, name='profile'),
                       url(r'^handle_requests/$', views.handle_requests, name='handle_requests'),
                       url(r'^leaderboard/$', views.leaderboard, name='leaderboard'),
                       url(r'^how_to/$', views.how_to, name='how_to'),
                       url(r'^userlogout/$', views.userlogout, name='userlogout'),
                       url(r'^restricted/$', views.restricted, name='restricted'),
)

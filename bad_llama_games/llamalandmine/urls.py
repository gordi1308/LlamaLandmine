from django.conf.urls import patterns, url

from llamalandmine.views import views, game_views, profile_views

urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^register/$', views.register, name='register'),
                       url(r'^play/$', game_views.play, name='play'),
                       url(r'^game/(?P<level>[\w\-]+)/$', game_views.game, name='game'),
                       url(r'^get_grid_data/$', game_views.get_grid_data, name='get_grid_data'),
                       url(r'^end_game/$', game_views.end_game, name='end_game'),
                       url(r'^game_over/$', game_views.game_over, name='game_over'),
                       url(r'^view_profile/$', profile_views.view_profile, name='view_profile'),
                       url(r'^profile/(?P<profile_username>[\w\-]+)/$', profile_views.profile, name='profile'),
                       url(r'^handle_requests/$', profile_views.handle_requests, name='handle_requests'),
                       url(r'^leaderboard/$', views.leaderboard, name='leaderboard'),
                       url(r'^how_to/$', views.how_to, name='how_to'),
                       url(r'^userlogout/$', views.userlogout, name='userlogout'),
                       url(r'^restricted/$', views.restricted, name='restricted'),
)

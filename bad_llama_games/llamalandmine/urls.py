from django.conf.urls import patterns, url
from llamalandmine import views


urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^register/$', views.register, name='register'),
                       url(r'^play/$',views.play, name='play'),
                       url(r'^game/(?P<level>[\w\-]+)/$', views.game, name='game'),
                       url(r'^get_grid_data/$', views.get_grid_data, name='get_grid_data'),
                       url(r'^profile/$',views.profile, name='profile'),
                       url(r'^leaderboard/$',views.leaderboard, name='leaderboard'),
                       url(r'^how_to/$',views.how_to, name='how_to'),
                       url(r'^userlogout/$',views.userlogout, name='userlogout'),
                       url(r'^game_over/',views.game_over, name='game_over'),
)
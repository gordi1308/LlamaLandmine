import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bad_llama_games.settings')

import django

django.setup()

from llamalandmine.models import Game, RegisteredUser, User


def game_over():
    user = User.objects.get(username='gregg')
    gregg = RegisteredUser.objects.get(user=user)
    lastgame = Game.objects.get(user=gregg, level='easy')

    todaygames = list(Game.objects.filter(date_played=lastgame.date_played).order_by('-score'))
    position = todaygames.index(lastgame)
    todaylist = todaygames[position-2:position+2]

    print todaygames
    print todaylist


if __name__ == '__main__':
    game_over()

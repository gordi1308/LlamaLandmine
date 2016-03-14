import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bad_llama_games.settings')

import django

django.setup()

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser
from django.contrib.auth.models import User


def populate():
    user1 = add_user(username='gordi',
                    email='gordi@gmail.com')

    add_game(user=user1, level='easy', was_won=True,
             score=100, time_taken=120)

    add_game(user=user1, level='medium', was_won=False,
             score=2, time_taken=10)

    add_game(user=user1, level='hard', was_won=False,
             score=0, time_taken=2)

    user2 = add_user(username='gregg',
                    email='gregg@gmail.com')

    add_game(user=user2, level='easy', was_won=False,
             score=0, time_taken=1)

    add_game(user=user2, level='medium', was_won=True,
             score=230, time_taken=200)

    add_game(user=user2, level='hard', was_won=False,
             score=15, time_taken=20)

    user3 = add_user(username='unknown',
                    email='unknown@gmail.com')

    add_game(user=user3, level='easy', was_won=True,
             score=160, time_taken=300)

    add_challenge(user1, user2, 100)
    add_challenge(user1, user3, 100)
    add_challenge(user3, user1, 160)

    badge1 = add_badge(name='badge1', description='Badge 1', tier=1)
    badge2 = add_badge(name='badge2', description='Badge 2', tier=1)
    badge3 = add_badge(name='badge3', description='Badge 3', tier=1)

    user1.earned_badges.add(badge1)
    user1.earned_badges.add(badge2)
    user2.earned_badges.add(badge2)
    user3.earned_badges.add(badge3)


def add_badge(name, description, tier):
    badge = Badge.objects.get_or_create(name=name)[0]
    badge.description = description
    badge.tier = tier
    badge.save()
    return badge


def add_user(username, email, password='pass'):
    user = User.objects.get_or_create(username=username, email=email,
                                      password=password)[0]
    registered_user = RegisteredUser.objects.get_or_create(user=user)[0]
    registered_user.save()
    return registered_user


def add_game(user, level, was_won, score, time_taken):
    game = Game.objects.get_or_create(user=user)[0]
    game.level = level
    game.was_won = was_won
    game.score = score
    game.time_taken = time_taken

    if level == 'easy':
        game.user.games_played_easy += 1
        if game.user.best_score_easy < score:
            game.user.best_score_easy = score
    elif level == 'medium':
        game.user.games_played_medium += 1
        if game.user.best_score_medium < score:
            game.user.best_score_medium = score
    else:
        game.user.games_played_hard += 1
        if game.user.best_score_hard < score:
            game.user.best_score_hard = score

    game.save()
    return game


def add_challenge(challenger, challenged, score_to_beat):
    challenge = Challenge.objects.get_or_create(challenger=challenger,
                                                challenged_user=challenged,
                                                score_to_beat=score_to_beat)[0]
    challenge.save()
    return challenge


if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bad_llama_games.settings')

import django

django.setup()

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, UserBadge
from django.contrib.auth.models import User


def populate():
    add_user(username='leifos',
             email='leifos@gmail.com',
             password='leifos',
             is_staff=True)
    add_user(username='laura',
             email='laura@gmail.com',
             password='laura',
             is_staff=True)

    add_user(username='david',
             email='david@gmail.com',
             password='david',
             is_staff=True)

    gordi = add_user(username='gordi',
                     email='gordi@gmail.com',
                     password='gordi',
                     is_staff=False)

    add_game(user=gordi, level='easy', was_won=True, score=100, time_taken=120)

    add_game(user=gordi, level='medium', was_won=False, score=2, time_taken=10)

    add_game(user=gordi, level='hard', was_won=False, score=0, time_taken=2)

    gregg = add_user(username='gregg',
                     email='gregg@gmail.com',
                     password='gregg',
                     is_staff=False)

    add_game(user=gregg, level='easy', was_won=False, score=0, time_taken=1)

    add_game(user=gregg, level='medium', was_won=True, score=230, time_taken=200)

    add_game(user=gregg, level='hard', was_won=False, score=15, time_taken=20)

    ozgur = add_user(username='ozgur',
                     email='ozgur@gmail.com',
                     password='ozgur',
                     is_staff=False)

    add_game(user=ozgur, level='easy', was_won=True, score=160, time_taken=300)

    add_challenge(gordi, gregg, 100)
    add_challenge(gordi, ozgur, 100)
    add_challenge(gregg, ozgur, 160)

    badge1 = add_badge(name='Gotta start somewhere',
                       description='Play your first game.',
                       tier=1)
    badge2 = add_badge(name="One small step for Man...",
                       description='Win 10 games on Normal',
                       tier=2)
    badge3 = add_badge(name='King of the Mountain',
                       description='Win 15 Challenges',
                       tier=3)

    UserBadge.objects.create(user=gordi, badge=badge1)
    UserBadge.objects.create(user=gordi, badge=badge2)
    UserBadge.objects.create(user=gregg, badge=badge2)
    UserBadge.objects.create(user=ozgur, badge=badge3)

    for user in RegisteredUser.objects.all():
        print user
        print "\tEasy games: " + str(user.games_played_easy) \
              + " - Best score: " + str(user.best_score_easy)
        print "\tMedium games: " + str(user.games_played_medium) \
              + " - Best score: " + str(user.best_score_medium)
        print "\tHard games: " + str(user.games_played_hard) \
              + " - Best score: " + str(user.best_score_hard)
        print "\tEarned badges: " + str(user.earned_badges.count())
        print "\tFriends: " + str(user.friends.count())


def add_badge(name, description, tier):
    badge = Badge.objects.get_or_create(name=name)[0]
    badge.description = description
    badge.tier = tier
    badge.save()
    return badge


def add_user(username, email, password, is_staff):
    user = User.objects.get_or_create(username=username, email=email)[0]
    user.set_password(password)
    user.is_staff = is_staff
    if is_staff:
        user.is_superuser = True
    user.save()
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

    game.user.save()
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

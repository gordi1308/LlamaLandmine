import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bad_llama_games.settings')

import django

django.setup()

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, Request, UserBadge, UserFriend
from llamalandmine.views.game_views import check_challenge_badges, check_game_badges
from llamalandmine.views.profile_views import check_badges_friends
from django.contrib.auth.models import User
from datetime import datetime, timedelta


def populate():
    """Adds badges, users, games, challenges to the db.
    """

    # badges related to plays
    print "Adding badges related to plays..."

    add_badge(name="Of all the games, on all the websites, in all the world, you logged on to mine",
                              description="Play your first game.",
                              tier=1, image="of_all_the_games.png")
    add_badge(name="At first you had my curiosity, now you have my attention",
              description="Play 25 games.",
              tier=2, image="you_had_my_curiosity.png")
    add_badge(name="Addicted",
              description="Play 50 games.",
              tier=3, image="addicted.png")
    add_badge(name="Baby steps",
                                   description="Play a game on Easy difficulty.",
                                   tier=1, image="baby_steps.png")
    add_badge(name="There's always a bigger fish",
                                     description="Play a game on Normal difficulty.",
                                     tier=2, image="always_a_bigger_fish.png")
    add_badge(name="Now this is Llama Landmine!",
                                   description="Play a game on Hard difficulty.",
                                   tier=3, image="now_this_is.png")

    # badges related to wins
    print "Adding badges related to wins..."

    add_badge(name="Chicken Dinner",
                             description="Win your first game.",
              tier=1, image="chicken_dinner.png")
    add_badge(name="You wanna be a big cop in a small town?",
              description="Win 10 games on Easy difficulty.",
              tier=1, image="big_cop.png")
    add_badge(name="Like procuring sweets from an infant",
              description="Win 25 games on Easy difficulty.",
              tier=1, image="like_procuring_sweets.png")
    add_badge(name="One small step for Man...",
              description="Win 10 games on Normal difficulty.",
              tier=2, image="one_small_step.png")
    add_badge(name="That'll do llama",
              description="Win 25 games on Normal difficulty.",
              tier=2, image="thatll_do_llama.png")
    add_badge(name="One giant leap for Llama-kind",
              description="Win 10 games on Hard difficulty.",
              tier=3, image="one_giant_leap.png")
    add_badge(name="The Llama Whisperer",
              description="Win 25 games on Hard difficulty",
              tier=3, image="llama_whisperer.png")

    # badges related to challenges
    print "Adding badges related to challenges..."

    add_badge(name="Great kid, don't get cocky",
              description="Win your first Challenge.",
              tier=1, image="great_kid.png")
    add_badge(name="King of the Hill",
              description="Win 5 Challenges.",
              tier=2, image="king_hill.png")
    add_badge(name="King of the Mountain",
              description="Win 15 Challenges.",
              tier=3, image="king_mountain.png")
    add_badge(name="Playground Bully!",
              description="Beat the same user 5 times in 5 Challenges.",
              tier=2, image="bully.png")
    add_badge(name="It's a trap!",
              description="Receive 5 challenges.",
              tier=1, image="trap.png")
    add_badge(name="I swear by my pretty floral bonnet I will end you",
              description="Accept a Challenge from a friend with a game on Easy difficulty.",
              tier=1, image="floral_bonnet.png")
    add_badge(name="Handbags at dawn",
              description="Accept a challenge from a friend with a game on Normal difficulty",
              tier=1, image="handbags.png")
    add_badge(name="It's a bold strategy Cotton!",
              description="Accept a Challenge from a friend with a game on Hard difficulty.",
              tier=1, image="bold_strategy.png")

    # badges related to friends
    print "Adding badges related to friends..."

    have_one_friend = add_badge(name="Phone a Friend",
                                description="Have 1 friend on Llama Landmine.",
                                tier=1, image="phone.png")
    add_badge(name="Gondor calls for aid!",
              description="Have 5 friends on Llama Landmine.",
              tier=2, image="gondor.png")

    # Misc badges
    print "Adding misc badges..."

    add_badge(name="Ouchtown population you bro!",
              description="Click on your first mine.",
              tier=1, image="ouchtown.png")
    add_badge(name="Collect all the badges!",
              description="Why are you even reading this...",
              tier=3, image="collected_all_badges.png")

    print "Adding users and games..."

    # Each user plays a game once a day
    date_delta = 10

    # First user
    gordi = add_user(username='gordi', email='gordi@gmail.com',
                     password='gordi', is_staff=False)

    # First game
    gordi_game = add_game(user=gordi, date_played=datetime.now() - timedelta(date_delta),
                          level='easy', was_won=True, score=2250, time_taken=45)
    date_delta -= 1

    check_game_badges(user=gordi, user_games=Game.objects.all(), level='easy', was_won=True)

    # Second game
    add_game(user=gordi, date_played=datetime.now() - timedelta(date_delta),
             level='normal', was_won=False, score=2153, time_taken=63)
    date_delta -= 1

    check_game_badges(user=gordi, user_games=Game.objects.all(), level='normal', was_won=False)

    # Third game
    add_game(user=gordi, date_played=datetime.now() - timedelta(date_delta),
             level='hard', was_won=False, score=5880, time_taken=12)
    date_delta -= 1

    check_game_badges(user=gordi, user_games=Game.objects.all(), level='hard', was_won=False)

    # Second user
    gregg = add_user(username='gregg', email='gregg@gmail.com',
                     password='gregg', is_staff=False)

    # First game
    add_game(user=gregg, date_played=datetime.now() - timedelta(date_delta),
             level='easy', was_won=False, score=3435, time_taken=92)
    date_delta -= 1

    check_game_badges(user=gregg, user_games=Game.objects.all(), level='easy', was_won=False)

    # Second game
    gregg_game = add_game(user=gregg, date_played=datetime.now() - timedelta(date_delta),
                          level='normal', was_won=True, score=5895, time_taken=207)
    date_delta -= 1

    check_game_badges(user=gregg, user_games=Game.objects.all(), level='normal', was_won=True)

    # Third game
    add_game(user=gregg, date_played=datetime.now() - timedelta(date_delta),
             level='hard', was_won=False, score=2860, time_taken=28)
    date_delta -= 1

    check_game_badges(user=gregg, user_games=Game.objects.all(), level='hard', was_won=False)

    # Third user
    ozgur = add_user(username='ozgur', email='ozgur@gmail.com',
                     password='ozgur', is_staff=False)

    # First game
    add_game(user=ozgur, date_played=datetime.now() - timedelta(date_delta),
             level='easy', was_won=True, score=160, time_taken=300)
    date_delta -= 1

    check_game_badges(user=ozgur, user_games=Game.objects.all(), level='easy', was_won=True)

    # Fourth user
    clem = add_user(username='clem', email='clem@gmail.com',
                    password='clem', is_staff=False)

    # First game
    clem_easy_game = add_game(user=clem, date_played=datetime.now() - timedelta(date_delta+2),
             level='easy', was_won=True, score=2610, time_taken=8)
    date_delta -= 1

    check_game_badges(user=clem, user_games=Game.objects.all(), level='easy', was_won=True)

    # Second game
    clem_normal_game = add_game(user=clem, date_played=datetime.now() - timedelta(date_delta+2),
             level='normal', was_won=True, score=7170, time_taken=172)
    date_delta -= 1

    check_game_badges(user=clem, user_games=Game.objects.all(), level='normal', was_won=True)

    # Third game
    clem_hard_game = add_game(user=clem, date_played=datetime.now() - timedelta(date_delta+2),
             level='hard', was_won=True, score=18680, time_taken=227)
    date_delta -= 1

    check_game_badges(user=clem, user_games=Game.objects.all(), level='hard', was_won=True)

    # Friendships
    UserFriend.objects.get_or_create(user=gordi, friend=gregg)
    check_badges_friends(user=gordi, friend_list=gordi.friends)

    UserFriend.objects.get_or_create(user=gregg, friend=gordi)
    check_badges_friends(user=gregg, friend_list=gregg.friends)

    UserFriend.objects.get_or_create(user=gregg, friend=clem)
    check_badges_friends(user=gregg, friend_list=gregg.friends)

    UserFriend.objects.get_or_create(user=clem, friend=gregg)
    check_badges_friends(user=clem, friend_list=gordi.friends)

    # Friend Requests
    Request.objects.get_or_create(user=ozgur, target=gregg)
    Request.objects.get_or_create(user=ozgur, target=gordi)
    Request.objects.get_or_create(user=ozgur, target=clem)

    # Challenges
    print "Adding challenges..."

    add_challenge(game=gordi_game, challenged=gregg)

    add_challenge(game=gregg_game, challenged=gordi)

    add_challenge(game=clem_easy_game, challenged=gregg)
    add_challenge(game=clem_normal_game, challenged=gregg)
    add_challenge(game=clem_hard_game, challenged=gregg)


    # Other users...
    add_user(username='leifos', email='leifos@gmail.com',
             password='leifos', is_staff=True)

    add_user(username='laura', email='laura@gmail.com',
             password='laura', is_staff=True)

    add_user(username='david', email='david@gmail.com',
             password='david', is_staff=True)

    for user in RegisteredUser.objects.all():
        print user

        easy_games = Game.objects.filter(user=user, level='easy')
        best_score_easy = 0
        if easy_games.count() > 0:
            best_score_easy = easy_games.order_by('-score')[0].score
        print "\tEasy games: " + str(easy_games.count()) \
              + " - Best score: " + str(best_score_easy)

        normal_games = Game.objects.filter(user=user, level='normal')
        best_score_normal = 0
        if normal_games.count() > 0:
            best_score_normal = normal_games.order_by('-score')[0].score
        print "\tNormal games: " + str(normal_games.count()) \
              + " - Best score: " + str(best_score_normal)

        hard_games = Game.objects.filter(user=user, level='hard')
        best_score_hard = 0
        if hard_games.count() > 0:
            best_score_hard = hard_games.order_by('-score')[0].score
        print "\tHard games: " + str(hard_games.count()) \
              + " - Best score: " + str(best_score_hard)

        print "\tEarned badges: " + str(user.earned_badges.count())

        requests = Request.objects.filter(target=user)
        print "\tFriends: " + str(user.friends.count())
        print "\tRequests received: " + str(requests.count())

        challenges = Challenge.objects.filter(challenged_user=user)
        print "\tChallenges received: " + str(challenges.count())



def add_badge(name, description, tier, image):
    """Creates a new badge and adds it to the db.
    :param name: badge name
    :param description: badge description
    :param tier: badge tier
    :param image: badge image
    :return: the created Badge object
    """

    badge = Badge.objects.get_or_create(name=name)[0]
    badge.description = description
    badge.tier = tier
    badge.icon = image
    badge.save()
    return badge


def add_user(username, email, password, is_staff):
    """Creates a new user and adds it to the db.
    :param username: username of the user
    :param email: email of the user
    :param password: password of the user
    :param is_staff: whether to set the user as superuser or not
    :return: the created RegisteredUser object
    """

    user = User.objects.get_or_create(username=username, email=email)[0]
    user.set_password(password)
    user.is_staff = is_staff
    if is_staff:
        user.is_superuser = True
    user.save()
    registered_user = RegisteredUser.objects.get_or_create(user=user)[0]
    registered_user.save()
    return registered_user


def add_game(user, date_played, level, was_won, score, time_taken):
    """Creates a new game for the given user and adds it to the db.
    :param user: the user playing the game
    :param date_played: the date the game was played on
    :param level: the level of the game
    :param was_won: the outcome of the game (True if the user won)
    :param score: the score obtained by the user for that game
    :param time_taken: the time taken by the user for that game
    :return: the created Game object
    """

    game = Game.objects.get_or_create(user=user, date_played=date_played)[0]
    game.level = level
    game.was_won = was_won
    game.score = score
    game.time_taken = time_taken

    game.save()
    return game


def add_challenge(game, challenged):
    """Creates a new challenge between the given users and adds it to the db.
    :param challenged: user who is being challenged
    :param game: the game on which the challenge is based
    :return: the created Challenge object
    """
    challenge = Challenge.objects.get_or_create(game=game, challenged_user=challenged)[0]
    challenge.save()
    return challenge


if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bad_llama_games.settings')

import django

django.setup()

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, UserBadge
from django.contrib.auth.models import User


def populate():
    """Adds badges, users, games, challenges to the db.
    """

    # Badges related to plays
    print "Adding badges related to plays..."

    play_one_game = add_badge(name="Gotta start somewhere",
                              description="Play your first game.",
                              tier=1)
    add_badge(name="At first you had my curiosity, now you have my attention",
              description="Play 25 games.",
              tier=2)
    add_badge(name="Addicted",
              description="Play 50 games.",
              tier=3)
    play_one_easy_game = add_badge(name="Baby steps",
                                   description="Play a game on Easy difficulty.",
                                   tier=1)
    play_one_normal_game = add_badge(name="There's always a bigger fish",
                                     description="Play a game on Normal difficulty.",
                                     tier=2)
    play_one_hard_game = add_badge(name="Now this is Llama Landmine!",
                                   description="Play a game on Hard difficulty.",
                                   tier=3)

    # Badges related to wins
    print "Adding badges related to wins..."

    win_one_game = add_badge(name="Chicken Dinner",
                             description="Win your first game.",
              tier=1)
    add_badge(name="You wanna be a big cop in a small town?",
              description="Win 10 games on Easy difficulty.",
              tier=1)
    add_badge(name="Like procuring sweets from an infant",
              description="Win 25 games on Easy difficulty.",
              tier=1)
    add_badge(name="One small step for Man...",
              description="Win 10 games on Normal difficulty.",
              tier=2)
    add_badge(name="That'll do llama",
              description="Win 25 games on Normal difficulty.",
              tier=2)
    add_badge(name="One giant leap of Llama-kind",
              description="Win 10 games on Hard difficulty.",
              tier=3)
    add_badge(name="The Llama Whisperer",
              description="Win 25 games on Hard difficulty",
              tier=3)

    # Badges related to challenges
    print "Adding badges related to challenges..."

    add_badge(name="Great kid, don't get cocky",
              description="Win your first Challenge.",
              tier=1)
    add_badge(name="King of the Hill",
              description="Win 5 Challenges.",
              tier=2)
    add_badge(name="King of the Mountain",
              description="Win 15 Challenges.",
              tier=3)
    add_badge(name="Playground Bully!",
              description="Beat the same user 5 times in 5 Challenges.",
              tier=2)
    add_badge(name="It's a trap!",
              description="Receive 5 challenges.",
              tier=1)
    add_badge(name="I swear by my pretty floral bonnet I will end you",
              description="Accept a Challenge from a friend with a game on Easy difficulty.",
              tier=1)
    add_badge(name="Handbags at dawn",
              description="Accept a challenge from a friend with a game on Normal difficulty",
              tier=1)
    add_badge(name="It's a bold strategy Cotton!",
              description="Accept a Challenge from a friend with a game on Hard difficulty.",
              tier=1)

    # Badges related to friends
    print "Adding badges related to friends..."

    add_badge(name="Phone a Friend",
              description="Invite a friend to Llama Landmine.",
              tier=1)
    add_badge(name="Gondor calls for aid!",
              description="Invite 5 friends to Llama Landmine.",
              tier=2)

    # Badges related to login
    print "Adding badges related to login..."

    add_badge(name="Hello Again!",
              description="Log in 2 days in a row.",
              tier=1)
    add_badge(name="Mambo Number 5",
              description="Log in 5 days in a row.",
              tier=2)
    add_badge(name="Gotta save 'em all",
              description="Log in 10 days in a row... Don't you have anything better to do?",
              tier=3)

    # Misc badges
    print "Adding misc badges..."

    add_badge(name="Ouchtown population you bro!",
              description="Click on your first mine.",
              tier=1)
    add_badge(name="...At least I've got chicken",
              description="Lose a game within 2 seconds with more than 5 clicks.",
              tier=2)
    add_badge(name="Collect all the badges!",
              description="Why are you even reading this...",
              tier=3)

    print "Adding users and games..."

    # First user
    gordi = add_user(username='gordi',
                     email='gordi@gmail.com',
                     password='gordi',
                     is_staff=False)

    add_game(user=gordi, level='easy', was_won=True, score=100, time_taken=120)
    UserBadge.objects.create(user=gordi, badge=play_one_game)
    UserBadge.objects.create(user=gordi, badge=play_one_easy_game)
    UserBadge.objects.create(user=gordi, badge=win_one_game)

    add_game(user=gordi, level='normal', was_won=False, score=2, time_taken=10)
    UserBadge.objects.create(user=gordi, badge=play_one_normal_game)

    add_game(user=gordi, level='hard', was_won=False, score=0, time_taken=2)
    UserBadge.objects.create(user=gordi, badge=play_one_hard_game)

    # Second user
    gregg = add_user(username='gregg',
                     email='gregg@gmail.com',
                     password='gregg',
                     is_staff=False)

    add_game(user=gregg, level='easy', was_won=False, score=0, time_taken=1)
    UserBadge.objects.create(user=gregg, badge=play_one_game)
    UserBadge.objects.create(user=gregg, badge=play_one_easy_game)
    UserBadge.objects.create(user=gregg, badge=win_one_game)

    add_game(user=gregg, level='normal', was_won=True, score=230, time_taken=200)
    UserBadge.objects.create(user=gregg, badge=play_one_normal_game)

    add_game(user=gregg, level='hard', was_won=False, score=15, time_taken=20)
    UserBadge.objects.create(user=gregg, badge=play_one_hard_game)

    # Third user
    ozgur = add_user(username='ozgur',
                     email='ozgur@gmail.com',
                     password='ozgur',
                     is_staff=False)

    add_game(user=ozgur, level='easy', was_won=True, score=160, time_taken=300)
    UserBadge.objects.create(user=ozgur, badge=play_one_game)
    UserBadge.objects.create(user=ozgur, badge=play_one_easy_game)
    UserBadge.objects.create(user=ozgur, badge=win_one_game)

    # Challenges
    print "Adding challenges..."

    add_challenge(challenger=gordi, challenged=gregg,
                  score_to_beat=100, level='easy')
    add_challenge(challenger=gordi, challenged=ozgur,
                  score_to_beat=100, level='easy')
    add_challenge(challenger=ozgur, challenged=gregg,
                  score_to_beat=160, level='easy')

    # Other users...
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
    """Creates a new badge and adds it to the db.
    :param name: badge name
    :param description: badge description
    :param tier: badge tier
    :return: the created Badge object
    """

    badge = Badge.objects.get_or_create(name=name)[0]
    badge.description = description
    badge.tier = tier
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


def add_game(user, level, was_won, score, time_taken):
    """Creates a new game for the given user and adds it to the db
    if he/she doesn't have one already,
    or updates the already-created one with the given attributes.
    :param user: the user playing the game
    :param level: the level of the game
    :param was_won: the outcome of the game (True if the user won)
    :param score: the score obtained by the user for that game
    :param time_taken: the time taken by the user for that game
    :return: the created Game object
    """

    game = Game.objects.get_or_create(user=user)[0]
    game.level = level
    game.was_won = was_won
    game.score = score
    game.time_taken = time_taken

    # Update user's stats
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


def add_challenge(challenger, challenged, score_to_beat, level):
    """Creates a new challenge between the given users and adds it to the db.
    :param challenger: user who created the challenge
    :param challenged: user who is being challenged
    :param score_to_beat: score that the challenged user has to beat to win
    :param level: the level of the game
    :return: the created Challenge object
    """
    challenge = Challenge.objects.get_or_create(challenger=challenger,
                                                challenged_user=challenged,
                                                score_to_beat=score_to_beat,
                                                level=level)[0]
    challenge.save()
    return challenge


if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()

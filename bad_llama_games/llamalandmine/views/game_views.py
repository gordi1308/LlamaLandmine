from __future__ import division

from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import loader
from django.core.mail import send_mail

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, \
    User, UserBadge, UserFriend
from llamalandmine.minesweeper import GameGrid

import json


def play(request):
    """View called when the user has to be redirected to a default game page."""
    level = 'normal'
    return HttpResponseRedirect(reverse("game", args=(level,)))


def game(request, level):
    """View called when the user chooses the level of the game he/she wants to play at."""

    request.session['game_grid'] = None

    # Grid data
    game_grid = GameGrid(level)

    # Store the grid in the request session so that
    # the data is accessible the whole time during the game
    request.session['game_grid'] = game_grid

    context_dict = dict()

    context_dict['level'] = level
    context_dict['size'] = game_grid.size
    context_dict['llamas'] = game_grid.nb_llamas
    context_dict['mines'] = game_grid.nb_mines

    return render(request, 'game.html', context_dict)


def get_grid_data(request):
    """View called when the user clicks on a cell in during the game."""
    if request.is_ajax() and request.method == 'GET':
        row = int(request.GET['row'])
        column = int(request.GET['column'])

        game_grid = request.session['game_grid']

        # Content of the cell clicked on, or list of cells to be revealed
        # if the user clicked on an empty cell
        result = game_grid.click_cell(row=row, col=column)

        json_data = json.dumps(result)
        return HttpResponse(json_data)

    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


def end_game(request):
    """View called when the user finishes a game (no matter what the outcome) is
    to reveal the content of the grid that have not been clicked on yet."""
    if request.is_ajax() and request.method == 'GET':
        game_grid = request.session['game_grid']

        result = json.dumps(game_grid.get_unclicked_cells())

        return HttpResponse(result)

    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


def game_over(request):
    """View called after a user has finished a game to display the user's score,
    and his position in the leaderboard if he registered,
    or the top five registered players."""

    context_dict = dict()

    if request.is_ajax() and request.method == 'POST':

        get_data_from_request(request, context_dict)

        # Start positions of the leaderboard entries
        today_start = 0
        all_time_start = 0
        in_friends_start = 0

        # The current user is registered
        if not request.user.is_anonymous():
            try:
                user = RegisteredUser.objects.get(user=request.user)
                context_dict['registered'] = True

                game = save_game(user=user, context_dict=context_dict)

                print "swag"
                # List of games played ever
                all_time_games = Game.objects.all()
                get_today_or_all_time_leaderboard(games_filter=all_time_games,
                                                  last_game=game, today=False,
                                                  context_dict=context_dict)
                # List of games played today
                today_games = all_time_games.filter(date_played=datetime.now()).order_by('-score')
                get_today_or_all_time_leaderboard(games_filter=today_games,
                                                  last_game=game, today=True,
                                                  context_dict=context_dict)

                # Current user's friend list
                friend_list = user.friends.all()

                if friend_list.__len__() > 0:
                    # List containing the games played by current user or his friends
                    friends_games = list(Game.objects.filter(user__in=friend_list))
                    friends_games.append(game)

                    sorted(friends_games, key=lambda g: g.score, reverse=True)

                    # Find the position of this game in current user's friends leaderboard
                    in_friends_position = list(friends_games).index(game)
                    if in_friends_position >= 2:
                        in_friends_start = in_friends_position-2
                    else:
                        in_friends_start = 0

                    friends_games_list = friends_games[in_friends_start:in_friends_start+5]

                # Current user has no friends
                else:
                    in_friends_start = 0
                    friends_games_list = []

            # Current user was not recognised
            except RegisteredUser.DoesNotExist:
                context_dict['registered'] = False
                today_game_list = Game.objects.filter(date_played=datetime.now()).order_by('-score')[:5]
                all_time_game_list = Game.objects.all().order_by('-score')[:5]
                friends_games_list = []

        # Current user is not registered
        else:
            context_dict['registered'] = False
            today_game_list = Game.objects.filter(date_played=datetime.now()).order_by('-score')[:5]
            all_time_game_list = Game.objects.all().order_by('-score')[:5]
            friends_games_list = []

        context_dict['friendlist'] = friends_games_list
        context_dict['friendstart'] = in_friends_start

        return HttpResponse(render_to_response('game_over.html', context_dict))

    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


def get_data_from_request(request, context_dict):
    game_grid = request.session['game_grid']
    context_dict['level'] = request.POST['level']
    context_dict['time_taken'] = int(request.POST['time_taken'])
    llamas_found = game_grid.nb_llamas - int(request.POST['llamas_left'])

    # The user can only win a game if he/she finds all the llamas
    context_dict['was_won'] = (game_grid.nb_llamas == llamas_found)

    calculate_score(time_taken=context_dict['time_taken'],
                    llamas_found=llamas_found, context_dict=context_dict)

    # Remove the grid from the request session
    request.session['game_grid'] = None


def calculate_score(time_taken, llamas_found, context_dict):
    score = 20000 - (time_taken*10) + (1000*llamas_found)
    if not context_dict['was_won']:
        score /= 2

    if context_dict['level'] == 'easy':
        score /= 2
    elif context_dict['level'] == 'hard':
        score *= 2

    context_dict['last_score'] = int(score)


def update_reg_user_data(user, context_dict):
    last_game = save_game(user=user, context_dict=context_dict)

    # List of games played ever
    all_time_games = Game.objects.all()
    get_today_or_all_time_leaderboard(games_filter=all_time_games, last_game=last_game,
                                      today=False, context_dict=context_dict)

    # List of games played today
    today_games = all_time_games.filter(date_played=datetime.now()).order_by('-score')
    get_today_or_all_time_leaderboard(games_filter=today_games, last_game=last_game,
                                      today=True, context_dict=context_dict)

    print "yolo"
    get_friends_leaderboard(user=user, context_dict=context_dict, last_game=last_game)


def save_game(user, context_dict):
     # Add the game to the user's game history
    last_game = Game(user=user, level=context_dict['level'],
                     time_taken=context_dict['time_taken'],
                     was_won=context_dict['was_won'], score=context_dict['last_score'])
    last_game.save()

    # Check the badges that this game unlocked
    user_games = Game.objects.filter(user=user)

    check_game_badges(user=user, user_games=user_games,
                      level=context_dict['level'], was_won=context_dict['was_won'])

    # Update all the ongoing challenges at the right level
    update_challenges(user=user, level=context_dict['level'],
                      score=context_dict['last_score'])


    return last_game


def get_today_or_all_time_leaderboard(games_filter, last_game, today, context_dict):
    # Position of this game in the leaderboard
    position = list(games_filter).index(last_game)

    if position >= 2:
        start = position-2
    else:
        start = 0

    game_list = games_filter[start:start+5]

    if today:
        key = "today"
    else:
        key = "alltime"

    context_dict[key + 'list'] = game_list
    context_dict[key + 'start'] = start


def get_friends_leaderboard(user, last_game, context_dict):
    # Current user's friend list
    friend_list = user.friends.all()

    if friend_list.__len__() > 0:
        # List containing the games played by current user or his friends
        friends_games = list(Game.objects.filter(user__in=friend_list))
        friends_games.append(game)
        sorted(friends_games, key=lambda g: g.score, reverse=True)

        # Find the position of this game in current user's friends leaderboard
        in_friends_position = list(friends_games).index(last_game)
        if in_friends_position >= 2:
            in_friends_start = in_friends_position-2
        else:
            in_friends_start = 0

        friends_games_list = friends_games[in_friends_start:in_friends_start+5]

        context_dict['friendlist'] = friends_games_list
        context_dict['friendstart'] = in_friends_start


def check_game_badges(user, user_games, level, was_won):
    if user_games.__len__() == 1:
        badge = Badge.objects.get(name__startswith="Of all the games")
        UserBadge.objects.get_or_create(user=user, badge=badge)

        if level == 'easy':
            badge = Badge.objects.get(name="Baby steps")
        elif level == 'normal':
            badge = Badge.objects.get(name="There's always a bigger fish")
        else:
            badge = Badge.objects.get(name="Now this is Llama Landmine!")
        UserBadge.objects.get_or_create(user=user, badge=badge)
    elif user_games.__len__() == 25:
        badge = Badge.objects.get(name__startswith="At first you had my curiosity,")
        UserBadge.objects.get_or_create(user=user, badge=badge)

    elif user_games.__len__() == 50:
        badge = Badge.objects.get(name="Addicted")
        UserBadge.objects.get_or_create(user=user, badge=badge)

    if was_won:
        user_wins = user_games.filter(was_won=True)

        if user_wins.__len__() == 1:
            badge = Badge.objects.get(name="Chicken Dinner")
            UserBadge.objects.get_or_create(user=user, badge=badge)

        elif user_wins.__len__() == 10:
            if level == 'easy':
                badge = Badge.objects.get(name="You wanna be a big cop in a small town?")
            elif level == 'normal':
                badge = Badge.objects.get(name="One small step for Man...")
            else:
                badge = Badge.objects.get(name="One giant leap for Llama-kind")
            UserBadge.objects.get_or_create(user=user, badge=badge)

        elif user_wins.__len__() == 25:
            if level == 'easy':
                badge = Badge.objects.get(name="Like procuring sweets from an infant")
            elif level == 'normal':
                badge = Badge.objects.get(name="That'll do llama")
            else:
                badge = Badge.objects.get(name="The Llama Whisperer")
            UserBadge.objects.get_or_create(user=user, badge=badge)

    else:
        badge = Badge.objects.get(name="Ouchtown population you bro!")
        UserBadge.objects.get_or_create(user=user, badge=badge)


def update_challenges(user, level, score):

    challenges = Challenge.objects.filter(challenged_user=user,
                                          accepted=True, completed=False, game__level=level)

    for challenge in challenges:
        if score >= challenge.score_to_beat():
            challenge.winner = user
            challenge.completed = True
            challenge.save()
        else:
            challenge.remaining_attempts -= 1
            if challenge.remaining_attempts is 0:
                challenge.completed = True
            challenge.save()

    check_challenge_badges(user)


def check_challenge_badges(user):
    challenges = Challenge.objects.filter(completed=True, winner=user)

    if challenges.count() == 1:
        badge = Badge.objects.get("Great kid, don't get cocky")
        UserBadge.objects.get_or_create(user=user, badge=badge)

    elif challenges.count() == 5:
        badge = Badge.objects.get("King of the Hill")
        UserBadge.objects.get_or_create(user=user, badge=badge)

    elif challenges.count() == 15:
        badge = Badge.objects.get("King of the Mountain")
        UserBadge.objects.get_or_create(user=user, badge=badge)


def send_challenge(request):

    if request.is_ajax() and request.method == 'POST':

        try:
            target_name = request.POST['to']
            target = User.objects.get(username=target_name)
            target_user = RegisteredUser.objects.get(user=target)
            print target_user

            current_user = RegisteredUser.objects.get(user=request.user)
            friend_filter = UserFriend.objects.filter(user=current_user)
            friend_list = []
            for entry in friend_filter:
                friend_list.append(entry.friend)

            if target_user in friend_list:
                game = Game.objects.filter(user=current_user).order_by('-date_played')[0]
                Challenge.objects.create(challenged_user=target_user, game=game)

                message = str("You have been challenged! " + str(current_user.user_name()) +
                              " bites their thumb at you Sir/Lady. Rise to the challenge "
                              "and vanquish your rival! The game is afoot! Bad Llama Games")
                html_message = loader.render_to_string("challenge_email.html", {
                    'reg_user.user.username': target_user.user_name(),
                    'current_user.user.username': current_user.user_name()
                })
                send_mail("A duel to the death, or at least to maiming !", message, "donotreply@badllamagames.com",
                          [target_user.user_email()], html_message)

                target_badges = UserBadge.objects.filter(user=target_user)
                if target_badges.count() == 5:
                    badge = Badge.objects.get(name="It's a trap!")
                    UserBadge.objects.get_or_create(user=target_user, badge=badge)

                return HttpResponse(json.dumps(True))

        except User.DoesNotExist:
            pass
        except RegisteredUser.DoesNotExist:
            pass

        return HttpResponse(json.dumps(False))

    else:
        return HttpResponseRedirect('/llamalandmine/restricted/')
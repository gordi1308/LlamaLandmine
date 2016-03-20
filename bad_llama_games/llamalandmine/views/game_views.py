from __future__ import division

from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, render_to_response

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, UserBadge
from llamalandmine.minesweeper import GameGrid

import json


def play(request):
    """View called when the user has to be redirected to a default game page."""
    level = 'normal'
    return HttpResponseRedirect(reverse("game", args=(level,)))


def game(request, level):
    """View called when the user chooses the level of the game he/she wants to play at."""

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

    if request.is_ajax() and request.method == 'POST':

        game_grid = request.session['game_grid']
        level = request.POST['level']
        time_taken = int(request.POST['time_taken'])

        llamas_found = game_grid.nb_llamas - int(request.POST['llamas_left'])

        # The user can only win a game if he/she finds all the llamas
        was_won = game_grid.nb_llamas == llamas_found

        score = 20000 - (time_taken*10) + (1000*llamas_found)
        if not was_won:
            score /= 2

        if level == 'easy':
            score /= 2
        elif level == 'hard':
            score *= 2

        # Remove the grid from the request session
        request.session['game_grid'] = None

        # Start positions of the leaderboard entries
        today_start = 0
        all_time_start = 0
        in_friends_start = 0

        # The current user is registered
        if not request.user.is_anonymous():
            try:
                user = RegisteredUser.objects.get(user=request.user)

                # Add the game to the user's game history
                game = Game(user=user, level=level, time_taken=time_taken,
                            was_won=was_won, score=int(score))
                game.save()

                # Check the badges that this game unlocked
                user_games = Game.objects.filter(user=user)
                check_game_badges(user=user, user_games=user_games,
                                  level=level, was_won=was_won)

                # CHECK CHALLENGES
                # CHECK BADGES CHALLENGES

                # CREATE CHALLENGE

                # List of games played today
                today_games = Game.objects.filter(date_played=datetime.now()).order_by('-score')

                # Position of this game in today's leaderboard
                today_position = list(today_games).index(game)
                if today_position >= 2:
                    today_start = today_position-2
                else:
                    today_start = 0
                today_game_list = today_games[today_start:today_start+5]

                # List of games played ever
                all_time_games = Game.objects.all().order_by('-score')

                # Position of this game in all time's leaderboard
                all_time_position = list(all_time_games).index(game)
                if all_time_position >= 2:
                    all_time_start = all_time_position-2
                else:
                    all_time_start = 0
                all_time_game_list = all_time_games[all_time_start:all_time_start+5]

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
                today_game_list = Game.objects.filter(date_played=datetime.now()).order_by('-score')[:5]
                all_time_game_list = Game.objects.all().order_by('-score')[:5]
                friends_games_list = []

        # Current user is not registered
        else:
            today_game_list = Game.objects.filter(date_played=datetime.now()).order_by('-score')[:5]
            all_time_game_list = Game.objects.all().order_by('-score')[:5]
            friends_games_list = []

        context_dict = {
            "last_score": int(score),
            "level": level,
            "todaylist": today_game_list,
            "todaystart": today_start,
            "alltimelist": all_time_game_list,
            "atstart": all_time_start,
            "friendlist": friends_games_list,
            "friendstart": in_friends_start
        }

        return HttpResponse(render_to_response('game_over.html', context_dict))

    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


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
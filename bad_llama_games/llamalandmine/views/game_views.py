from __future__ import division

from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

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

    game_grid = get_new_grid(request, level)

    context_dict = {
        'level': level,
        'size': game_grid.size,
        'size_range': range(game_grid.size),
        'llamas': game_grid.nb_llamas,
        'mines': game_grid.nb_mines
    }

    return render(request, 'game2.html', context_dict)


def reset(request):
    if request.is_ajax() and request.method == 'GET':
        # Grid data
        get_new_grid(request, request.GET['level'])
        return HttpResponse()

    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


def get_new_grid(request, level):
    # Grid data
    game_grid = GameGrid(level)

    # Store the grid in the request session so that
    # the data is accessible the whole time during the game
    request.session['game_grid'] = game_grid
    print game_grid

    return game_grid


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

                registered = True

                # Add the game to the user's game history
                game = Game(user=user, level=level, time_taken=time_taken,
                            was_won=was_won, score=int(score))
                game.save()

                # Check the badges that this game unlocked
                user_games = Game.objects.filter(user=user)
                check_game_badges(user=user, user_games=user_games,
                                  level=level, was_won=was_won)

                # Update all the ongoing challenges at the right level
                update_challenges(user=user, level=level, score=score)

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
                    friends_games = sorted(friends_games,
                                           key=lambda g: g.score, reverse=True)

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
                registered = False
                today_game_list = Game.objects.filter(date_played=datetime.now()).order_by('-score')[:5]
                all_time_game_list = Game.objects.all().order_by('-score')[:5]
                friends_games_list = []

        # Current user is not registered
        else:
            registered = False
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
            "friendstart": in_friends_start,
            "registered": registered,
            "was_won": was_won
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

                subject,from_email, to = "A duel to the death, or at least to maiming !", \
                             "badllamagames@gmail.com", target_user.user_email()
                message = "You have been challenged! " + str(current_user.user_name()) + \
                          "bites their thumb at you Sir/Lady. Rise to the challenge " \
                          "and vanquish your rival! The game is afoot! Bad Llama Games"

                htmly = get_template("challenge_email.html")
                con = Context({
                    'reg_user': target_user,
                    'current_user': current_user
                })
                html_message = htmly.render(con)

                msg = EmailMultiAlternatives(subject, message, from_email, [to])
                msg.attach_alternative(html_message, "text/html")
                msg.send()


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
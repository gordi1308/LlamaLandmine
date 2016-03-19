from __future__ import division

from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, render_to_response

from llamalandmine.models import Challenge, Game, RegisteredUser, User, UserBadge, UserFriend

from llamalandmine.forms import UserForm, UserProfileForm
from llamalandmine.minesweeper import GameGrid

import json


def home(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/llamalandmine/play/')
            else:
                return HttpResponse('Your Llama Landmine account is disabled.')
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'home.html', {})


def register(request):

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            profile.save()
            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html',
                  {'user_form': user_form, 'profile_form': profile_form,
                   'registered': registered})


def view_profile(request):
    try:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        return HttpResponseRedirect(reverse('profile', args=reg_user.user.username))

    except RegisteredUser.DoesNotExist:
        return HttpResponseNotFound('Login to view your Profile!')


@login_required
def profile(request, profile_username):

    try:
        # User object with username 'profile_username'
        base_user = User.objects.get(username=profile_username)
        reg_user = RegisteredUser.objects.get(user=base_user)

        # List of badges earned by the user
        badge_filter = UserBadge.objects.filter(user=reg_user)
        sorted(badge_filter, key=lambda b: b.badge_tier)
        badge_list = []
        for badge in badge_filter:
            badge_list.append(badge.badge)

        # List of challenges that the user received and accepted, but hasn't completed yet.
        challenge_list = Challenge.objects.filter(challenged_user=reg_user,
                                                  accepted=True,
                                                  completed=False).order_by('remaining_attempts')[:4]

        # List of all the games played by the user
        user_games = Game.objects.filter(user=reg_user)

        # User's easy games stats
        easy_filter = user_games.filter(level="easy")
        games_played_easy = easy_filter.count()
        games_won_easy = easy_filter.filter(was_won=True).count()
        print games_won_easy
        if games_played_easy is not 0 and games_won_easy is not 0:
            percentage_easy = float(games_won_easy/games_played_easy)*100
        else:
            percentage_easy = 0

        # User's normal games stats
        norm_filter = user_games.filter(level="normal")
        games_played_norm = norm_filter.count()
        games_won_norm = norm_filter.filter(was_won=True).count()
        if games_played_norm > 0:
            percentage_norm = float(games_won_norm/games_played_norm)*100
        else:
            percentage_norm = 0

        # User's hard games stats
        hard_filter = user_games.filter(level="hard")
        games_played_hard = hard_filter.count()
        games_won_hard = hard_filter.filter(was_won=True).count()
        if games_played_hard > 0:
            percentage_hard = float(games_won_hard/games_played_hard)*100
        else:
            percentage_hard = 0

        # Stats of the challenges the user has received and completed
        challenges_received_filter = Challenge.objects.filter(challenged_user=reg_user, completed=True)
        challenges_received_count = challenges_received_filter.count()
        challenges_received_won = challenges_received_filter.filter(winner=reg_user).count()

        # Stats of the challenges the user has issued
        challenges_issued_filter = Challenge.objects.filter(game__in=user_games)
        challenges_issued_count = challenges_issued_filter.count()
        challenges_issued_won = challenges_issued_filter.filter(winner=reg_user).count()

        # Stats of the completed challenges (issued or received)
        challenges_completed = challenges_received_count + challenges_issued_count
        challenges_won = challenges_received_won + challenges_issued_won
        if challenges_completed > 0:
            percent_challenge_win = (challenges_won/challenges_completed)*100
        else:
            percent_challenge_win = 0

        # Highest scores for easy, normal and hard games
        if easy_filter.__len__() > 0:
            easy_high_score = easy_filter.order_by('-score')[0].score
        else:
            easy_high_score = 0
        if norm_filter.__len__() > 0:
            norm_high_score = norm_filter.order_by('-score')[0].score
        else:
            norm_high_score = 0
        if hard_filter.__len__() > 0:
            hard_high_score = hard_filter.order_by('-score')[0].score
        else:
            hard_high_score = 0

        # Friend list of profile owner
        friend_list = UserFriend.objects.filter(user=reg_user)

        current_user = RegisteredUser.objects.get(user=request.user.id)
        are_not_friends = True
        if current_user.id == reg_user.id:
            are_not_friends = False
        for friend in friend_list:
            if friend.friend.user.id is current_user.id:
                are_not_friends = False
                break

        context_dict = {
            "badge_list": badge_list[:4],
            "challenge_list": challenge_list,
            "games_played_easy": games_played_easy,
            "games_won_easy": games_won_easy,
            "percentage_easy": percentage_easy,
            "games_played_norm": games_played_norm,
            "games_won_norm": games_won_norm,
            "percentage_norm": percentage_norm,
            "games_played_hard": games_played_hard,
            "games_won_hard": games_won_hard,
            "percentage_hard": percentage_hard,
            "challenges_received": challenges_received_count,
            "challenges_issued": challenges_issued_count,
            "challenges_won": challenges_won,
            "percent_challenge_win": percent_challenge_win,
            "easy_high": easy_high_score,
            "norm_high": norm_high_score,
            "hard_high": hard_high_score,
            "friend_list": friend_list,
            "profile_username": profile_username,
            "is_your_page": request.user.username is profile_username,
            "are_not_friends": are_not_friends
        }
        return render(request, 'profile.html', context_dict)

    except User.DoesNotExist:
        return HttpResponseNotFound("This user does not exist.")
    except RegisteredUser.DoesNotExist:
        return HttpResponseNotFound("This user does not exist.")


def leaderboard(request):

    # List of games played today
    today_filter = Game.objects.filter(date_played=datetime.now())

    if today_filter.__len__() > 0:
        todaygames = today_filter.order_by('-score')[:20]
    else:
        todaygames = []

    # List of games played ever
    alltimegames = list(Game.objects.all().order_by('-score')[:20])

    try:
        # Current user
        user = RegisteredUser.objects.get(user=request.user.id)

        # Current user's friend list
        friendlist = UserFriend.objects.filter(user=user)

        # Games played by the friends of the current user
        if not friendlist:
            friendsgames = []
        else:
            friendsgames = list(Game.objects.filter(friendlist).order_by('-score')[:20])

    except RegisteredUser.DoesNotExist:
        friendsgames = []

    context_dict = {
        "todaylist": todaygames,
        "alltimelist": alltimegames,
        "friendslist": friendsgames
    }

    return render(request, 'leaderboard.html', context_dict)


def how_to(request):
    return render(request, 'howto.html', {})


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

        # Remove the grid from the request session
        request.session['game_grid'] = None

        return HttpResponse(result)

    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


def game_over(request):
    """View called after a user has finished a game to display the user's score,
    and his position in the leaderboard if he registered,
    or the top five registered players."""

    if request.is_ajax() and request.method == 'GET':

        # Start positions of the leaderboard entries
        today_start = 0
        all_time_start = 0
        in_friends_start = 0

        # List of games played by the user's friends
        friends_games_list = []

        # List of games played today
        today_filter = Game.objects.filter(date_played=datetime.now())
        if today_filter.__len__() > 0:
            today_games = today_filter.order_by('-score')
            today_game_list = today_games[:5]
        else:
            today_games = []
            today_game_list = []

        # List of games played ever
        all_time_filter = Game.objects.all()
        if all_time_filter.__len__() > 0:
            all_time_games = all_time_filter.order_by('-score')
            all_time_game_list = all_time_games[:5]
        else:
            all_time_games = []
            all_time_game_list = []

        if not request.user.is_anonymous():
            try:
                user = RegisteredUser.objects.get(user=request.user)

                # Add the game to the user's game history
                game = Game()
                game.user = user
                game.level = request.GET['level']
                game.time_taken = int(request.GET['time_taken'])
                game.was_won = bool(request.GET['was_won'])
                # ADD SCORE
                game.save()

                # CHECK BADGES

                # CHECK CHALLENGES

                # CREATE CHALLENGE

                # Find the position of this game in today's leaderboard
                if today_games.__len__() > 0:
                    today_position = today_games.index(game)
                    today_start = today_position-3
                    today_game_list = today_games[today_position-2:today_position+2]
                else:
                    today_start = 0
                    today_game_list = []

                # Find the position of this game in all time's leaderboard
                if all_time_games.__len__() > 0:
                    all_time_position = all_time_games.index(game)
                    all_time_start = all_time_position-3
                    all_time_game_list = all_time_games[all_time_position-2:all_time_position+2]
                else:
                    all_time_start = 0
                    all_time_game_list = []

                # Find the position of this game in current user's friends leaderboard
                friends_data_found = False

                friend_list = user.friends.all()
                if friend_list.__len__() > 0:
                    friends_filter = Game.objects.filter(Q(user__in=friend_list) | Q(user=user))
                    if friends_filter.__len__() > 0:
                        friends_games = friends_filter.order_by('-score')
                        if friends_games.__len__() > 0:
                            in_friends_position = friends_games.index(game)
                            in_friends_start = in_friends_position-3
                            friends_games_list = friends_games[in_friends_position-2:in_friends_position+2]
                            friends_data_found = True

                # The user has either no friends, or his friends haven't played any games
                if not friends_data_found:
                    in_friends_start = 0
                    friends_games_list = []

            except RegisteredUser.DoesNotExist:
                pass

        context_dict = {
            "last_score": 0,
            "level": request.GET['level'],
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


@login_required
def userlogout(request):
    logout(request)

    return HttpResponseRedirect('/llamalandmine/')
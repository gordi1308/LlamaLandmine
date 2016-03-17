from __future__ import division

from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from llamalandmine.models import Game, RegisteredUser, Challenge, UserBadge, UserFriend
from llamalandmine.forms import UserForm, UserProfileForm


def home(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/llamalandmine/game/')
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


def game(request):
    return render(request, 'game.html', {})


@login_required
def profile(request):

    try:
        # Currently logged in user
        reg_user = RegisteredUser.objects.get(user=request.user)

        # List of badges earned by the user
        badge_filter = UserBadge.objects.filter(user=reg_user)
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
        easy_high_score = easy_filter.order_by('-score')[0].score
        norm_high_score = norm_filter.order_by('-score')[0].score
        hard_high_score = hard_filter.order_by('-score')[0].score

        # User's friend list
        friend_list = UserFriend.objects.filter(user=reg_user)

        context_dict = {
            "badge_list": badge_list,
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
            "friend_list": friend_list
        }

    except RegisteredUser.DoesNotExist:
        return HttpResponse('You need to log in to see that page.<br/>'
                            '<a href="/llamalandmine/">Back to home page</a>')

    return render(request, 'profile.html', context_dict)


def leaderboard(request):

    todaygames = list(Game.objects.filter(date_played=datetime.now()).order_by('-score')[:20])
    alltimegames = list(Game.objects.all().order_by('-score')[:20])
    try:
        user = RegisteredUser.objects.get(user=request.user.id)
        friendlist = UserFriend.objects.filter(user=user)
        if not friendlist:
            friendsgames = []
        else:
            friendsgames = list(Game.objects.filter(friendlist).order_by('-score')[:20])
    except RegisteredUser.DoesNotExist:
        friendsgames = []

    context_dict = {
        "todaylist" : todaygames,
        "alltimelist" : alltimegames,
        "friendslist" : friendsgames
    }

    return render(request, 'leaderboard.html', context_dict)


def how_to(request):
    return render(request, 'howto.html', {})


def game_over(request, lastgame):

    todaygames = list(Game.objects.filter(date_played=lastgame.date_played).order_by('-score'))
    position = todaygames.index(lastgame)
    todaylist = todaygames[position-2:position+2]

    alltimegames = list(Game.objects.all().order_by('-score'))
    atposition = alltimegames.index(lastgame)
    alltimelist = alltimegames[atposition-2:atposition+2]

    friendlist = lastgame.user.friends.all()
    friendsgames = list(Game.objects.filter(friendlist).order_by('-score'))
    fposition = friendsgames.index(lastgame)
    friendsgameslist = friendsgames[atposition-2:atposition+2]

    context_dict = {
        "todaylist" : todaylist,
        "alltimelist" : alltimelist,
        "friendslist" : friendsgameslist,
        "todaystart" : position - 3,
        "atstart" : atposition - 3,
        "friendstart" : fposition - 3,
        "lastscore" : lastgame.score
    }

    return render(request, 'game_over.html', context_dict)


@login_required
def userlogout(request):
    logout(request)

    return HttpResponseRedirect('/llamalandmine/')
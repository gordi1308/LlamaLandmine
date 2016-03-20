# -*- coding: utf-8 -*-

from __future__ import division

from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, \
    Request, User, UserBadge, UserFriend

from llamalandmine.forms import UserForm

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

    if request.user.is_authenticated():
        registered = True

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            username = request.POST.get("username")
            password = request.POST.get("password")
            registered = True

            reg_user = RegisteredUser.objects.get_or_create(user=user)[0]
            reg_user.save()
            reg_user = authenticate(username=username, password=password)
            login(request, reg_user)
            return HttpResponseRedirect('/llamalandmine/how_to/', {'registered': registered})

        else:
            print user_form.errors

    else:
        user_form = UserForm()

    return render(request, 'register.html',
                  {'user_form': user_form, 'registered': registered})


def view_profile(request):
    try:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        return HttpResponseRedirect(reverse('profile', args=reg_user.user_name()))

    except RegisteredUser.DoesNotExist:
        return HttpResponseNotFound('Login to view your Profile!')


@login_required(login_url='/llamalandmine/')
def profile(request, profile_username):

    # User object with username 'profile_username'
    base_user = User.objects.get(username=profile_username)
    profile_owner = RegisteredUser.objects.get(user=base_user)

    # Friend list of profile owner
    friend_list = UserFriend.objects.filter(user=profile_owner)
    friends = []
    if friend_list.__len__() > 0:
        for entry in friend_list:
            friends.append(entry.friend)

    current_user = RegisteredUser.objects.get(user=request.user.id)

    is_current_user_page = request.user.username == profile_username

    # If the current user is looking at another user's profile, are they already friends?
    are_friends = False

    if is_current_user_page:
        are_friends = True
    elif current_user.id != profile_owner.id:
        for friend in friend_list:
            if friend.friend.user.id is current_user.id:
                are_friends = True
                break

    # Loading the profile of the user with username 'profile_username'
    if request.method == 'GET':

        try:
            # List of badges earned by the user
            badge_filter = UserBadge.objects.filter(user=profile_owner)
            sorted(badge_filter, key=lambda b: b.badge_tier)
            badge_list = []
            for i in range(badge_filter.count()-1, 0, -1):
                badge_list.append(badge_filter[i].badge)

            # List of challenges that the user received and accepted, but hasn't completed yet.
            challenge_list = Challenge.objects.filter(challenged_user=profile_owner,
                                                      accepted=True,
                                                      completed=False).order_by('remaining_attempts')[:4]

            # List of all the games played by the user
            user_games = Game.objects.filter(user=profile_owner)

            # User's easy games stats
            easy_filter = user_games.filter(level="easy")
            games_played_easy = easy_filter.count()
            games_won_easy = easy_filter.filter(was_won=True).count()
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
            challenges_received_filter = Challenge.objects.filter(challenged_user=profile_owner, completed=True)
            challenges_received_count = challenges_received_filter.count()
            challenges_received_won = challenges_received_filter.filter(winner=profile_owner).count()

            # Stats of the challenges the user has issued
            challenges_issued_filter = Challenge.objects.filter(game__in=user_games)
            challenges_issued_count = challenges_issued_filter.count()
            challenges_issued_won = challenges_issued_filter.filter(winner=profile_owner).count()

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

            # Pending friend requests
            request_list = Request.objects.filter(target=profile_owner)
            request_shortlist = []

            if request_list.__len__() > 0:
                if request_list.__len__() >= 4:
                    request_nb = 4
                else:
                    request_nb = request_list.__len__()

                for i in range(request_nb):
                    request_shortlist.append(request_list[i].user.user_name())

            context_dict = {
                "current_user_id": current_user.user.id,
                "current_user_name": current_user.user_name(),
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
                "friend_list": friends,
                "profile_username": profile_username,
                "is_your_page": is_current_user_page,
                "are_friends": are_friends,
                "request_list": request_shortlist
            }

            return render(request, 'profile.html', context_dict)

        except User.DoesNotExist:
            return HttpResponseNotFound("This user does not exist.")
        except RegisteredUser.DoesNotExist:
            return HttpResponseNotFound("This user does not exist.")

    elif request.is_ajax() and request.method == 'POST':

        if not are_friends:
            friend_request = Request(user=current_user, target=profile_owner)
            friend_request.save()
            message = str("Dearest "+ profile_owner.user.username + ", " + current_user.user_name() + \
                      " would like to form a most brilliant partnership with you. Like Holmes and Watson, Batman and Robin " \
                      "or Llamas and EXTREME SKYDIVING….ok, so maybe not the last one... There you will traverse " \
                      "minefields and rescue Llamas. Merriment awaits! Bad Llama Games")
            html_message = loader.render_to_string("friend_email.html", {
                'reg_user.user.username': profile_owner.user_name(),
                'current_user.user.username': current_user.user_name()
            })
            send_mail("A partnership of catastrophic proportions!", message, "donotreply@badllamagames.com",
                      [profile_owner.user_email()], html_message)

    return HttpResponseRedirect(reverse("profile", args=(profile_username,)))


def handle_requests(request):

    from_user_name = request.POST['from']
    from_user = User.objects.get(username=from_user_name)
    from_reg_user = RegisteredUser.objects.get(user=from_user)
    print request.POST['accept']
    accepted = bool(request.POST['accept'])
    print accepted

    current_user = RegisteredUser.objects.get(user=request.user.id)

    if accepted:
        friendship = UserFriend(user=current_user, friend=from_reg_user)
        friendship.save()
        friendship = UserFriend(user=from_reg_user, friend=current_user)
        friendship.save()

    Request.objects.get(user=from_reg_user, target=current_user).delete()

    request_list = Request.objects.filter(target=current_user)
    request_shortlist = []
    if request_list > 0:
        if request_list.__len__() >= 4:
            request_nb = 4
        else:
            request_nb = request_list.__len__()

        for i in range(request_nb):
            request_shortlist.append(request_list[i].user.user_name())

    return HttpResponse(json.dumps(request_shortlist))


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
            friendsgames = list(Game.objects.filter(user__in=friendlist).order_by('-score')[:20])

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


def check_badges_friends(user, friend_list):

    if friend_list.__len__() == 1:
        badge = Badge.objects.get(name ="Phone a Friend")
        UserBadge.objects.get_or_create(user=user, badge=badge)

    elif friend_list.__len__() == 5:
        badge = Badge.objects.get(name ="Gondor calls for aid!")
        UserBadge.objects.get_or_create(user=user, badge=badge)


@login_required
def userlogout(request):
    logout(request)

    return HttpResponseRedirect('/llamalandmine/')

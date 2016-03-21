# -*- coding: utf-8 -*-

from __future__ import division

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, \
    Request, User, UserBadge, UserFriend

import json


def view_profile(request):
    try:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        return HttpResponseRedirect(reverse('profile', args=reg_user.user_name()))

    except RegisteredUser.DoesNotExist:
        return HttpResponseRedirect('/llamalandmine/restricted/')


@login_required(login_url='/llamalandmine/restricted/')
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

            pending_challenges = Challenge.objects.filter(challenged_user=profile_owner,
                                                          accepted=False)[:4]

            # List of all the games played by the user
            user_games = Game.objects.filter(user=profile_owner)

            # Profile owner's stats
            easy_stats = get_user_games_stats(user_games=user_games, level='easy')
            normal_stats = get_user_games_stats(user_games=user_games, level='normal')
            hard_stats = get_user_games_stats(user_games=user_games, level='hard')

            challenges_received = get_user_challenges_stats(profile_owner=profile_owner,
                                                            user_games=user_games, received=True)
            challenges_issued = get_user_challenges_stats(profile_owner=profile_owner,
                                                          user_games=user_games, received=False)

            # Stats of the completed challenges (issued or received)
            challenges_completed = challenges_received['challenges_count'] + challenges_issued['challenges_count']
            challenges_won = challenges_received['challenges_won'] + challenges_issued['challenges_won']

            if challenges_completed > 0:
                percent_challenge_win = (challenges_won/challenges_completed)*100
            else:
                percent_challenge_win = 0

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
                "pending_challenges": pending_challenges,
                "games_played_easy": easy_stats['games_played_count'],
                "games_won_easy": easy_stats['games_won_count'],
                "percentage_easy": easy_stats['percentage'],
                "games_played_norm": normal_stats['games_played_count'],
                "games_won_norm": normal_stats['games_won_count'],
                "percentage_norm": normal_stats['percentage'],
                "games_played_hard": hard_stats['games_played_count'],
                "games_won_hard": hard_stats['games_won_count'],
                "percentage_hard": hard_stats['percentage'],
                "challenges_received": challenges_received['challenges_count'],
                "challenges_issued": challenges_issued['challenges_count'],
                "challenges_won": challenges_won,
                "percent_challenge_win": percent_challenge_win,
                "easy_high": easy_stats['high_score'],
                "norm_high": normal_stats['high_score'],
                "hard_high": hard_stats['high_score'],
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
            message = str("Dearest "+ profile_owner.user.username + ", " + current_user.user_name() +
                          " would like to form a most brilliant partnership with you. "
                          "Like Holmes and Watson, Batman and Robin "
                          "or Llamas and EXTREME SKYDIVING….ok, so maybe not the last one... "
                          "There you will traverse minefields and rescue Llamas. "
                          "Merriment awaits! Bad Llama Games")
            html_message = loader.render_to_string("friend_email.html", {
                'reg_user.user.username': profile_owner.user_name(),
                'current_user.user.username': current_user.user_name()
            })
            send_mail("A partnership of catastrophic proportions!", message, "donotreply@badllamagames.com",
                      [profile_owner.user_email()], html_message)

    return HttpResponseRedirect(reverse("profile", args=(profile_username,)))


def get_user_games_stats(user_games, level):

    # User's easy games stats
    games_played = user_games.filter(level=level)
    games_played_count = games_played.count()

    if games_played_count > 0:
        high_score = games_played.order_by('-score')[0].score
    else:
        high_score = 0

    games_won_count = games_played.filter(was_won=True).count()

    if games_played_count is not 0 and games_won_count is not 0:
        percentage = float(games_won_count/games_played_count)*100
    else:
        percentage = 0

    return {
        'games_played_count': games_played_count,
        'games_won_count': games_won_count,
        'percentage': percentage,
        'high_score': high_score
    }


def get_user_challenges_stats(profile_owner, user_games, received):
    if received:
        challenges = Challenge.objects.filter(challenged_user=profile_owner, completed=True)
    else:
        challenges = Challenge.objects.filter(game__in=user_games)

    challenges_count = challenges.count()
    challenges_won = challenges.filter(winner=profile_owner).count()

    return {
        'challenges_count': challenges_count,
        'challenges_won': challenges_won
    }


def handle_requests(request):

    from_user_name = request.POST['from']
    from_user = User.objects.get(username=from_user_name)
    from_reg_user = RegisteredUser.objects.get(user=from_user)
    accepted = bool(request.POST['accept'])

    current_user = RegisteredUser.objects.get(user=request.user.id)

    if accepted:
        friendship = UserFriend(user=current_user, friend=from_reg_user)
        friendship.save()
        friendship = UserFriend(user=from_reg_user, friend=current_user)
        friendship.save()

        friendlist = UserFriend.objects.filter(user=current_user)
        check_badges_friends(user=current_user, friend_list=friendlist)
        friendlist = UserFriend.objects.filter(user=from_reg_user)
        check_badges_friends(user=from_reg_user, friend_list=friendlist)

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


def check_badges_friends(user, friend_list):

    if friend_list.__len__() == 1:
        badge = Badge.objects.get(name ="Phone a Friend")
        UserBadge.objects.get_or_create(user=user, badge=badge)

    elif friend_list.__len__() == 5:
        badge = Badge.objects.get(name ="Gondor calls for aid!")
        UserBadge.objects.get_or_create(user=user, badge=badge)
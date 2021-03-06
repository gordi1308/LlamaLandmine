# -*- coding: utf-8 -*-

from __future__ import division
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from decimal import *

from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, \
    Request, User, UserBadge, UserFriend
from llamalandmine.views.game_views import send_email


def view_profile(request):
    """View called when the currently logged in user wants to see his/her own profile page."""

    try:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        return HttpResponseRedirect(reverse('profile', args=reg_user.user_name()))

    except RegisteredUser.DoesNotExist:
        return HttpResponseRedirect('/llamalandmine/restricted/')


@login_required(login_url='/llamalandmine/restricted/')
def profile(request, profile_username):
    """View called when the currently logged in user wants to see any other user's profile page
    (his/her own included)."""

    context_dict = dict()

    # Profile owner username
    context_dict['profile_username'] = profile_username

    # User object with username 'profile_username'
    base_user = User.objects.get(username=profile_username)
    profile_owner = RegisteredUser.objects.get(user=base_user)

    # Is the currently logged in user looking at his/her own page?
    context_dict['is_your_page'] = request.user.username == profile_username

    # User object corresponding to the user currently logged in
    current_user = RegisteredUser.objects.get(user=request.user.id)

    # Add friend list of profile owner to context dictionary
    get_user_friend_list(profile_owner, context_dict)

    # Pending friend requests of the profile owner
    check_friend_requests(current_user=current_user, profile_owner=profile_owner,
                          context_dict=context_dict)

    # If the current user looking at one of his/her friends profile or his/her own?
    check_users_are_friends(current_user=current_user, profile_owner=profile_owner,
                            context_dict=context_dict)

    # Loading the profile of the user with username 'profile_username'
    if request.method == 'GET':
        try:
            get_profile_owner_stats(profile_owner=profile_owner, context_dict=context_dict,
                                    current_user=current_user)

            return render(request, 'profile.html', context_dict)
        except User.DoesNotExist:
            return HttpResponseNotFound("This user does not exist.")
        except RegisteredUser.DoesNotExist:
            return HttpResponseNotFound("This user does not exist.")

    else:
        # The current user sent a friend request to the profile owner
        if not context_dict['are_friends'] and not context_dict['request_sent']:
            send_friend_request_to_profile_owner(current_user=current_user, profile_owner=profile_owner,
                                             context_dict=context_dict)
            context_dict['request_sent'] = True

    return render(request, 'profile.html', context_dict)


def get_user_friend_list(user, context_dict):
    """Adds the list of friends of the given user to the context dictionary."""
    friend_list = UserFriend.objects.filter(user=user)

    # Get the list of RegisteredUsers who are friends with the given user
    # from the list of UserFriend objects
    friends = []
    if friend_list.__len__() > 0:
        for entry in friend_list:
            friends.append(entry.friend)
    context_dict['friend_list'] = friends


def check_friend_requests(current_user, profile_owner, context_dict):
    """Adds the list of Request objects between the currently logged in and the profile owner
    to the context dictionary."""

    # Requests sent or received to/by the profile owner
    request_list = Request.objects.filter(
        Q(target=profile_owner, user=current_user) |
        Q(user=profile_owner, target=current_user))
    context_dict['request_sent'] = False

    for entry in request_list:
        if current_user.id is entry.user.id or current_user.id is entry.target.id:
            context_dict['request_sent'] = True
            break

    context_dict['request_list'] = Request.objects.filter(target=profile_owner)[:4]


def check_users_are_friends(current_user, profile_owner, context_dict):
    """Adds whether the profile owner is in the current user's friend list,
    or if the current user is on his/her own profile page to the given context dictionary."""

    are_friends = False

    # If it's your page, you can't send a friend request to yourself
    if context_dict['is_your_page']:
        are_friends = True

    elif current_user.id != profile_owner.id:
        for friend in context_dict['friend_list']:
            if friend.id is current_user.id:
                are_friends = True
                break

    context_dict['are_friends'] = are_friends


def get_user_badges(user, context_dict):
    """Adds the list of badges received by the give user to the given context dictionary."""

    badge_filter = list(UserBadge.objects.filter(user=user))

    badge_list = []
    for entry in badge_filter:
        badge_list.append(entry.badge)

    badge_list = sorted(badge_list, key=lambda b: b.tier, reverse=True)

    context_dict['badge_list'] = badge_list
    context_dict['badge_shortlist'] = badge_list[:4]


def get_user_ongoing_challenges(user, context_dict):
    """Adds the list of challenges that the user accepted but hasn't completed yet
    to the given context dictionary."""

    challenges = Challenge.objects.filter(challenged_user=user, accepted=True,
                                          completed=False).order_by('remaining_attempts')[:4]
    context_dict['ongoing_challenges'] = challenges


def get_user_pending_challenges(user, context_dict):
    """Adds the list of challenges that the user hasn't accepted yet
    to the given context dictionary."""

    challenges = Challenge.objects.filter(challenged_user=user, accepted=False)[:4]
    context_dict['pending_challenges'] = challenges


def get_user_completed_challenges_stats(user, user_games, context_dict):
    """Adds user stats related to challenges to the given context dictionary."""

    challenges_received = get_user_challenges_stats(profile_owner=user,
                                                    user_games=user_games, received=True)
    context_dict['challenges_received'] = challenges_received['challenges_count']

    challenges_issued = get_user_challenges_stats(profile_owner=user,
                                                  user_games=user_games, received=False)
    context_dict['challenges_issued'] = challenges_issued['challenges_count']

    # Stats of the completed challenges (issued or received)
    challenges_completed = challenges_received['challenges_count'] + challenges_issued['challenges_count']
    challenges_won = challenges_received['challenges_won'] + challenges_issued['challenges_won']
    context_dict['challenges_won'] = challenges_won

    if challenges_completed > 0:
        percent_challenge_win = (challenges_won/challenges_completed)*100
    else:
        percent_challenge_win = 0
    context_dict['percent_challenge_win'] = percent_challenge_win


def get_profile_owner_stats(current_user, profile_owner, context_dict):
    """Adds user stats related to games played and won to the given context dictionary."""

    try:
        # List of badges earned by the user
        get_user_badges(user=profile_owner, context_dict=context_dict)

        # List of challenges that the user received and accepted, but hasn't completed yet.
        get_user_ongoing_challenges(user=profile_owner, context_dict=context_dict)

        # List of challenges that the user received and hasn't accepted or declined yet
        get_user_pending_challenges(user=profile_owner, context_dict=context_dict)

        # List of all the games played by the user
        user_games = Game.objects.filter(user=profile_owner)

        # Profile owner's stats
        easy_stats = get_user_games_stats(user_games=user_games, level='easy')
        normal_stats = get_user_games_stats(user_games=user_games, level='normal')
        hard_stats = get_user_games_stats(user_games=user_games, level='hard')

        context_dict['games_played_easy'] = easy_stats['games_played_count']
        context_dict['games_won_easy'] = easy_stats['games_won_count']
        context_dict['percentage_easy'] = easy_stats['percentage']
        context_dict['games_played_norm'] = normal_stats['games_played_count']
        context_dict['games_won_norm'] = normal_stats['games_won_count']
        context_dict['percentage_norm'] = normal_stats['percentage']
        context_dict['games_played_hard'] = hard_stats['games_played_count']
        context_dict['games_won_hard'] = hard_stats['games_won_count']
        context_dict['percentage_hard'] = hard_stats['percentage']
        context_dict['easy_high'] = easy_stats['high_score']
        context_dict['norm_high'] = normal_stats['high_score']
        context_dict['hard_high'] = hard_stats['high_score']

        get_user_completed_challenges_stats(user=profile_owner, user_games=user_games,
                                            context_dict=context_dict)

    except User.DoesNotExist:
        raise User.DoesNotExist
    except RegisteredUser.DoesNotExist:
        raise RegisteredUser.DoesNotExist


def send_friend_request_to_profile_owner(current_user, profile_owner):
    """Sends friend request to profile owner from current user."""

    friend_request = Request(user=current_user, target=profile_owner)
    friend_request.save()
    send_email(target_user=profile_owner, current_user=current_user, status="request sent")


def get_user_games_stats(user_games, level):
    """Returns a dictionary containing the user stats related to games played and won."""

    # User's easy games stats
    games_played = user_games.filter(level=level)
    games_played_count = games_played.count()

    if games_played_count > 0:
        high_score = games_played.order_by('-score')[0].score
    else:
        high_score = 0

    games_won_count = games_played.filter(was_won=True).count()

    if games_played_count is not 0 and games_won_count is not 0:
        percentage = Decimal((games_won_count/games_played_count)*100).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    else:
        percentage = 0

    return {
        'games_played_count': games_played_count,
        'games_won_count': games_won_count,
        'percentage': percentage,
        'high_score': high_score
    }


def get_user_challenges_stats(profile_owner, user_games, received):
    """Returns a dictionary containing the user stats related to challenges."""

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
    """View called when the user accepts or declines a friend request."""

    if request.is_ajax() and request.method == 'POST':

        from_user_name = request.POST['item']
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
        return HttpResponse()

    else:
        return HttpResponseNotFound("<h1>Page not found</h1>")


def check_badges_friends(user, friend_list):
    """Checks which badges the user unlocked when added a new friend."""

    if friend_list.__len__() <= 5:
        if friend_list.__len__() == 1:
            badge = Badge.objects.get(name ="Phone a Friend")
            UserBadge.objects.get_or_create(user=user, badge=badge)

        elif friend_list.__len__() == 5:
            badge = Badge.objects.get(name ="Gondor calls for aid!")
            UserBadge.objects.get_or_create(user=user, badge=badge)


def handle_challenges(request):
    """View called when the user accepts or declines a challenge request."""

    if request.is_ajax() and request.method == 'POST':

        try:
            challenge = Challenge.objects.get(id=int(request.POST['item']))
            accepted = bool(request.POST['accept'])

            if accepted:
                challenge.accepted = True
                challenge.save()

                if challenge.game.level == 'hard':
                    name = "It's a bold strategy Cotton!"
                elif challenge.game.level == 'normal':
                    name = "Handbags at dawn"
                else:
                    name = "I swear by my pretty floral bonnet I will end you"

                badge = Badge.objects.get(name=name)
                UserBadge.objects.get_or_create(user=challenge.challenged_user,
                                                badge=badge)
            else:
                challenge.delete()

        except Challenge.DoesNotExist:
            pass

        return HttpResponse()

    else:
        return HttpResponseNotFound("<h1>Page not found</h1>")
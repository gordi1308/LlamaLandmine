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


def game(request, level):
    """View called when the user chooses the level of the game he/she wants to play at."""

    # Grid data
    game_grid = GameGrid(level)
    request.session['game_grid'] = game_grid

    context_dict = {
        'level': level,
        'size': game_grid.size,
        'size_range': range(game_grid.size),
        'llamas': game_grid.nb_llamas,
        'mines': game_grid.nb_mines
    }

    return render(request, 'game.html', context_dict)


def play(request):
    """View called when the user has to be redirected to a default game page."""

    level = 'normal'
    return HttpResponseRedirect(reverse("game", args=(level,)))


def get_grid_data(request):
    """View called when the user clicks on a cell in during the game."""

    if request.is_ajax() and request.method == 'GET':
        # Coordinates of the cell the user clicked on
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

        score = ((get_time_score(level)-(time_taken*10)) + (500*llamas_found))
        if not was_won:
            score *= 0.25
        score *= get_multiplier(level)

        # Remove the grid from the request session
        request.session['game_grid'] = None

        # Default start positions of the leaderboard entries
        today_start = 1
        all_time_start = 1
        in_friends_start = 1

        game = None
        registered = False
        today_game_list = Game.objects.filter(date_played=datetime.now()).order_by('-score')[:5]
        all_time_game_list = Game.objects.all().order_by('-score')[:5]
        friends_games_list = []

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

                # Show the user's game, with two games before and two games after (if any)
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

                    # Show the user's game, with two games before and two games after (if any)
                    friends_games_list = friends_games[in_friends_start:in_friends_start+5]

            # Current user was not recognised
            except RegisteredUser.DoesNotExist:
                pass

        context_dict = {
            "last_score": int(score),
            "last_game": game,
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


def get_time_score(level):
    """Calculates a score to user based on the time he/she took."""

    if level == "easy":
        time_score = 1200
    elif level == "normal":
        time_score = 3000
    else:
        time_score = 6000

    return time_score


def get_multiplier(level):
    """Returns a multiplier to be applied to user's score based on the game difficulty."""

    multiplier = 1
    if level == "normal":
        multiplier = 1.5
    elif level == "hard":
        multiplier = 2

    return multiplier


def check_game_badges(user, user_games, level, was_won):
    """Check which badges the user unlocked after his/her last game."""

    all_badges_count = Badge.objects.all().count()
    user_badges_count = user.earned_badges.count()

    if user_badges_count < all_badges_count:
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

            if user_wins.__len__() >= 1:
                badge = Badge.objects.get(name="Chicken Dinner")
                UserBadge.objects.get_or_create(user=user, badge=badge)

            elif user_wins.__len__() >= 10:
                if level == 'easy':
                    badge = Badge.objects.get(name="You wanna be a big cop in a small town?")
                elif level == 'normal':
                    badge = Badge.objects.get(name="One small step for Man...")
                else:
                    badge = Badge.objects.get(name="One giant leap for Llama-kind")
                UserBadge.objects.get_or_create(user=user, badge=badge)

            elif user_wins.__len__() >= 25:
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

        user_badges_count = user.earned_badges.count()
        if user_badges_count == all_badges_count - 1:
            badge = Badge.objects.get(name="Collect all the badges!")
            UserBadge.objects.get_or_create(user=user, badge=badge)


def update_challenges(user, level, score):
    """Decreases the number of remaining attempts for the user's ongoing challenges,
    checks checks whether the user's last game's score is enough to beat them."""

    challenges = Challenge.objects.filter(challenged_user=user, accepted=True,
                                          completed=False, game__level=level)

    if challenges:
        for challenge in challenges:
            if score >= challenge.score_to_beat():
                challenge.winner = user
                challenge.completed = True
                # Send notification to user who created the challenge
                send_email(target_user=challenge.challenger(), current_user=user,
                           status="challenge lost")
                challenge.save()
            else:
                challenge.remaining_attempts -= 1
                if challenge.remaining_attempts is 0:
                    challenge.completed = True
                    # Send notification to user who created the challenge
                    send_email(target_user=challenge.challenger(), current_user=user,
                               status="challenge won")
                challenge.save()

        check_challenge_badges(user)


def check_challenge_badges(user):
    """Checks which badges the user unlocked after having updated his challenges."""

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
    """Sends a challenge to a friend of the user."""

    if request.is_ajax() and request.method == 'POST':

        try:
            target_name = request.POST['to']
            target = User.objects.get(username=target_name)
            target_user = RegisteredUser.objects.get(user=target)
            current_user = RegisteredUser.objects.get(user=request.user)

            friend_filter = UserFriend.objects.filter(user=current_user)
            friend_list = []
            for entry in friend_filter:
                friend_list.append(entry.friend)

            if target_user in friend_list:
                # Get the current user's latest game
                game = Game.objects.filter(user=current_user).order_by('-id')[0]
                Challenge.objects.create(challenged_user=target_user, game=game)
                send_email(target_user=target_user, current_user=current_user, status="challenge sent")
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


def send_email(target_user, current_user, status):
    """Sends an email notification to the given target user."""

    from_email = "badllamagames@gmail.com"
    to = target_user.user_email()
    message = ""

    if status == "challenge sent":
        subject = "A duel to the death, or at least until maiming or serious injury!"
        htmly = get_template("emails/challenge_email.html")
        con = Context({
            'challenge_sender': current_user,
            'challenge_receiver': target_user
        })

    elif status == "challenge won":
        subject = "Congratulations your opponent has failed your challenge!"
        htmly = get_template("emails/challenge_won.html")
        con = Context({
            'challenge_sender': target_user,
            'challenge_receiver': current_user
        })

    elif status == "challenge lost":
        subject = "Comiserations your opponent had defeated your challenge!"
        htmly = get_template("emails/challenge_loss.html")
        con = Context({
            'challenge_sender': target_user,
            'challenge_receiver': current_user
        })

    else:
        subject = "A partnership of catastrophic proportions!"
        htmly = get_template("emails/friend_email.html")
        con = Context({
            'request_sender': current_user,
            'request_receiver': target_user
        })

    html_message = htmly.render(con)

    msg = EmailMultiAlternatives(subject, message, from_email, [to])
    msg.attach_alternative(html_message, "text/html")
    msg.send()

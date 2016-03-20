from __future__ import division

from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from llamalandmine.models import Game, RegisteredUser, UserFriend

from llamalandmine.forms import UserForm


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


def restricted(request):
    return render(request, 'restricted.html', {})


@login_required
def userlogout(request):
    logout(request)

    return HttpResponseRedirect('/llamalandmine/')

from django.shortcuts import render
from llamalandmine.models import Game, RegisteredUser, User
from datetime import datetime
from llamalandmine.forms import UserForm, UserProfileForm


def home(request):
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

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def game(request):
    return render(request, 'game.html', {})


def profile(request):
    return render(request, 'profile.html', {})


def leaderboard(request):

    todaygames = list(Game.objects.filter(date_played=datetime.now()).order_by('-score')[:20])
    alltimegames = list(Game.objects.all().order_by('-score')[:20])
    try:
        user = RegisteredUser.objects.get(user=request.user.id)
        friendlist = user.friends.all()
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


def edit_profile(request):
    return render(request, 'editprof.html', {})
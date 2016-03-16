from __future__ import division
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from llamalandmine.models import Game, RegisteredUser, Challenge, UserBadge, UserFriend
from datetime import datetime
from llamalandmine.forms import UserForm, UserProfileForm

def intro(request):
    return render (request, 'intro.html', {})

def home(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/game/')
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

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def game(request):
    return render(request, 'game.html', {})


def profile(request):
    base_user = User.objects.get_or_create(username=request.user.username)[0]
    reguser = RegisteredUser.objects.get_or_create(user=base_user)[0]
    reguser.save()
    badgelist = list(UserBadge.objects.filter(user=reguser))
    challengelist = Challenge.objects.filter(challenged_user=reguser, accepted=True, completed=False).order_by('remaining_attempts')[:4]

    usereasyfilter = Game.objects.filter(user=reguser, level="easy")
    usergameseasy = list(usereasyfilter).__len__()
    usereasywonfilter = Game.objects.filter(user__in=usereasyfilter, was_won=True)
    usergameseasywon = usereasywonfilter.count()
    if usergameseasy is not 0 and usergameseasywon is not 0:
        usergameseasypct = float(usergameseasywon/usergameseasy)*100
    else:
        usergameseasypct = 0

    usernormfilter = Game.objects.filter(user=reguser, level="normal")
    usergamesnorm = list(usernormfilter).__len__()
    usernormwonfilter = Game.objects.filter(user__in=usernormfilter, was_won=True)
    usergamesnormwon = usernormwonfilter.count()
    if usergamesnorm > 0:
        usergamesnormpct = float(usergamesnormwon/usergamesnorm)*100
    else:
        usergamesnormpct = 0

    userhardfilter = Game.objects.filter(user=reguser, level="normal")
    usergameshard = list(userhardfilter).__len__()
    userhardwonfilter = Game.objects.filter(user__in=userhardfilter, was_won=True).count()
    usergameshardwon = userhardwonfilter
    if usergameshard > 0:
        usergameshardpct = float(usergameshardwon/usergameshard)*100
    else:
        usergameshardpct = 0

    userchallengefilter = Challenge.objects.filter(challenged_user=reguser, completed=True)
    userchallenge = userchallengefilter.count()
    userchallengewonfilter = Challenge.objects.filter(id__in=userchallengefilter, winner=reguser)
    userchallengewon = userchallengewonfilter.count()
    if userchallenge > 0:
        userchallengepercent = (userchallengewon/userchallenge)*100
    else:
        userchallengepercent = 0

    usereasyhigh = Game.objects.filter(user=reguser, level="easy").order_by('-score')[:1]
    usernormhigh = Game.objects.filter(user=reguser, level="normal").order_by('-score')[:1]
    userhardhigh = Game.objects.filter(user=reguser, level="hard").order_by('-score')[:1]
    friendlist = UserFriend.objects.filter(user=reguser)

    context_dict = {
        "clem": reguser,
        "badgelist": badgelist,
        "challengelist": challengelist,
        "usergameplayedeasy": usergameseasy,
        "usergamewoneasy": usergameseasywon,
        "userpercentageeasy": usergameseasypct,
        "usergameplayednorm": usergamesnorm,
        "usergamewonnorm": usergamesnormwon,
        "userpercentagenorm": usergamesnormpct,
        "usergameplayedhard": usergameshard,
        "usergamewonhard": usergameshardwon,
        "userpercentagehard": usergameshardpct,
        "userchallenge": userchallenge,
        "userchallengewon": userchallengewon,
        "userchallengepercent": userchallengepercent,
        "usereasyhigh": usereasyhigh,
        "usernormhigh": usernormhigh,
        "userhardhigh": userhardhigh,
        "friendlist": friendlist
    }

    return render(request, 'profile.html', context_dict)


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
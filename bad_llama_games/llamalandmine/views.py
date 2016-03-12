from django.shortcuts import render


def home(request):
    return render(request, 'home.html', {})


def register(request):
    return render(request, 'register.html', {})


def game(request):
    return render(request, 'game.html', {})


def profile(request):
    return render(request, 'profile.html', {})


def leaderboard(request):
    return render(request, 'leaderboard.html', {})


def how_to(request):
    return render(request, 'howto.html', {})


def game_over(request):
    return render(request, 'game_over.html', {})


def edit_profile(request):
    return render(request, 'editprof.html', {})
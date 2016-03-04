from django.db import models
from django.contrib.auth.models import User
from datetime import date


# Model to represent a badge.
class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100)
    tier = models.IntegerField()
    icon = models.ImageField()

    def __unicode__(self):
        return self.name + " " + self.tier


# Model to represent a registered user.
# (Not called User to differentiate from the django User class)
class RegisteredUser(models.Model):
    # Django User object with the default user attributes.
    user = models.OneToOneField(User)
    picture = models.ImageField(blank=True)
    games_played_easy = models.IntegerField(default=0)
    games_played_medium = models.IntegerField(default=0)
    games_played_hard = models.IntegerField(default=0)
    best_score_easy = models.IntegerField(default=0)
    best_score_medium = models.IntegerField(default=0)
    best_score_hard = models.IntegerField(default=0)

    # A user can earn many badges. A badge can be earned by many users.
    earned_badges = models.ManyToManyField(Badge)
    # A user can send friend requests to many users. A user can receive friends requests from many users.
    friends = models.ManyToManyField("self", related_name="friends")

    def __unicode__(self):
        return self.user.username


# Model to represent a game.
class Game(models.Model):
    level = models.CharField(max_length=6)
    was_won = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    date_played = models.DateField(default=date.today)
    time_taken = models.IntegerField(default=0)

    # A user can play one game at time. A game can be played by one user.
    user = models.OneToOneField(RegisteredUser, related_name="current_game")

    def __unicode__(self):
        return self.user.username + " " + self.date + " " + self.score


# Model to represent a challenge.
class Challenge(models.Model):
    score_to_beat = models.IntegerField()
    accepted = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    remaining_attempts = models.IntegerField(default=5)

    # A challenge can be made by one user. A user can make many games.
    challenger = models.ForeignKey(RegisteredUser, related_name='challenges_created')
    # For now, only one user can be challenged at a time.
    challenged_user = models.ForeignKey(RegisteredUser, related_name="challenges_received")
    # A challenge can be won by one user. A user can win many games.
    winner = models.ForeignKey(RegisteredUser, related_name="challenges_won", default=challenger)

    def __unicode__(self):
        return self.challenger + " VS " + self.challenged_user + " " + self.score_to_beat
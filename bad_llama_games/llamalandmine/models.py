from django.db import models
from django.contrib.auth.models import User
from datetime import date


# Model to represent a badge.
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    tier = models.IntegerField(default=1)
    icon = models.ImageField(blank=True)

    def __unicode__(self):
        return self.name + " " + str(self.tier)


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
    earned_badges = models.ManyToManyField(Badge, through='UserBadge')

    # A user can send friend requests to many users. A user can receive friends requests from many users.
    friends = models.ManyToManyField("self", symmetrical=False, through='UserFriend')

    def __unicode__(self):
        return self.user.username

    def user_email(self):
        return self.user.email


class UserBadge(models.Model):
    user = models.ForeignKey(RegisteredUser)
    badge = models.ForeignKey(Badge)

    def badge_name(self):
        return self.badge.name

    def badge_description(self):
        return self.badge.description

    def badge_tier(self):
        return self.badge.tier

    def badge_icon(self):
        return self.badge.icon


class UserFriend(models.Model):
    user = models.ForeignKey(RegisteredUser)
    friend = models.ForeignKey(RegisteredUser, related_name="friend")


# Model to represent a game.
class Game(models.Model):
    level = models.CharField(max_length=6)
    was_won = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)

    # A user can play one game at time. A game can be played by one user.
    user = models.OneToOneField(RegisteredUser, related_name="current_game")

    def __unicode__(self):
        return "Game #" + str(self.id)


# Model to represent a challenge.
class Challenge(models.Model):
    score_to_beat = models.IntegerField()
    accepted = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    remaining_attempts = models.IntegerField(default=5)

    # A challenge can be made by one user. A user can make many games.
    challenger = models.ForeignKey(RegisteredUser, related_name='challenges_created')
    # For now, only one user can be challenged at a time.
    challenged_user = models.ForeignKey(RegisteredUser, related_name='challenges_received')
    # A challenge can be won by one user. A user can win many games.
    winner = models.ForeignKey(RegisteredUser, related_name='challenges_won', null=True)

    def __unicode__(self):
        return self.challenger.user.username + " VS " \
               + self.challenged_user.user.username + " " + \
               str(self.score_to_beat)
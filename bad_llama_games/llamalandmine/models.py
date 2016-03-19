from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Badge(models.Model):
    """Model to represent a badge.
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    tier = models.IntegerField(default=1)
    icon = models.ImageField(blank=True)

    def __unicode__(self):
        return self.name


class RegisteredUser(models.Model):
    """Model to represent a registered user.
    (Not called User to differentiate from the django User class
    """

    # Django User object with the default user attributes.
    user = models.OneToOneField(User)
    picture = models.ImageField(blank=True)

    # A user can earn many badges. A badge can be earned by many users.
    earned_badges = models.ManyToManyField(Badge, through='UserBadge')

    # A user can send friend requests to many users.
    # A user can receive friends requests from many users.
    friends = models.ManyToManyField("self", symmetrical=False, through='UserFriend')

    def __unicode__(self):
        return self.user.username.capitalize()

    def user_name(self):
        return self.user.username

    def user_email(self):
        """
        :return: the email of the user
        """
        return self.user.email


class UserBadge(models.Model):
    """Model to handle the many-to-many relationship between a user and a badge.
    """

    user = models.ForeignKey(RegisteredUser)
    badge = models.ForeignKey(Badge)

    def __unicode__(self):
        return self.badge.name

    def badge_name(self):
        return self.badge.name

    def badge_description(self):
        return self.badge.description

    def badge_tier(self):
        return self.badge.tier

    def badge_icon(self):
        return self.badge.icon


class UserFriend(models.Model):
    """Model to handle the many-to-many relationship between a user and another user.
    """

    user = models.ForeignKey(RegisteredUser)
    friend = models.ForeignKey(RegisteredUser, related_name="friend")


class FriendRequest(models.Model):
    """Model to handle Friend Requests between Users
    """


class Game(models.Model):
    """Model to represent a game.
    """

    level = models.CharField(max_length=6)
    was_won = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)
    date_played = models.DateField(default=datetime.now())

    # A user can play many games. A game can be played by one user.
    user = models.ForeignKey(RegisteredUser, related_name="game")

    def __unicode__(self):
        return self.user.__unicode__() + " - " + \
               self.date_played.strftime('%d/%m/%Y')


class Challenge(models.Model):
    """Model to represent a challenge.
    """

    # One user can be challenged at a time.
    challenged_user = models.ForeignKey(RegisteredUser,
                                        related_name='challenges_received')

    # Instead of having separate attributes, common with the game the challenge is based on
    # (the level of the game, the user who created the challenge,
    # the score to beat to win the challenge),
    # this class just stores a reference to the corresponding Game object.
    game = models.ForeignKey(Game)

    accepted = models.BooleanField(default=False)
    remaining_attempts = models.IntegerField(default=5)

    completed = models.BooleanField(default=False)

    # A challenge can be won by one user. A user can win many games.
    winner = models.ForeignKey(RegisteredUser,
                               related_name='challenges_won', null=True)

    def __unicode__(self):
        return self.game.user.__unicode__() + " VS " \
               + self.challenged_user.user.username + " - " + \
               str(self.game.score)

    def challenger(self):
        return self.game.user

    def score_to_beat(self):
        return self.game.score
from django.db import models
from django.contrib.auth.models import User


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
    games_played_easy = models.IntegerField(default=0)
    games_played_medium = models.IntegerField(default=0)
    games_played_hard = models.IntegerField(default=0)
    best_score_easy = models.IntegerField(default=0)
    best_score_medium = models.IntegerField(default=0)
    best_score_hard = models.IntegerField(default=0)

    # A user can earn many badges. A badge can be earned by many users.
    earned_badges = models.ManyToManyField(Badge, through='UserBadge')

    # A user can send friend requests to many users.
    # A user can receive friends requests from many users.
    friends = models.ManyToManyField("self", symmetrical=False, through='UserFriend')

    def __unicode__(self):
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


class Game(models.Model):
    """Model to represent a game.
    """

    level = models.CharField(max_length=6)
    was_won = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)

    # A user can play one game at time. A game can be played by one user.
    user = models.OneToOneField(RegisteredUser, related_name="current_game")

    def __unicode__(self):
        return self.user.__unicode__().capitalize() + "'s last game"


class Challenge(models.Model):
    """Model to represent a challenge.
    """

    level = models.CharField(max_length=6, default='easy')
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
               + self.challenged_user.user.username + " - " + \
               str(self.score_to_beat)
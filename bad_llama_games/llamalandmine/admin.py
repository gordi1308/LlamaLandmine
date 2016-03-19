from django.contrib import admin
from llamalandmine.models import Badge, Challenge, Game, RegisteredUser


class BadgeAdmin(admin.ModelAdmin):
    # List of fields to be displayed on the 'badges' admin page
    list_display = ('name', 'tier', 'description')


class BadgeInLine(admin.TabularInline):
    """Class to display a badge earned by a given user
    (on the 'RegisteredUser' admin page).
    """

    # Get the badges earned by the user from the UserBadge table
    model = RegisteredUser.earned_badges.through

    extra = 0

    # Badge attributes to be displayed
    readonly_fields = ('badge_description', 'badge_tier', 'badge_icon',)

    verbose_name = 'Badge'
    verbose_name_plural = 'badges'


class ChallengeAdmin(admin.ModelAdmin):
    # List of fields to be displayed on the 'Challenges' admin page
    list_display = ('id', 'challenger', 'challenged_user', 'score_to_beat', 'winner')

    ordering = ('id',)


class ChallengeInLine(admin.TabularInline):
    """Class to display the challenges received by a given user.
    """
    model = Challenge

    extra = 0

    # Differentiate the user who created the challenge from the user who is challenged
    fk_name = 'challenged_user'

    readonly_fields = ('challenger', 'score_to_beat', 'accepted',
                       'remaining_attempts', 'completed', 'winner')

    verbose_name = 'Challenge received'
    verbose_name_plural = 'Challenges received'


class FriendInLine(admin.TabularInline):
    """Class to display a given user's friend list.
    """
    model = RegisteredUser.friends.through

    extra = 0
    fk_name = 'friend'

    verbose_name = 'Friend'
    verbose_name_plural = 'Friends'


class GameInLine(admin.TabularInline):
    """Class to display the game history of a given user.
    """
    model = Game
    extra = 0

    date_hierarchy = 'date_played'

    verbose_name = 'Last Game'


class RegisteredUserAdmin(admin.ModelAdmin):

    fieldsets = (
        ('User', {'fields': (('user', 'picture'),)}),
    )

    inlines = [GameInLine, BadgeInLine, ChallengeInLine, FriendInLine]

    # List of fields to be displayed on the 'registered users' admin page
    list_display = ('user', 'user_email')


admin.site.register(Badge, BadgeAdmin)
admin.site.register(RegisteredUser, RegisteredUserAdmin)
admin.site.register(Challenge, ChallengeAdmin)

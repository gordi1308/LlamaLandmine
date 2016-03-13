from django.contrib import admin
from llamalandmine.models import Badge, Challenge, Game, RegisteredUser, UserBadge


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'description')


class BadgeInLine(admin.TabularInline):
    model = RegisteredUser.earned_badges.through
    extra = 0
    readonly_fields = ('badge_name', 'badge_description', 'badge_tier', 'badge_icon',)
    verbose_name = 'Badges'


class ChallengeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('challenged_user','challenger', 'score_to_beat',),
                'classes': ('wide',)}),
        (None, {'fields': ('accepted', 'remaining_attempts',),
                'classes': ('wide',)}),
        ('Outcome', {'fields': ('completed', 'winner',),
                     'classes': ('wide',)}),
    )

    list_display = ('id', 'challenger', 'challenged_user', 'score_to_beat', 'winner')

    ordering = ('id',)


class ChallengeInLine(admin.TabularInline):
    model = Challenge
    extra = 0
    fk_name = 'challenged_user'
    verbose_name = 'Ongoing Challenges'
    readonly_fields = ('challenger', 'score_to_beat', 'accepted', 'remaining_attempts',
                       'completed', 'winner')


class FriendInLine(admin.TabularInline):
    model = RegisteredUser.friends.through
    extra = 0
    fk_name = 'friend'
    verbose_name = 'Friends'


class GameInLine(admin.TabularInline):
    model = Game
    date_hierarchy = 'date_played'
    verbose_name = 'Last Game'


class RegisteredUserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User', {'fields': (('user', 'picture'),)}),
        ('Easy Games', {'fields': (('games_played_easy', 'best_score_easy'),),
                        'classes': ('wide',)}),
        ('Medium Games', {'fields': (('games_played_medium', 'best_score_medium'),),
                          'classes': ('wide',)}),
        ('Hard Games', {'fields': (('games_played_hard', 'best_score_hard'),),
                        'classes': ('wide',)}),
    )

    inlines = [GameInLine, BadgeInLine, ChallengeInLine, FriendInLine]

    list_display = ('user', 'user_email')


admin.site.register(Badge, BadgeAdmin)
admin.site.register(RegisteredUser, RegisteredUserAdmin)
admin.site.register(Challenge, ChallengeAdmin)

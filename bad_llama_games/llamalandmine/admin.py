from django.contrib import admin
from llamalandmine.models import Badge, Challenge, Game, RegisteredUser


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'description')


class BadgeInLine(admin.TabularInline):
    model = RegisteredUser.earned_badges.through
    extra = 0
    fields = ('badge_name', 'badge_description', 'badge_tier', 'badge_icon')

    def badge_name(self, instance):
        return instance.badge.name
    badge_name.short_description = 'badge_name'

    def badge_description(self, instance):
        return instance.badge.description
    badge_description.short_description = 'badge_description'

    def badge_tier(self, instance):
        return instance.badge.tier
    badge_tier.short_description = 'badge_tier'

    def badge_icon(self, instance):
        return instance.badge.icon
    badge_icon.short_description = 'badge_icon'


class FriendInLine(admin.TabularInline):
    model = RegisteredUser.friends.through
    extra = 0
    fk_name = 'friend'


class GameInLine(admin.TabularInline):
    model = Game
    date_hierarchy = 'date_played'


class RegisteredUserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User', {'fields': ('user', 'picture',)}),
        ('Easy Games', {'fields': ('games_played_easy', 'best_score_easy',),
                        'classes': ('wide',)}),
        ('Medium Games', {'fields': ('games_played_medium', 'best_score_medium',),
                          'classes': ('wide',)}),
        ('Hard Games', {'fields': ('games_played_hard', 'best_score_hard',),
                        'classes': ('wide',)}),
    )

    inlines = [GameInLine, BadgeInLine, FriendInLine]

    list_display = ('user', 'user_email')


class ChallengeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Badge, BadgeAdmin)
admin.site.register(RegisteredUser, RegisteredUserAdmin)
admin.site.register(Challenge)

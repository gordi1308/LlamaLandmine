from django.contrib import admin
from llamalandmine.models import Badge, Challenge, Game, RegisteredUser


admin.site.register(Badge)
admin.site.register(RegisteredUser)
admin.site.register(Game)
admin.site.register(Challenge)

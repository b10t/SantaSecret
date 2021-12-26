from django.contrib import admin

from .models import Player, Game, PlayersInGame


class PlayersInGameAdmin(admin.ModelAdmin):
    list_filter = ['game']

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(PlayersInGame, PlayersInGameAdmin)

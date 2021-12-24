import random

from django.core.management.base import BaseCommand
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from bot.models import Player, PlayersInGame, Game


def santas_distribution(game_number):
    players = PlayersInGame.objects.filter(game=game_number)
    santas = list(players).copy()

    for player in players:
        while True:
            random_santa = random.choice(santas)
            if random_santa.player is not player.player and random_santa.santa is not player.player:
                player.santa = random_santa.player
                break
        santas.remove(random_santa)


class Command(BaseCommand):
    help = 'Telegram Bot Santa Secret'

    def handle(self, *args, **options):
        # import this
        print('Start Bot')

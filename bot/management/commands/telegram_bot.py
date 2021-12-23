from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Telegram Bot Santa Secret'

    def handle(self, *args, **options):
        # import this
        print('Start Bot')

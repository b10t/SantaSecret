from django.db import models


class Game(models.Model):
    title = models.CharField('Название игры', max_length=250)
    owner = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        verbose_name='Владелец игры',
        related_name='players'
    )
    cash_limit = models.CharField('Бюджет', default='0')
    stop_registration_date = models.DateTimeField('Окончание регистрации')
    sending_gift_date = models.DateField('Дата отправки подарков')

    def __str__(self):
        return f'Игра {self.pk} - {self.title}, владелец {self.owner}'


class Player(models.Model):
    firs_name = models.CharField('Имя', max_length=250)
    last_name = models.CharField('Фамилия', max_length=250, blank=True)
    vk_id = models.CharField('Vk id', max_length=50, unique=True)
    phone = models.CharField('Номер телефона', max_length=20, unique=True)
    mail = models.CharField('Электронная почта', max_length=250, blank=True)
    games = models.ManyToManyField(
        Game,
        verbose_name='Участвует в играх',
        related_name='players_in_game'
    )

    def __str__(self):
        return f'{self.firs_name} {self.last_name} {self.phone}'


class PlayersInGame(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name='Номер игры',
        related_name='games',
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        verbose_name='Участник',
        related_name='players',
    )
    santa = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Тайный Санта',
        related_name='players',
    )

    def __str__(self):
        return f'Игра {self.game.pk}, игрок {self.player}, его Санта {self.santa}'

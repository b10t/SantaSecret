from django.db import models


class Player(models.Model):
    firs_name = models.CharField('Имя', max_length=250)
    last_name = models.CharField('Фамилия', max_length=250, blank=True)
    chat_id = models.IntegerField('Chat id', unique=True)
    phone = models.CharField('Номер телефона', max_length=20, blank=True)
    mail = models.CharField('Электронная почта', max_length=250, blank=True)

    def __str__(self):
        return f'ID: {self.chat_id} имя: {self.firs_name} телефон: {self.phone}'

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


class Game(models.Model):
    title = models.CharField('Название игры', max_length=250)
    owner = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Владелец игры',
        related_name='owner'
    )
    cash_limit = models.CharField('Бюджет', default='0', max_length=25)
    stop_registration_date = models.TextField('Окончание регистрации')
    sending_gift_date = models.TextField('Дата отправки подарков')
    is_finish = models.BooleanField(default=False, blank=False,
                                    db_index=True,
                                    verbose_name='Игра закончена')

    def __str__(self):
        return f'Игра {self.pk}, Название: {self.title}, Владелец: {self.owner}'

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'


class PlayersInGame(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name='Номер игры',
        related_name='game',
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        verbose_name='Участник',
        related_name='player',
    )
    santa = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Тайный Санта',
        related_name='santa',
    )

    def __str__(self):
        return f'Игра {self.game.pk}, игрок {self.player}, его Санта {self.santa}'

    class Meta:
        verbose_name = 'Игрок в игре'
        verbose_name_plural = 'Игроки в игре'

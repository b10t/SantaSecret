import os
import random

from bot.models import Game, Player, PlayersInGame
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, ReplyKeyboardRemove, Update, chat)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)
from telegram.utils import helpers


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def start_handler(update: Update, context: CallbackContext):
    # TODO изменить поле phone в модели Player
    # после исправления проблемы с телефоном

    inl_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    '🎅🏼 Создать игру 🎄',
                    callback_data='CREATE_GAME'
                )
            ],
            [
                InlineKeyboardButton(
                    '🎅🏼 Присоедениться к игре 🎄',
                    callback_data='JOIN_THE_GAME'
                )
            ]
        ]
    )

    user_id = update.message.chat_id
    context.user_data['user_id'] = user_id
    first_name = update.message.chat.first_name
    if update.message.chat.last_name:
        context.user_data['last_name'] = update.message.chat.last_name
    else:
        context.user_data['last_name'] = ''

    database_user_id = Player.objects.filter(chat_id=user_id)
    if not database_user_id:
        Player.objects.create(
            chat_id=user_id,
            firs_name=first_name,
            last_name=context.user_data['last_name'],
        )

    update.message.reply_text(
        f'Привет, {first_name}'
        '🎁 Организуй тайный обмен подарками, \n'
        'запусти праздничное настроение\! 🎁',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inl_keyboard
    )
    return 'callback_create_game'


def callback_create_game(update: Update, context: CallbackContext):
    """Обработчик кнопок по работе с ПД."""
    bot = update.effective_message.bot
    query = update.callback_query

    if query.data == 'CREATE_GAME':
        return send_gamename_question(update, context)
    elif query.data == 'JOIN_THE_GAME':
        return choose_game(update, context)
    else:
        return ConversationHandler.END


def choose_game(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        'Введите номер игры',
        reply_markup=ForceReply(force_reply=True,
                                input_field_placeholder='Номер...',
                                selective=True)
    )
    return 'join_the_game'


def join_the_game(update: Update, context: CallbackContext):

    inl_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    '🎅🏼 Создать игру 🎄',
                    callback_data='CREATE_GAME'
                )
            ],
            [
                InlineKeyboardButton(
                    '🎅🏼 Присоедениться к игре 🎄',
                    callback_data='JOIN_THE_GAME'
                )
            ]
        ]
    )

    number = update.message.text

    player = Player.objects.get(chat_id=context.user_data['user_id'])
    current_game = Game.objects.get(pk=number)
    PlayersInGame.objects.create(game=current_game, player=player)
    
    update.message.reply_text(
        f'Игрок {player.firs_name} присоединился к игре {current_game}',
    )
    return start_handler(update, context)


def send_gamename_question(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        'Введите название игры:',
        reply_markup=ForceReply(force_reply=True,
                                input_field_placeholder='Название игры...',
                                selective=True)
    )
    return 'get_game_name'


def get_game_name(update: Update, context: CallbackContext):
    context.user_data['game_name'] = update.message.text
    return send_cost_gift_question(update, context)


def send_cost_gift_question(update: Update, context: CallbackContext):
    inl_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('💵 До 500 ', callback_data='500RUB')],
            [InlineKeyboardButton('💴 500-1000 ', callback_data='1000RUB')],
            [InlineKeyboardButton('💶 1000-2000 ', callback_data='2000RUB')],
            [InlineKeyboardButton('👎 Нет', callback_data='NO')]
        ]
    )
    update.message.reply_text(
        'Ограничить стоимость подарка ?',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inl_keyboard
    )
    return 'callback_cost_gift'


def callback_cost_gift(update: Update, context: CallbackContext):
    """Обработчик кнопок по работе с ПД."""
    bot = update.effective_message.bot
    query = update.callback_query

    context.user_data['cost_gift'] = query.data

    return send_registration_period_question(update, context)


def send_registration_period_question(update: Update,
                                      context: CallbackContext):
    inl_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                '📆 до 25.12.2021', callback_data='25.12.2021')],
            [InlineKeyboardButton(
                '📆 до 31.12.2021', callback_data=' 2021-12-31 12:00')],
        ]
    )
    update.effective_message.reply_text(
        'Выберите период регистрации участников',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inl_keyboard
    )
    return 'callback_registration_period'


def callback_registration_period(update: Update, context: CallbackContext):
    """Обработчик кнопок по работе с ПД."""
    bot = update.effective_message.bot
    query = update.callback_query

    context.user_data['registration_period'] = query.data

    return send_dispatch_date(update, context)


def send_dispatch_date(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        'Введите дату отправки подарка:',
        reply_markup=ForceReply(force_reply=True,
                                input_field_placeholder='Дата отправки подарка',
                                selective=True)
    )
    return 'get_dispatch_date'


def get_dispatch_date(update: Update, context: CallbackContext):
    context.user_data['dispatch_date'] = update.message.text
    return send_invitation_link(update, context)


def send_invitation_link(update: Update, context: CallbackContext):
    bot = context.bot
    player = Player.objects.get(chat_id=update.message.chat_id)
    Game.objects.create(
        title=context.user_data['game_name'],
        owner=player,
        cash_limit=context.user_data['cost_gift'],
        stop_registration_date=context.user_data['registration_period'],
        sending_gift_date=context.user_data['dispatch_date']
    )

    last_game = Game.objects.last()

    update.effective_message.reply_text(
        'Отлично, Тайный Санта уже готовится к раздаче подарков\!\n\n'
        f'Скажи друзьям номер игры, что бы они могли присоединится {last_game.pk}',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text(
        'Всего доброго!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def santas_distribution(game_number):
    players = PlayersInGame.objects.filter(game=game_number)
    santas = list(players).copy()

    for player in players:
        while True:
            random_santa = random.choice(santas)
            if random_santa.player is not player.player and random_santa.santa is not player.player:
                player.santa = random_santa.player
                player.save()
                break
        santas.remove(random_santa)

    if PlayersInGame.objects.filter(game=game_number, santa=None):
        santas_distribution(game_number)

    players[0].game.is_finish = True


class Command(BaseCommand):
    help = 'Telegram Bot Santa Secret'

    def handle(self, *args, **options):
        print('Start Telegram Bot')
        print('TELEGRAM_TOKEN', TELEGRAM_TOKEN)
        updater = Updater(token=TELEGRAM_TOKEN)

        dispatcher = updater.dispatcher

        conversation = ConversationHandler(
            entry_points=[CommandHandler('start', start_handler)],
            states={
                'callback_create_game': [
                    CallbackQueryHandler(
                        callback_create_game
                    )
                ],
                'join_the_game': [
                    MessageHandler(
                        Filters.text & ~Filters.command,
                        join_the_game
                    )
                ],
                'get_game_name': [
                    MessageHandler(
                        Filters.text & ~Filters.command,
                        get_game_name
                    )
                ],
                'callback_cost_gift': [
                    CallbackQueryHandler(
                        callback_cost_gift
                    )
                ],
                'callback_registration_period': [
                    CallbackQueryHandler(
                        callback_registration_period
                    )
                ],
                'get_dispatch_date': [
                    MessageHandler(
                        Filters.text & ~Filters.command,
                        get_dispatch_date
                    )
                ],
            },
            fallbacks=[
                CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conversation)

        updater.start_polling()
        updater.idle()

# if __name__ == '__main__':
#     load_dotenv()
#     # mode = os.getenv('MODE', 'dev')
#     TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

#     updater = Updater(token=TELEGRAM_TOKEN)

#     dispatcher = updater.dispatcher
#     # dispatcher.add_handler(CommandHandler('start', start_handler))

#     conversation = ConversationHandler(
#         entry_points=[CommandHandler('start', start_handler)],
#         states={
#             'callback_create_game': [
#                 CallbackQueryHandler(
#                     callback_create_game
#                 )
#             ],
#             'get_game_name': [
#                 MessageHandler(
#                     Filters.text & ~Filters.command,
#                     get_game_name
#                 )
#             ],
#             'callback_cost_gift': [
#                 CallbackQueryHandler(
#                     callback_cost_gift
#                 )
#             ],
#             'callback_registration_period': [
#                 CallbackQueryHandler(
#                     callback_registration_period
#                 )
#             ],
#             'get_dispatch_date': [
#                 MessageHandler(
#                     Filters.text & ~Filters.command,
#                     get_dispatch_date
#                 )
#             ],
#         },
#         fallbacks=[
#             CommandHandler('cancel', cancel)],
#     )

#     dispatcher.add_handler(conversation)

#     updater.start_polling()
#     updater.idle()

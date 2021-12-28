import os
import random

from bot.models import Game, Player, PlayersInGame
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup,
                      Update,
                      KeyboardButton)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)


# 🎅🏼🎄💸💵💴💶💷💰🎊🎉✉️📨💌📅📆🗓🎁


def start_handler(update: Update, context: CallbackContext):
    SEND_CONTACT_KEYBOARD = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton('Ручной ввод'),
                KeyboardButton('Отправить контакт', request_contact=True)
            ]
        ],
        resize_keyboard=True
    )

    message = update.message
    user_name = message.chat.first_name
    user_id = message.chat_id
    context.user_data['user_id'] = user_id
    # Если пользователь в базе пропустить этот шаг
    database_user_id = Player.objects.filter(chat_id=user_id)
    if not database_user_id:
        update.message.reply_text(
            f"Привет, {user_name}!🤚\n\n"
            "Для участия в игре необходимо указать контактный номер телефона.",
            reply_markup=SEND_CONTACT_KEYBOARD,
        )
        return "ask_contact"
    else:
        inl_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton('🎅🏼 Создать игру 🎄',
                                   callback_data='CREATE_GAME')]]
        )

        update.message.reply_text(
            '🎁 Организуй тайный обмен подарками, \n'
            'запусти праздничное настроение! 🎁',
            reply_markup=inl_keyboard,
        )
        return 'callback_create_game'


def ask_contact(update, context):
    message = update.message
    user_id = message.chat_id
    if message.contact:
        phone = message.contact.phone_number
        context.user_data['phone'] = phone
        update.message.reply_text(
            f'Контактный номер {phone} сохранен\n\n',
            reply_markup=ReplyKeyboardRemove()
        )

        inl_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton('🎅🏼 Создать игру 🎄',
                                   callback_data='CREATE_GAME')]]
        )

        update.message.reply_text(
            '🎁 Организуй тайный обмен подарками, \n'
            'запусти праздничное настроение 🎁',
            reply_markup=inl_keyboard
        )
        return 'callback_create_game'

    elif message.text == "Ручной ввод":
        update.message.reply_text(
            'Введите номер телефона в формате +71231231212',
            reply_markup=ReplyKeyboardRemove(),
        )
        return 'save_phone_number'


def save_phone_number(update, context):
    phone = update.message.text
    context.user_data['phone'] = phone
    update.message.reply_text(
        f'Контактный номер {phone} сохранен\n\n',
        reply_markup=ReplyKeyboardRemove()
    )

    inl_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton('🎅🏼 Создать игру 🎄',
                               callback_data='CREATE_GAME')]]
    )

    update.message.reply_text(
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
    else:
        return ConversationHandler.END


def send_gamename_question(update: Update, context: CallbackContext):
    # message = update.message
    # user_id = message.chat_id
    # player, _ = Player.objects.get_or_create(chat_id=user_id, defaults={
    #     "first_name": message.chat.first_name,
    #     "last_name": message.chat.last_name,
    #     "phone": context.user_data['phone'],
    # })
    context.user_data['phone'] = update.message.text
    update.message.reply_text(
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
                '📆 до 31.12.2021', callback_data='31.12.2021')],
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
    player = Player.objects.get(chat_id=update.message.chat_id)
    Game.objects.create(
        title=context.user_data['game_name'],
        owner=player,
        cash_limit=context.user_data['cost_gift'],
        stop_registration_date=context.user_data['registration_period'],
        sending_gift_date=context.user_data['dispatch_date']
    )
    update.effective_message.reply_text(
        'Отлично, Тайный Санта уже готовится к раздаче подарков!',
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

    if PlayersInGame.objects.filter(game=game_number, santas=None):
        santas_distribution(game_number)

    players[0].game.is_finish = True


class Command(BaseCommand):
    help = 'Telegram Bot Santa Secret'

    def handle(self, *args, **options):
        load_dotenv()
        # mode = os.getenv('MODE', 'dev')
        TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

        updater = Updater(token=TELEGRAM_TOKEN)

        dispatcher = updater.dispatcher
        # dispatcher.add_handler(CommandHandler('start', start_handler))

        conversation = ConversationHandler(
            entry_points=[CommandHandler('start', start_handler)],
            states={
                'ask_contact': [
                    MessageHandler(
                        Filters.all & ~Filters.command, ask_contact,
                    )
                ],
                'save_phone_number': [
                    MessageHandler(
                        Filters.text & ~Filters.command, save_phone_number,
                    )
                ],
                'callback_create_game': [
                    CallbackQueryHandler(
                        callback_create_game
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

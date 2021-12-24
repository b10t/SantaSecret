import os

from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

# 🎅🏼🎄💸💵💴💶💷💰🎊🎉✉️📨💌📅📆🗓🎁


def start_handler(update: Update, context: CallbackContext):
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
        bot.answerCallbackQuery(
            callback_query_id=update.callback_query.id,
            text='⛔️ Бот не может продолжить с Вами работу'
                 ' без согласия на сбор ПД.',
            per_message=False)

        # return ConversationHandler.END
    else:
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text(
        'Всего доброго!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


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
                "callback_create_game": [
                    CallbackQueryHandler(
                        callback_create_game
                    )
                ],
            },
            fallbacks=[
                CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conversation)

        updater.start_polling()
        updater.idle()

from urllib.request import Request

# Create your views here.
import logging
import urllib
from os import walk

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # update.message.reply_markdown_v2(
    #     fr'Hi {user.mention_markdown_v2()}\!',
    #     reply_markup=ForceReply(selective=True),
    # )

    update.message.reply_text(f"{update.effective_user.first_name} укажите ИНН Лизингополучателя")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    # update.message.reply_text(update.message.text)

    # update.message.reply_text(str(update.message.text.find("start")))

    # update.message.reply_text("echo" + update.message.text)
    # post_data = [('inn', update.message.text), ]  # a sequence of two element tuples
    # result = requests.post("https://178.57.75.140/cul_2019/hs/amocrm/v1/ping", data=post_data)

    # update.message.reply_text(update.message.text)

    keyboard = [
        [InlineKeyboardButton("Новая заявка", callback_data='0')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message.text.isdigit():
        if len(update.message.text) == 12 or len(update.message.text) == 10:

            if update.message.text[0] == "1":

                update.message.reply_text('Вам предодобрен кредит на сумму до 2млн. руб.')

                keyboard = [
                    [
                        InlineKeyboardButton("12 мес.", callback_data='12'),
                        InlineKeyboardButton("24 мес.", callback_data='24'),
                    ],
                    [InlineKeyboardButton("Новая заявка", callback_data='0')],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text('Укажите срок лизинга:', reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("Новая заявка", callback_data='0')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('В кредите отказано:', reply_markup=reply_markup)
        else:
            answer = "yellow"
            if answer == "red":
                update.message.reply_text("В заявке на лизинг отказано.", reply_markup=reply_markup)
                return
            else:
                update.message.reply_text("Вам одобрены следующие предложения:")
                filenames = next(walk("."), (None, None, []))[2][0:3]
                for file in filenames:
                    in_file = open(file, "rb")  # opening for [r]eading as [b]inary
                    data = in_file.read()
                    in_file.close()
                    update.message.reply_document(document=data, filename=file)
            # elif answer == "green":

            update.message.reply_text(text="Удачных покупок!",reply_markup=reply_markup)

    elif update.message.text.find("start"):
        update.message.reply_text("Укажите ИНН компании")

    # keyboard = [
    #     [
    #         InlineKeyboardButton("Option 1", callback_data='1'),
    #         InlineKeyboardButton("Option 2", callback_data='2'),
    #     ],
    #     [InlineKeyboardButton("Option 3", callback_data='3')],
    # ]
    #
    # reply_markup = InlineKeyboardMarkup(keyboard)
    #
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    if query.data == "0":
        # update.message.reply_text("Укажите ИНН компании")
        update.callback_query.edit_message_text(text="Укажите ИНН компании")
        return

    if query.data == "12" or query.data == "24" or query.data == "32":
        # update.message.reply_text("Укажите ИНН компании")
        update.callback_query.edit_message_text(text="Укажите стоимость ПЛ")
        return

    # query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1732313396:AAGZH9cWQ3nu4wJGnne1Iz8oNM1i6Wz-pWE")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
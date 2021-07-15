# Create your views here.
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import requests
import json
from requests.auth import HTTPBasicAuth

import locale
locale.setlocale(locale.LC_ALL, '')

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

    update.message.reply_text(f"{update.effective_user.first_name}, добро пожаловать в компанию Нацлизинг! "
                              f"Для получения предварительного решения введите ИНН Вашей компании.")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""

    keyboard = [
        [InlineKeyboardButton("Новая заявка", callback_data='0')],
    ]

    if update.message.text.isdigit():

        # Проверяю что ввели ИНН
        if len(update.message.text) == 12 or len(update.message.text) == 10:

            # Пишу ответы пользователя
            file1 = open(f"files/{update.effective_user.id}_answers.txt", "w")
            file1.write(update.message.text + "\n")
            file1.close()

            data = {"inn": update.message.text}

            data_ = json.dumps(data)

            headers = {'Content-Type': 'application/json'}
            result = requests.post("http://10.110.36.30/cul_2019/hs/amocrm/api/get_score_data", data=data_)

            if result.status_code == 200:

                rez = json.loads(result.text)

                if rez["marker"] in (0, 3):
                    keyboard = [
                        [InlineKeyboardButton("Новая заявка", callback_data='0')],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text('К сожалению по Вашей заявке получен отказ. Вы можете оформить новую заявку '
                                          'на другую компанию, либо связаться с нашим менеджеров по номеру телефона '
                                          '8-800-505-88-32.', reply_markup=reply_markup)
                    return

                # Пишу полное наименование компании
                file1 = open(f"files/{update.effective_user.id}_answers.txt", "a")
                file1.write(rez["name"] + "\n")
                # file1.write("ООО аваы" + "\n")
                file1.close()

                kp_sum = round((rez["sum"])*1.3, -4)
                if kp_sum > 5000000:
                    kp_sum = 5000000

                update.message.reply_text(f'Поздравляем! Ваша заявка одобрена на сумму {kp_sum:n} рублей стоимости предмета лизинга. Предлагаем Вам на выбор 3 варианта графика платежей.')
                # update.message.reply_text(f'Вам предодобрен кредит. На сумму {"{:.2f}".format((rez["sum"]/400))} млн. руб. Готовлю коммерческие предложения.')

                for i in range(3):

                    period = 12
                    bot_file_name = "1 год.pdf"
                    if i == 1:
                        period = 24
                        bot_file_name = "2 года.pdf"
                    elif i == 2:
                        period = 36
                        bot_file_name = "3 года.pdf"

                    data = {
                            "leadId": 32200027,
                            "currency": 643,
                            "schedule_type": 10,
                            "vat_rate_cp": 20,
                            "vat_rate_la": 20,
                            "refund_type": 1,
                            "agent_type": 10,
                            "distribution_additional_costs": 10,
                            "tracker_type": 0,
                            "date": "07.04.2021",
                            "contract_price_no_discount": kp_sum,
                            "contract_price": kp_sum,
                            "discount": 0,
                            "acceleration": 1,
                            "prepayment": 20,
                            "prepayment_sum": 0,
                            "repayment": 1,
                            "repayment_sum": 0,
                            "period": period,
                            "leasing_rate": 20,
                            "insurance_rate": 28,
                            "additional_costs": 0,
                            "agent_commission": 0,
                            "insurance_sum": 0,
                            "name": "test",
                            "leasing_subject": "Оптоволоконный лазерный станок для резки металла MetalTec 1530 (1000W)",
                            "payments": {},
                            "manager": {

                                "id": 5468,
                                "name": "Мен мен мен",
                                "phone": "8996967877",
                                "mail": "gfgf@mail.ru"

                            },
                            "save": True
                        }

                    data_ = json.dumps(data)

                    headers = {'Content-Type': 'application/json'}
                    result = requests.post("https://api.nlkleasing.ru/api/schedule-calculate/", data=data_
                                           , auth=HTTPBasicAuth('admin', '131ZXnm90'), headers=headers)

                    if result.status_code == 200:
                        json_answer = json.loads(result.text)
                        file = json_answer['file']

                        r = requests.get(file, allow_redirects=True)
                        file_name = f'files/{update.effective_user.id}_{i}.pdf'
                        open(file_name, 'wb').write(r.content)
                        # update.message.reply_text(file)

                        in_file = open(file_name, "rb")  # opening for [r]eading as [b]inary
                        data = in_file.read()
                        in_file.close()
                        update.message.reply_document(document=data, filename=bot_file_name)

                keyboard = [
                    [InlineKeyboardButton("Год", callback_data='year_1'), InlineKeyboardButton("Два", callback_data='year_2'),InlineKeyboardButton("Три", callback_data='year_3')],

                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('Выберите подходящий для Вас график платежей.', reply_markup=reply_markup)

            else:

                keyboard = [
                    [InlineKeyboardButton("Новая заявка", callback_data='0')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('К сожалению по Вашей заявке получен отказ. Вы можете оформить новую заявку '
                                          'на другую компанию, либо связаться с нашим менеджеров по номеру телефона '
                                          '8-800-505-88-32.', reply_markup=reply_markup)

        else:
            file1 = open(f"files/{update.effective_user.id}_answers.txt", "w")
            file1.write(update.message.text + "\n")
            file1.close()




    elif update.message.text.find("start"):
        update.message.reply_text("Укажите ИНН компании")


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

    if query.data == "year_1" or query.data == "year_2" or query.data == "year_3":
        # update.message.reply_text("Укажите ИНН компании")

        # Счет клиенту
        in_file = open("files/score.pdf", "rb")  # opening for [r]eading as [b]inary
        data = in_file.read()
        in_file.close()
        context.bot.sendDocument(chat_id=update.callback_query.message.chat.id, document=data , filename="Счет на оплату.pdf")

        update.callback_query.edit_message_text(text="Спасибо за то что выбрали нашу компанию. В ближайшее время для "
                                                     "заключения договора с Вами свяжется Ваш менеджер. А также "
                                                     "высылаем Вам счет на оплату Авансового платежа.")

        # Рассылка ответственному менеджеру
        # 579493519

        # Данные из файла пользователя
        chat_id = update.callback_query.message.chat.id

        file1 = open(f"files/{chat_id}_answers.txt", "r+")
        all_data = file1.read().split("\n")
        inn = all_data[0]
        phone = "+7(977)425-41-79"
        name = all_data[1]

        if query.data == "year_1":
            kp = f'files/{chat_id}_{0}.pdf'
        elif query.data == "year_2":
            kp = f'files/{chat_id}_{1}.pdf'
        else:
            kp = f'files/{chat_id}_{2}.pdf'

        manager = 579493519
        context.bot.sendMessage(chat_id=manager, text=f"{name} получил предварительное одобрение. Клиент ждет "
                                                        f"связи от менеджера для заключения договора. Связаться с "
                                                        f"клиентом можно по телефону {phone} или написать ему в "
                                                        f"Телеграм {update.effective_user.name}")
        context.bot.sendDocument(chat_id=manager, document=data, filename="Счет на оплату.pdf")  # 579493519

        in_file = open(kp, "rb")  # opening for [r]eading as [b]inary
        kp_data = in_file.read()
        in_file.close()
        context.bot.sendDocument(chat_id=manager, document=kp_data, filename=f"КП_{inn}.pdf")  # 579493519


        # Очистить файл ответов
        file1 = open(f"files/{update.effective_user.id}_answers.txt", "w")
        file1.close()

        return

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
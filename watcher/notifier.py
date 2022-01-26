from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from positioner import config


class Notifier:
    def __init__(self) -> None:
        token = config.default("telegram", "token")
        self.updater = Updater(token=token)

        # get the dispatcher
        dispatcher = self.updater.dispatcher

        # on /start cmd
        start_handler = CommandHandler("start", self.__on_start_cmd)
        dispatcher.add_handler(start_handler)

        # on /buy cmd
        buy_handler = CommandHandler("buy", self.__on_buy_cmd)
        dispatcher.add_handler(buy_handler)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

    def __on_start_cmd(self, update: Update, _: CallbackContext) -> None:
        """Send a welcome message when the command /start is issued."""
        print("start command issued")
        update.message.reply_text('Hi! Welcome to PtajmanAlgoBot')

    def __on_buy_cmd(self, update: Update, _: CallbackContext) -> None:
        """Buys a mustange when the command /buy is issued."""
        print("buy command issued")
        update.message.reply_text('Buying Mustang!')

    def send_message(self, message: str, chat_id=config.default("telegram", "group_chat_id")):
        print("sending message", message)
        self.updater.bot.send_message(chat_id, message)

from django.conf import settings
import threading
import telebot
from .models import Feedback
bot: telebot.TeleBot = settings.BOT


@bot.callback_query_handler(lambda x: x.data.startswith('accept_'))
def accept_feedback(callback: telebot.types.CallbackQuery):
    pk = int(callback.data.split('_')[-1])
    Feedback.objects.filter(id=pk).update(is_accepted=True, is_reviewed=True)
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(lambda x: x.data.startswith('decline_'))
def accept_feedback(callback: telebot.types.CallbackQuery):
    pk = int(callback.data.split('_')[-1])
    Feedback.objects.filter(id=pk).update(is_reviewed=True)
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)


def start_bot():
    threading.Thread(target=bot.infinity_polling).start()

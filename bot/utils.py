from django.conf import settings
from uuid import uuid4
from .models import Feedback
import telebot
bot: telebot.TeleBot = settings.BOT
import magic
import time


def get_mime_type(file: str): # Test function
    type = file.rsplit('.')[-1]
    if type in ('png', 'jpg', 'jpeg'):
        return 'image'
    if type in ('mp4', ):
        return 'video'

def send_feedback_to_moderation(feedback: Feedback):
    time.sleep(20)
    text = f'''Новый отзыв
Имя: {feedback.name}
Место работы: {feedback.working_place}
Текст: {feedback.text}
'''     
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(text='Подтвердить', callback_data=f'accept_{feedback.pk}'),
        telebot.types.InlineKeyboardButton(text='Отменить', callback_data=f'decline_{feedback.pk}'),
    )

    if feedback.media.name is None:
        bot.send_message(settings.MODERATION_CHAT_ID, text=text, reply_markup=markup)
    else:
        mimetype = get_mime_type(feedback.media).split('/')[0]
        if mimetype == 'video':
            bot.send_video(settings.MODERATION_CHAT_ID, caption=text, reply_markup=markup, video=feedback.media)
        elif mimetype == 'image':
            bot.send_photo(settings.MODERATION_CHAT_ID, caption=text, reply_markup=markup, photo=feedback.media)
        else:
            raise Exception(f"unexpected '{mimetype}' type")
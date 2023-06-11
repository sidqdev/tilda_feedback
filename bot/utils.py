from django.conf import settings
from uuid import uuid4
from .models import Feedback
import telebot
bot: telebot.TeleBot = settings.BOT
import magic


def get_mime_type(file):
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    return mime_type


def handle_uploaded_file(f, name):
    name = uuid4().hex + name
    name = f"{settings.MEDIA_ROOT}/{name}"
    with open(name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    return name


def send_feedback_to_moderation(feedback: Feedback):
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
        mimetype = get_mime_type(feedback.media.file).split('/')[0]
        if mimetype == 'video':
            bot.send_video(settings.MODERATION_CHAT_ID, caption=text, reply_markup=markup, video=feedback.media)
        elif mimetype == 'image':
            bot.send_photo(settings.MODERATION_CHAT_ID, caption=text, reply_markup=markup, photo=feedback.media)
        else:
            raise Exception(f"unexpected '{mimetype}' type")
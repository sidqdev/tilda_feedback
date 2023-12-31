import time
import requests
import bs4
from django.conf import settings
from .models import Feedback
import telebot
import dropbox
from dropbox.exceptions import AuthError
import io
import json 


bot: telebot.TeleBot = settings.BOT

def get_dropbox_link(link: str):
    html = None
    for i in range(5):
        html = requests.get(link).text
        if 'has not been uploaded' not in html:
            break
        time.sleep((i + 2) * 10)

    if html is None:
        return None

    soup = bs4.BeautifulSoup(html, "lxml")
    return soup.find("div", {"class": "download"}).find("a")['href'].split("?")[0]


def dropbox_connect():
    """Create a connection to Dropbox."""

    try:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": settings.DROPBOX_REFRESH_TOKEN,
            "client_id": settings.DROPBOX_APP_KEY,
            "client_secret": settings.DROPBOX_APP_SECRET
        }
        resp = requests.post("https://api.dropbox.com/oauth2/token", data=data)
        access_token = json.loads(resp.text)['access_token']
        dbx = dropbox.Dropbox(oauth2_access_token=access_token)
    except AuthError as e:
        print('Error connecting to Dropbox with access token: ' + str(e))
    return dbx


def dropbox_get_shared_link(dropbox_file_path):
    """Get a shared link for a Dropbox file path.

    Args:
        dropbox_file_path (str): The path to the file in the Dropbox app directory.

    Returns:
        link: The shared link.
    """
    filename = dropbox_file_path.rsplit('/')[-1]
    dropbox_file_path = f'/Приложения/Tilda Publishing/{filename}'
    try:
        dbx = dropbox_connect()
        dbx.sharing_unshare_file(dropbox_file_path)
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_file_path)
        shared_link = shared_link_metadata.url
        return shared_link.replace('?dl=0', '?dl=1')
    except dropbox.exceptions.ApiError as exception:
        if exception.error.is_shared_link_already_exists():
            shared_link_metadata = dbx.sharing_get_shared_links(dropbox_file_path)
            shared_link = shared_link_metadata.links[0].url
            return shared_link.replace('?dl=0', '?dl=1')


def get_mime_type(file: str): # Test function
    type = file.split('?')[0].rsplit('.')[-1]
    if type in ('png', 'jpg', 'jpeg'):
        return 'image'
    if type in ('mp4', ):
        return 'video'

def send_feedback_to_moderation(feedback: Feedback):
    if feedback.media is not None:
        raw_link = get_dropbox_link(feedback.media)
        link = dropbox_get_shared_link(raw_link)
        feedback.media = link
        feedback.save()

    text = f'''Новый отзыв
Имя: {feedback.name}
Место работы: {feedback.working_place}
Текст: {feedback.text}
Медиа: {feedback.media}
'''     
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(text='Подтвердить', callback_data=f'accept_{feedback.pk}'),
        telebot.types.InlineKeyboardButton(text='Отменить', callback_data=f'decline_{feedback.pk}'),
    )

    if feedback.media is None:
        bot.send_message(settings.MODERATION_CHAT_ID, text=text, reply_markup=markup)
    else:

        mimetype = get_mime_type(feedback.media).split('/')[0]
        file = io.BytesIO(requests.get(feedback.media, allow_redirects=True).content)
        if mimetype == 'video':
            bot.send_video(settings.MODERATION_CHAT_ID, caption=text, reply_markup=markup, video=file)
        elif mimetype == 'image':
            bot.send_photo(settings.MODERATION_CHAT_ID, caption=text, reply_markup=markup, photo=file)
        else:
            raise Exception(f"unexpected '{mimetype}' type")
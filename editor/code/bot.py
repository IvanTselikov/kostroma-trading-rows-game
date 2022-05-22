import telebot  # pip install pyTelegramBotAPI
from telebot import types
from bot_message import *
from config import TOKEN
import media_converter
import pickle
import sys
from code_analyzer import CodeAnalyzer
import parser

class Bot:
    """Класс Telegram-бота с игрой."""
    def __init__(self, token, start_post):
        """Создаёт Telegram-бота с указанным токеном и сценарием.

        Параметры:
        token - токен бота
        start_post - первый пост игры
        """
        token = TOKEN
        self.tgbot = telebot.TeleBot(token)
        self.user_table = []  # таблица с записями вида "userid - post - last_message_id"
        self.start_post = start_post

        @self.tgbot.message_handler(commands=['start'])
        def register_new_user(message):
            """Записывает нового игрока в таблицу при нажатии им кнопки "Старт"."""
            if any([user_id == message.from_user.id for user_id, _, _ in self.user_table]):
                return  # данный игрок уже начал игру
            # делаем запись о новом игроке
            self.user_table.append((message.from_user.id, self.start_post, message.id))
            print(f'Пользователь {message.from_user.id} начал игру.')
            post = self.start_post
            self.send(message, post)  # отправляем первое сообщение
            while True:
                post = post.get_next(message.text)
                if post is None:
                    break
                self.send(received=message, new_post=post)
                message.text = None


        @self.tgbot.message_handler(content_types=['text'])
        def handle_text(message):
            """Обрабатывает текстовые сообщения от игрока."""
            post = None
            for user_id, last_post, _ in self.user_table:
                if user_id == message.from_user.id:
                    post = last_post
                    break
            if post is None:
                # игрок ещё не начал игру (не нажал на "Старт")
                return
            while True:
                post = post.get_next(message.text)  # получаем новые сообщения для отправки
                if post is None:
                    # сообщения кончились либо ожидается ответ от пользователя
                    break
                self.send(received=message, new_post=post)
                message.text = None

        AUDIO_OGG = 'audio.ogg'
        @self.tgbot.message_handler(content_types=['voice'])
        def handle_voice(message):
            """Обрабатывает голосовые сообщения от игрока."""
            post = None
            for user_id, last_post, _ in self.user_table:
                if user_id == message.from_user.id:
                    post = last_post
                    break
            if post is None:
                # игрок ещё не начал игру (не нажал на "Старт")
                return
            file_info = self.tgbot.get_file(message.voice.file_id)
            downloaded_file = self.tgbot.download_file(file_info.file_path)
            with open(AUDIO_OGG, 'wb') as f:
                f.write(downloaded_file)
            mc = media_converter.MediaConverter()
            text = mc.voiceToText(AUDIO_OGG)
            if text == mc.UNKNOWN:
                self.tgbot.send_message(message.chat.id, '🙁 Извините, я не понял, что вы сказали', timeout=self.TIMEOUT)
            else:
                self.tgbot.send_message(message.chat.id, f'😊 Кажется, вы сказали: {text}', timeout=self.TIMEOUT)
            while True:
                post = post.get_next(text)  # получаем новые сообщения для отправки
                if post is None:
                    # сообщения кончились либо ожидается ответ от пользователя
                    break
                self.send(received=message, new_post=post)
                text = None

        @self.tgbot.callback_query_handler(func=lambda call: True)
        def handle_buttons(call):
            """Обрабатывает нажатия на кнопки."""
            self.tgbot.answer_callback_query(call.id)
            post = None
            for user_id, last_post, last_message_id in self.user_table:
                if user_id == call.from_user.id and last_message_id == call.message.id:
                    post = last_post
                    break
            if post is None:
                # игрок ещё не начал игру (не нажал на "Старт") или нажал на старые кнопки
                return
            while True:
                post = post.get_next(call.data)  # получаем новые сообщения для отправки
                if post is None:
                    # сообщения кончились либо ожидается ответ от пользователя
                    break
                self.send(received=call.message, new_post=post)
                call.data = None

        self.tgbot.infinity_polling()  # начинаем слушать бота

    TIMEOUT = 45
    def send(self, received, new_post):
        """Отправляет пост в чат.

        Параметры:
        received - полученнное сообщение (тип telebot.Message)
        new_post - пост для отправки (тип bot_message.Post)
        """
        if isinstance(new_post, TextPost):
            sent = self.tgbot.send_message(received.chat.id, new_post.content, timeout=self.TIMEOUT)
        elif isinstance(new_post, ImagePost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_photo(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, VideoPost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_video(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, VoicePost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_voice(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, GifPost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_animation(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, RoundPost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_video_note(received.chat.id, content,
                                                  length=new_post.width, timeout=self.TIMEOUT)
        elif isinstance(new_post, DocPost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_document(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, AudioPost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_audio(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, StickerPost):
            with open(new_post.content, 'rb') as content:
                sent = self.tgbot.send_sticker(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, ButtonsPost):
            markup_inline = types.InlineKeyboardMarkup()
            for button in new_post.content:
                new_item = types.InlineKeyboardButton(text=button.text,
                                                      callback_data=button.callback_data)
                markup_inline.add(new_item)
            sent = self.tgbot.send_message(received.chat.id, new_post.caption,
                                           reply_markup=markup_inline, timeout=self.TIMEOUT)
        elif isinstance(new_post, GroupPost):
            if not new_post.content:  # сгруппированное сообщение содержит только текст
                sent = self.tgbot.send_message(received.chat.id, new_post.caption, timeout=self.TIMEOUT)
            else:
                medias = []
                opened_files = []
                for post in new_post.content:
                    content = open(post.content, 'rb')
                    if isinstance(post, DocPost):
                        medias = [types.InputMediaDocument(content)]
                        break
                    elif isinstance(post, AudioPost):
                        medias= [types.InputMediaAudio(content)]
                        break
                    elif isinstance(post, ImagePost):
                        medias.append(types.InputMediaPhoto(content))
                    elif isinstance(post, VideoPost):
                        medias.append(types.InputMediaVideo(content))
                    opened_files.append(content)
                medias[0].caption = new_post.caption
                sent = self.tgbot.send_media_group(received.chat.id, medias, timeout=self.TIMEOUT)[-1]
                for file in opened_files:
                    file.close()
        else:
            sent = None
            print('Неизвестный тип сообщений.')
        # сохраняем id последнего отправленного сообщения для конкретного пользователя и новый пост
        for i, (user_id, last_post, last_message_id) in enumerate(self.user_table):
            if user_id == received.chat.id:
                self.user_table[i] = (user_id, new_post, sent.id)
                break
        if new_post.is_endpoint():
                    print('endpoint')
                    # отправлено последнее сообщение игры, игрок может начать заново
                    for i in range(len(self.user_table)):
                        if self.user_table[i][0] == received.from_user.id:
                            del self.user_table[i]

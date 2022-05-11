from abc import ABC, abstractmethod
import random
import string
import media_converter
import os
import morpheme

class Post(ABC):
    """Класс поста."""
    SEND_IMMEDIATELY = '0'  # константа: отправить следующий пост сразу за текущим
    SEND_ELSE = '1'  # константа: отправить следующий пост, если условие не выполнилось
    def __init__(self, content):
        """Создать пост с указанным контентом.

        Параметры:
        content: содержимое поста (текст, аудио, кнопки, документы и т.д.)
        """
        self.content = content
        self.transitions = []  # список функций, возвращающих следующий пост при выполнении
                               # некоторого условия
        self.morph = morpheme.StringsAnalyser()  # анализатор для поиска ключевых слов в строке

    def add_next(self, next_post, requiered_callback=SEND_IMMEDIATELY, is_keyword=False):
        """Добавить переход на пост.

        Параметры:
        next_post: пост, на который нужно перейти
        requiered_callback: содержание полученного от игрока сообщения (строка или запись 
                            голоса) либо константа SEND_IMMEDIATELY - пост следует 
                            отправить сразу за текущим, не проверяя условий
        is_keyword: если True, то в параметр requiered_callback передано ключевое слово,
                    которое нужно найти; иначе - ответ игрока должен точно совпадать с указанным
                    в required_callback
        """
        def transition(received):
            if requiered_callback == self.SEND_IMMEDIATELY:
                # следующий пост следует отправить сразу за текущим
                return next_post
            if received is None:
                # ответа от игрока не получено - ничего не возвращаем
                return None
            if self.morph.check(received, requiered_callback, is_keyword):
                return next_post
            if requiered_callback == self.SEND_ELSE:
                # следующий пост нужно отправить, если ни одно условие не выполнилось
                return next_post
        self.transitions.append(transition)

    def get_next(self, received=None):
        """Получить следующий пост.

        Параметры:
        received: полученное от пользователя сообщение (текст либо голос). Если None,
                  будет производиться поиск поста, который отправляется
                  без условий
        """
        for transition in self.transitions:
            next_post = transition(received)
            if not next_post is None:
                return next_post


class TextPost(Post):
    """Текстовый пост."""
    def __init__(self, text):
        super().__init__(text)


class ImagePost(Post):
    """Пост с картинкой."""
    FORMATS = ['.jpg', '.jpeg', '.png', '.webp']  # доступные форматы изображений
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            raise Exception(f'Файл {file_path} имеет недопустимый формат.')
        super().__init__(file_path)


class VideoPost(Post):
    """Пост с видео."""
    FORMATS = ['.mp4']
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            raise Exception(f'Файл {file_path} имеет недопустимый формат.')
        super().__init__(file_path)


class VoicePost(Post):  # должен быть формат ogg
    """Пост с голосовым сообщением"""
    FORMATS = ['.ogg']
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            file_path = mc.convertToOgg(file_path)  # выбрасывает исключение в случае 
                                                    # неподдерживаемого формата
        super().__init__(file_path)


class GifPost(Post):
    """Пост с gif-анимацией."""
    FORMATS = ['.gif']
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            raise Exception(f'Файл {file_path} имеет недопустимый формат.')
        super().__init__(file_path)


class RoundPost(Post):
    """Пост с круглым видео."""
    FORMATS = ['.mp4']
    WIDTH = 480  # ширина (высота) видео по умолчанию

    def __init__(self, file_path, width=480):
        """Создаёт пост с круглым видео.

        Параметры:
        file_path - путь до видео
        width - ширина (и высота) видео
        """
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            raise Exception(f'Файл {file_path} имеет недопустимый формат.')
        if width < 10:
            raise Exception(f'Указана недопустимая ширина (высота) видео.')
        width = min(width, self.WIDTH)
        mc.changeVideoResolution(file_path, (width, width))
        self.width = width
        super().__init__(file_path)


class DocPost(Post):
    """Пост с прикреплённым документом (произвольным файлом)."""
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        super().__init__(file_path)


class AudioPost(Post):
    """Пост с аудиозаписью."""
    # mp3 формат
    FORMATS = ['.mp3']
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            file_path = mc.convertToMp3(file_path)  # выбрасывает исключение в случае 
                                                    # неподдерживаемого формата
        super().__init__(file_path)


class StickerPost(Post):
    """Пост с картинкой-стикером."""
    FORMATS = ImagePost.FORMATS
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f'Файл {file_path} не существует.')
        if not os.path.getsize(file_path):
            raise Exception(f'Файл {file_path} не должен быть пустым.')
        mc = media_converter.MediaConverter()
        if not mc.getFileExtension(file_path) in self.FORMATS:
            raise Exception(f'Файл {file_path} имеет недопустимый формат.')
        super().__init__(file_path)


class ButtonsPost(Post):
    """Пост с набором кнопок."""
    def __init__(self, caption, buttons):
        """Создаёт пост с набором кнопок и подписью.

        Параметры:
        buttons - массив кнопок Button
        caption - текстовая подпись к посту
        """
        super().__init__(buttons)
        self.caption = caption

    def add_next(self, next_post, requiered_button):
        def transition(callback_data):
            if callback_data == requiered_button.callback_data and requiered_button in self.content:
                # удаляем с панели кнопку, на которую нажали
                # del self.content[self.content.index(requiered_button)]
                return next_post
        self.transitions.append(transition)


class Button:
    """Кнопка."""
    def __init__(self, text):
        """Создаёт кнопку.

        Параметры:
        text - текст на кнопке.
        """
        self.text = text
        self.callback_data = self.generate_callback_data()  # идентификатор кнопки

    def generate_callback_data(self):
        """Генерирует случайный идентификатор для кнопки."""
        return ''.join(random.choices(string.ascii_lowercase, k=10))


class GroupPost(Post):
    """Пост, содержащий фото, видео, документы, аудио и (или) текст."""
    def __init__(self, posts):
        """Создаёт сгруппированный пост.
        * документы нельзя смешивать с другими типами (кроме текста)
        * аудио нельзя смешивать с другими типами (кроме текста)
        * не больше 10 сообщений (не включая текст)
        * только один текст

        Параметры:
        messages - посты, входящие в состав группы.
        """
        if not posts:
            raise Exception('Пустой сгруппированный пост.')
        if not all([isinstance(post, TextPost) or isinstance(post, DocPost) or
                    isinstance(post, AudioPost) or isinstance(post, ImagePost) or 
                    isinstance(post, VideoPost) for post in posts]):
            raise Exception('Сгруппированный пост может содержать только документы, видео, аудио, фото или текст.')
        text_posts = []
        posts_without_text = []
        for post in posts:
            if isinstance(post, TextPost):
                text_posts.append(post)
            else:
                posts_without_text.append(post)
        posts = posts_without_text
        if len(posts)>10:
            raise Exception('Сгруппированный пост не может содержать больше 10 сообщений (не включая текст).')
        if len(text_posts)>1:
            raise Exception('Сгруппированный пост может включать в себя только одно текстовое сообщение.')
        doc_posts = list(filter(lambda p: isinstance(p, DocPost), posts))
        if len(doc_posts)>1:
            raise Exception('Можно отправлять только один документ.')
        if doc_posts and len(posts)>len(doc_posts):
            raise Exception('Документы нельзя смешивать с другими типами сообщений.')
        audio_posts = list(filter(lambda p: isinstance(p, AudioPost), posts))
        if len(audio_posts)>1:
            raise Exception('Можно отправлять только один аудиофайл.')
        if audio_posts and len(posts)>len(audio_posts):
            raise Exception('Аудио нельзя смешивать с другими типами сообщений.')
        self.caption = text_posts[0].content if text_posts else None
        super().__init__(posts)

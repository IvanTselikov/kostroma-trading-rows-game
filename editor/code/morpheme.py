import pymorphy2  # pip install pymorphy2
import num2words  # pip install num2words
import re
from pyphrasy.inflect import PhraseInflector  # pip install pyphrasy

class StringsAnalyser:
    CASES = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct', 'voct', 'gen2', 'acc2', 'loc2']  # падежи

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def replace_numbers_with_words(self, string):
        """Заменяет все числа в строке словами."""
        # ищем числа в строке
        try:
            numbers = re.findall(r'\d+', string)
        except:
            return string
        # преобразуем числа в слова
        numwords = []
        for number in numbers:
            number = num2words.num2words(number, lang='ru')
            if number.startswith('одна тысяча'):
                number = number.replace('одна ', '', 1)
            elif number.startswith('один миллион') or number.startswith('один миллиард') or\
                 number.startswith('один триллион'):
                number = number.replace('один ', '', 1)
            numwords.append(number)
        # вставляем слова обратно в строку
        for i, nw in enumerate(numwords):
            string = string.replace(numbers[i], nw, 1)
        return string

    def get_all_forms(self, phrase):
        """Возвращает список форм слова (словосочетания)."""
        inflector = PhraseInflector(self.morph)
        forms = []
        for case in self.CASES:
            forms.append(inflector.inflect(phrase, case))
        forms = list(set(forms))  # убираем дубликаты
        return forms


    DIGITS_ONLY = -1  # строка содержит только цифры
    WORDS_ONLY = 1  # строка содержит только слова
    MIXED = 0  # строка содержит и слова, и цифры

    def get_status(s):
        try:
            re.findall(r'\d+', s)
        except:
            return self.WORDS_ONLY
        if s.isdigit():
            return self.DIGITS_ONLY
        if not re.findall(r'\d+', s):
            return self.WORDS_ONLY
        return self.MIXED

    def check(self, received, requiered, is_keyword):
        """Проверяет, содержится (или совпадает) строка requiered в строке received."""
        received = received.lower()
        requiered = requiered.lower()
        contains_digits = lambda s: re.findall(r'\d+', s)
        try:
            cd_requiered = contains_digits(requiered)
        except:
            cd_requiered = False
        try:
            cd_received = contains_digits(received)
        except:
            cd_received = False
        if cd_requiered and cd_received:
            # не переводим не склоняем, ищем
            if is_keyword:
                return received.find(requiered) != -1
            return received.lower() == requiered.lower()
        elif cd_requiered and not cd_received:
            # переводим ключ слово, склоняем ключ слово, ищем
            requiered = self.replace_numbers_with_words(requiered)
            forms = self.get_all_forms(requiered)
            if is_keyword:
                return any([received.find(form) != -1 for form in forms])
            return any([received.lower() == form.lower() for form in forms])
        elif not cd_requiered and cd_received:
            # переводим полученное, склоняем если ключевое, ищем
            received = self.replace_numbers_with_words(received)
            if is_keyword:
                forms = self.get_all_forms(requiered)
                return any([received.find(form) != -1 for form in forms])
            return received.lower() == requiered.lower()
        elif not cd_requiered and not cd_received:
            # склоняем ключ если ключевое, ищем
            if is_keyword:
                forms = self.get_all_forms(requiered)
                return any([received.find(form) != -1 for form in forms])
            return received.lower() == requiered.lower()

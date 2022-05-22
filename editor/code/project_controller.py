import os
import shutil
import pickle
from code_analyzer import CodeAnalyzer
import parser
import subprocess
from bot import Bot
import sys

class Project:
    """Проект с ботом."""

    RES_NAME = 'res'  # название папки с ресурсами
    BIN_NAME = 'bin'  # название папки со скомпилированным проектом
    SCN_FILENAME = 'code.scn'  # название файла с кодом
    OBJ_FILENAME = 'obj.bin'  # название файла со скомпилированными объектами


    def __init__(self, path, bot_path):
        """Создаёт новый проект по указанному пути."""
        self.path = path  # путь до проекта
        self.res = path + os.sep + self.RES_NAME  # путь до папки с ресурсами
        self.scn = path + os.sep + self.SCN_FILENAME  # путь до файла с кодом
        self.bin = path + os.sep + self.BIN_NAME  # путь до папки со скомпилированным проектом
        self.obj = self.bin + os.sep + self.OBJ_FILENAME  # путь до файла со скомпилированными объектами
        self.name = os.path.basename(self.path)  # название проекта
        self.bot_path = bot_path  # путь до скрипта, запускающего бота
        self.code_analyzer = CodeAnalyzer()
        self.process = None
        self.create_temp()


    def create_temp(self):
        """Создаёт файловую структуру проекта."""
        if not os.path.isdir(self.res):
            # создаём папку с ресурсами
            os.makedirs(self.res)
        if not os.path.isdir(self.bin):
            # создаём папку с объектами
            os.mkdir(self.bin)
            # создаём файл для скомпилированных объектов
            with open(self.obj, 'w') as f:
                pass
        if not os.path.isfile(self.scn):
            # создаём файл с кодом
            with open(self.scn, 'w', encoding='utf-8', newline='') as f:
                pass


    def save(self, code):
        """Сохраняет код в файле для кода в проекте.

        Параметры:
        code - код для сохранения
        """
        try:
            with open(self.scn, 'w', encoding='utf-8', newline='') as f:
                f.write(code)
        except:
            # файл с кодом был затёрт
            self.create_temp()  # восстанавливаем структуру проекта
            self.name = os.path.basename(self.path)
            with open(self.scn, 'w', encoding='utf-8', newline='') as f:
                f.write(code)


    def is_saved(self, current_code):
        """Возвращает True, если указанный код сохранён в проекте."""
        try:
            with open(self.scn, 'r', encoding='utf-8', newline='') as f:
                saved_code = f.read()
                return current_code == saved_code
        except:
            # не удалось открыть файл с сохранённым кодом
            return False


    def get_code(self):
        """ Возвращает сохранённый код проекта."""
        try:
            with open(self.scn, 'r', encoding='utf-8', newline='') as f:
                return f.read()
        except:
            # не удалось открыть файл с сохранённым кодом
            return ''


    def is_project(path):
        """ Проверяет файловую структуру в папке на соответствие файловой структуре проекта.

        Параметры:
        path - папка для проверки
        """
        if os.path.isdir(path + os.sep + Project.RES_NAME) and\
           os.path.isfile(path + os.sep + Project.SCN_FILENAME) and\
           os.path.isfile(path + os.sep + Project.BIN_NAME + os.sep + Project.OBJ_FILENAME):
            return True
        return False


    def get_resources_names(self):
        """Возвращает названия файлов в каталоге ресурсов."""
        if os.path.isdir(self.res):
            return os.listdir(self.res)
        return []


    def add_res(self, path):
        """Добавляет файл ресурсов в проект."""
        shutil.copy(path, self.res)


    def remove_res(self, name):
        """Удаляет файл ресурсов из проекта."""
        os.remove(self.res + os.sep + name)


    def run(self, recompile, new_console=True):
        """Собирает .exe-файл с ботом"""
        if new_console:
            if recompile:
                self.process = subprocess.Popen(['python', __file__, '-c', self.path, self.bot_path],
                                                creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                self.process = subprocess.Popen(['python', __file__, self.path, self.bot_path],
                                                creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            if recompile:
                code = self.get_code()
                analyzed, _ = self.code_analyzer.get_words(code)
                words_for_parsing = self.code_analyzer.get_words_for_parsing(analyzed)
                scenery = parser.getScenery(words_for_parsing, self.res + os.sep)
                serialized = pickle.dumps(scenery)
                with open(self.obj, 'wb') as f:
                    f.write(serialized)
            print('=== ЗАПУСКАЕМ БОТА... ===')
            with open(self.obj, 'rb') as f:
                token, first_message = pickle.load(f)
            print('=== БОТ ЗАПУЩЕН. МОЖНО ИГРАТЬ ===')
            bot = Bot(token, first_message)


    def stop(self):
        """Останавливает бота."""
        self.process.kill()
        self.process = None


    def is_alive(self):
        if self.process and self.process.poll() is None:
            return True
        return False


if __name__ == '__main__':
    try:
        project = Project(sys.argv[-2], sys.argv[-1])
        if len(sys.argv) == 4:
            # project_controller.exe -c path bot_path
            # нужно скомпилировать проект
            project.run(recompile=True, new_console=False)
        elif len(sys.argv) == 3:
            # project_controller.exe path bot_path
            # нужно запустить уже скомпилированный проект
            project.run(recompile=False, new_console=False)
    except Exception as e:
        print(e)
        input('Для выхода нажмите любую клавишу...')
        sys.exit(0)

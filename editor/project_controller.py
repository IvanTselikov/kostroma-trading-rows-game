import os
import shutil

class Project:
    RES_NAME = 'res'  # название папки с ресурсами
    SCN_FILENAME = 'code.scn'  # название файла с кодом

    def __init__(self, path):
        self.path = path  # путь до проекта
        self.res = path + os.sep + self.RES_NAME  # путь до папки с ресурсами
        self.scn = path + os.sep + self.SCN_FILENAME  # путь до файла с кодом
        self.name = os.path.basename(self.path)  # название проекта
        self.create_temp()


    def create_temp(self):
        if not os.path.isdir(self.res):
            # создаём папку с ресурсами
            os.makedirs(self.res)
        if not os.path.isfile(self.scn):
            # создаём файл с кодом
            with open(self.scn, 'w', newline='') as f:
                pass


    def save(self, code):
        try:
            with open(self.scn, 'w', newline='') as f:
                f.write(code)
        except:
            self.create_temp()
            self.name = os.path.basename(self.path)
            with open(self.scn, 'w', newline='') as f:
                f.write(code)


    def is_saved(self, current_code):
        try:
            with open(self.scn, 'r', newline='') as f:
                saved_code = f.read()
                return current_code == saved_code
        except:
            return False


    def get_code(self):
        with open(self.scn, 'r', newline='') as f:
            return f.read()


    def is_project(path):
        res_path = path + os.sep + Project.RES_NAME
        code_path = path + os.sep + Project.SCN_FILENAME
        if os.path.isdir(res_path) and os.path.isfile(code_path):
            return True
        return False


    def get_resources_names(self):
        """Возвращает названия файлов в каталоге ресурсов."""
        if os.path.isdir(self.res):
            return os.listdir(self.res)
        else:
            return []


    def add_res(self, path):
        shutil.copy(path, self.res)


    def remove_res(self, name):
        os.remove(self.res + os.sep + name)

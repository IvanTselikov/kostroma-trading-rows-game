import wx  # pip install -U --pre -f https://wxpython.org/Phoenix/snapshot-builds/ wxPython
import wx.stc
import codecs
import code_analyzer
from project_controller import Project
from editor import Editor
from help import HelpDialog, DocDialog
import parserV2


class MainWindow(wx.Frame):
    """Класс окна редактора."""
    DEFAULT_APPNAME = 'Безымянный'

    def __init__(self, parent, title):
        super().__init__(parent, title=title, style = wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE)
        # иконки меню
        self.createMenuBar()
        self.createSideBar()

        self.app_name = title
        self.SetTitle(f'{self.app_name} - {self.DEFAULT_APPNAME}')

        self.SetIcon(wx.Icon('icon.ico'))

        self.main_spltr = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_LIVE_UPDATE)

        font = wx.Font(11, wx.DEFAULT, wx.BOLD, wx.NORMAL)
        self.main_spltr.SetFont(font)

        self.sidebar_p = wx.Panel(self.main_spltr)
        self.edit_p = wx.Panel(self.main_spltr)

        self.sidebar_p.SetBackgroundColour('#ddddff')

        self.main_spltr.SplitVertically(self.sidebar_p, self.edit_p)
        self.main_spltr.SetMinimumPaneSize(200)

        self.res_p = wx.Panel(self.sidebar_p)
        self.res_st = wx.StaticText(self.res_p, label=' Ресурсы')
        self.res_b = wx.Button(self.res_p, label='+', size=(20,20))
        self.res_rm_b = wx.Button(self.res_p, label='-', size=(20,20))
        self.res_lb = wx.ListBox(self.res_p, choices=[], style=wx.LB_MULTIPLE)
        self.res_gbs = wx.GridBagSizer(2, 3)
        self.res_gbs.Add(self.res_st, pos=(0, 0), flag = wx.UP, border=5)
        self.res_gbs.Add(self.res_rm_b, pos=(0,1), flag = wx.UP | wx.ALIGN_RIGHT, border=5)
        self.res_gbs.Add(self.res_b, pos=(0, 2), flag = wx.UP, border=5)
        self.res_gbs.Add(self.res_lb, pos=(1, 0), span=(1, 3), flag=wx.EXPAND | wx.UP, border=3)
        self.res_gbs.AddGrowableCol(1)
        self.res_gbs.AddGrowableRow(1)
        self.res_p.SetSizer(self.res_gbs)

        self.res_lb.SetBackgroundColour('#eeeeff')

        self.sidebar_bs = wx.BoxSizer(wx.VERTICAL)
        # self.sidebar_bs.Add(self.scenes_p, wx.ID_ANY, flag=wx.EXPAND | wx.ALL, border=5)
        self.sidebar_bs.Add(self.res_p, wx.ID_ANY, flag=wx.EXPAND | wx.ALL, border=5)
        self.sidebar_p.SetSizer(self.sidebar_bs)

        self.editor = Editor(self.edit_p, frame=self)
        self.edit_bs = wx.BoxSizer()
        self.edit_bs.Add(self.editor, wx.ID_ANY, flag=wx.EXPAND)
        self.edit_p.SetSizer(self.edit_bs)

        self.project = None  # текущий редактируемый проект
        self.save_project_dd = wx.DirDialog(self, 'Сохранение проекта...', '', 
                                         wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        self.open_project_dd = wx.DirDialog(self, 'Открытие проекта...', '',
                                         wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        self.create_project_dd = wx.DirDialog(self, 'Создание проекта...', '',
                                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        self.save_changes_md = wx.MessageDialog(self, 'Сохранить изменения?', 
                                                self.DEFAULT_APPNAME,
                                                wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_INFORMATION)
        self.add_res_fd = wx.FileDialog(self, 'Добавление ресурсов...', 
                                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)

        self.help_dlg = None  # окно с руководством пользователя
        self.doc_dlg = None  # окно с документацией по языку

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.Bind(wx.EVT_BUTTON, self.add_res, self.res_b)
        self.Bind(wx.EVT_BUTTON, self.remove_res, self.res_rm_b)

        self.editor.SetFocus()

        # self.res_lb.Bind(wx.EVT_LEFT_UP, self.show_ctx_res)


    def createMenuBar(self):
        self.menubar = wx.MenuBar()

        # TODO: свои ID
        self.project_menu = wx.Menu()  # вкладка "Проект"
        self.create_item = self.project_menu.Append(wx.ID_ANY, 'Создать\tCtrl+N', 'Создать новый пустой проект')
        self.open_item = self.project_menu.Append(wx.ID_ANY, 'Открыть...\tCtrl+O', 'Открыть существующий проект')
        self.save_item = self.project_menu.Append(wx.ID_ANY, 'Сохранить...\tCtrl+S', 'Сохранить изменения в текущем проекте')

        self.bot_menu = wx.Menu()  # подменю "Бот"
        self.start_item = self.bot_menu.Append(wx.ID_ANY, 'Запуск...\tCtrl+K', 'Запустить бота')
        self.stop_item = self.bot_menu.Append(wx.ID_ANY, 'Стоп\tCtrl+P', 'Остановить бота')

        self.about_menu = wx.Menu()  # вкладка "О программе"
        self.doc_item = self.about_menu.Append(wx.ID_ANY, 'Спецификация языка\tCtrl+D', 'Просмотреть команды языка разметки сценариев')
        self.help_item = self.about_menu.Append(wx.ID_ANY, 'Руководство пользователя\tCtrl+H', 'Посмотреть руководство пользователя')

        self.menubar.Append(self.project_menu, '&Проект')
        self.menubar.Append(self.bot_menu, '&Бот')
        self.menubar.Append(self.about_menu, '&Помощь')

        self.SetMenuBar(self.menubar)

        self.Bind(wx.EVT_MENU, self.onCreateClick, self.create_item)
        self.Bind(wx.EVT_MENU, self.onOpenClick, self.open_item)
        self.Bind(wx.EVT_MENU, self.onSaveClick, self.save_item)
        self.Bind(wx.EVT_MENU, self.onStartClick, self.start_item)
        self.Bind(wx.EVT_MENU, self.onStopClick, self.stop_item)
        self.Bind(wx.EVT_MENU, self.onDocClick, self.doc_item)
        self.Bind(wx.EVT_MENU, self.onHelpClick, self.help_item)


    def createSideBar(self):
        pass


    def suggest_saving(self):
        """Предлагает сохранить изменения в текущем проекте.
        Возвращает True, если операция выполнена успешно, False - если пользователь
        запросил полной отмена операции."""
        if self.project is None:
            # текущий проект ещё никуда не сохранён
            # предлагаем сохранить
            result = self.save_changes_md.ShowModal()
            if result == wx.ID_YES:
                # пользователь хочет сохранить текущий проект
                # просим путь, по которому он хочет сохранить его
                result = self.save_project_dd.ShowModal()
                if result == wx.ID_OK:
                    # сохраняем проект по указанному пути
                    self.project = Project(self.save_project_dd.GetPath())
                    self.project.save(self.editor.GetText())
                elif result == wx.ID_CANCEL:
                    # отменяем операцию
                    return False
            elif result == wx.ID_NO:
                # пользователь не хочет сохранить текущий проект
                pass
            elif result == wx.ID_CANCEL:
                # пользователь хочет отменить операцию создания нового проекта полностью
                return False
        elif not self.project.is_saved(self.editor.GetText()):
            # текущие изменения в проекте не сохранены
            result = self.save_changes_md.ShowModal()
            if result == wx.ID_YES:
                # пользователь хочет сохранить изменения
                self.project.save(self.editor.GetText())
            elif result == wx.ID_NO:
                # пользователь не хочет сохранить изменения
                pass
            elif result == wx.ID_CANCEL:
                # пользователь хочет отменить операцию создания нового проекта полностью
                return False
        return True


    def updateUI(self):
        """Изменяет интерфейс в соответствии с открытым проектом."""
        # записываем сохранённый код в поле ввода
        self.editor.ClearAll()
        self.editor.AddText(self.project.get_code())
        self.SetTitle(f'{self.app_name} - {self.project.name}')
        self.save_changes_md.SetTitle(self.project.name)
        # выводим названия файлов с ресурсами в листбокс
        while self.res_lb.GetCount():
            self.res_lb.Delete(0)
        fnames = self.project.get_resources_names()
        self.res_lb.InsertItems(fnames, 0)
        # TODO: установка сцен
        # TODO: установка ресурсов


    def onCreateClick(self, event):
        """Создание нового проекта."""
        may_continue = self.suggest_saving()
        if may_continue:
            # создаём новый проект
            result = self.create_project_dd.ShowModal()
            if result == wx.ID_OK:
                path = self.create_project_dd.GetPath()
                print('Выбран каталог:', path)
                self.project = Project(path)
                self.updateUI()


    def onOpenClick(self, event):
        """Открыть существующий проект."""
        result = self.open_project_dd.ShowModal()
        if result == wx.ID_OK:
            path =self.open_project_dd.GetPath()
            print('Выбран каталог:', path)
            if not Project.is_project(path):
                wx.MessageBox('Указанная папка не содержит проекта.', 'Ошибка', wx.OK | wx.ICON_WARNING, self)
            else:
                may_continue = self.suggest_saving()
                if may_continue:
                    # открываем проект
                    self.project = Project(path)
                    self.updateUI()


    def onSaveClick(self, event):
        """Сохранение текущего проекта."""
        if self.project is None:
            # текущий проект ещё никуда не сохранён
            result = self.save_project_dd.ShowModal()
            if result == wx.ID_OK:
                path = self.save_project_dd.GetPath()
                self.project = Project(path)
            elif result == wx.ID_CANCEL:
                return
        self.project.save(self.editor.GetText())
        self.updateUI()


    def onStartClick(self, event):
        self.code_analyzer = code_analyzer.CodeAnalyzer()
        if self.editor.analyzed:
            words_for_parsing = self.code_analyzer.get_words_for_parsing(self.editor.analyzed)
            parserV2.getScenery(words_for_parsing, self.project.path+"/res/")
        else:
            words_for_parsing = []
        print(words_for_parsing)


    def getWordsForParsing(self):
        words_for_parsing = self.code_analyzer.get_words_for_parsing(self.editor.analyzed)
        return words_for_parsing


    def onStopClick(self, event):
        pass


    def onDocClick(self, event):
        if self.doc_dlg is None:
            self.doc_dlg = DocDialog(self, 'doc.html')
            self.doc_dlg.Show()


    def onHelpClick(self, event):
        if self.help_dlg is None:
            self.help_dlg = HelpDialog(self, 'help.html')
            self.help_dlg.Show()


    def onClose(self, event):
        may_exit = self.suggest_saving()
        if may_exit:
            self.Destroy()
        else:
            event.Veto()

    def add_res(self, event):
        if self.project is None:
            result = wx.MessageBox('Перед добавлением ресурсов необходимо сохранить проект. Создать?',
                                   'Проект не создан',
                                   wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_INFORMATION, self)
            if result != wx.YES:
                return
            self.onSaveClick(None)
            if self.project is None:
                # проект так и не создан
                return
        result = self.add_res_fd.ShowModal()
        if result == wx.ID_OK:
            fnames = self.add_res_fd.GetPaths()
            for fname in fnames:
                self.project.add_res(fname)
            self.updateUI()

    def remove_res(self, event):
        if not self.project is None:
            items_for_removing = self.res_lb.GetSelections()
            for item in items_for_removing:
                path = self.res_lb.GetString(item)
                self.project.remove_res(path)
            self.updateUI()



app = wx.App()

frame = MainWindow(None, 'Редактор Telegram-ботов')
frame.Show()

app.MainLoop()

# main.py
import sys
import os
import json
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Импорт наших модулей
from editor import CodeEditor
from game_preview import GamePreviewWidget
from auth import UserProfile
from dialogs import LoginDialog, SettingsDialog

class SuperPythonIDE(QMainWindow):
    """Главное окно IDE"""
    def __init__(self):
        super().__init__()
        self.user_profile = UserProfile()
        self.current_file = None
        self.initUI()
        self.show_login()
        self.setup_autosave()
        
    def initUI(self):
        self.setWindowTitle("SuperPython Game IDE - v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Установка иконки
        self.setWindowIcon(QIcon('icon.png'))
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QHBoxLayout()
        
        # Левая панель - файловый браузер
        self.file_browser = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_browser.setModel(self.file_model)
        self.file_browser.setRootIndex(self.file_model.index(os.getcwd()))
        self.file_browser.setMaximumWidth(250)
        self.file_browser.doubleClicked.connect(self.open_file_from_browser)
        
        # Центральная панель - редактор кода
        self.code_editor = CodeEditor()
        
        # Правая панель - предпросмотр игры
        self.preview_widget = GamePreviewWidget()
        self.preview_widget.setParent(self)
        
        # Разделители
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_browser)
        splitter.addWidget(self.code_editor)
        splitter.addWidget(self.preview_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Создание меню
        self.create_menus()
        
        # Создание панели инструментов
        self.create_toolbar()
        
        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Применение темной темы
        self.apply_dark_theme()
    
    def create_menus(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        new_action = QAction('Новый', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Сохранить как...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Правка
        edit_menu = menubar.addMenu('Правка')
        
        undo_action = QAction('Отменить', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.code_editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Повторить', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.code_editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('Вырезать', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.code_editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('Копировать', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.code_editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('Вставить', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.code_editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction('Найти', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        replace_action = QAction('Заменить', self)
        replace_action.setShortcut('Ctrl+H')
        replace_action.triggered.connect(self.replace_text)
        edit_menu.addAction(replace_action)
        
        # Меню Запуск
        run_menu = menubar.addMenu('Запуск')
        
        run_action = QAction('Запустить', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)
        
        debug_action = QAction('Отладка', self)
        debug_action.setShortcut('F9')
        run_menu.addAction(debug_action)
        
        # Меню Инструменты
        tools_menu = menubar.addMenu('Инструменты')
        
        terminal_action = QAction('Терминал', self)
        terminal_action.setShortcut('Ctrl+`')
        terminal_action.triggered.connect(self.open_terminal)
        tools_menu.addAction(terminal_action)
        
        pip_action = QAction('Менеджер пакетов', self)
        pip_action.triggered.connect(self.open_pip_manager)
        tools_menu.addAction(pip_action)
        
        # Меню Настройки
        settings_menu = menubar.addMenu('Настройки')
        
        preferences_action = QAction('Параметры', self)
        preferences_action.triggered.connect(self.open_settings)
        settings_menu.addAction(preferences_action)
        
        # Меню Профиль
        profile_menu = menubar.addMenu('Профиль')
        
        if self.user_profile.current_user:
            username = self.user_profile.current_user['username']
            profile_menu.addAction(f'Вошли как: {username}')
            profile_menu.addSeparator()
            
            logout_action = QAction('Выйти', self)
            logout_action.triggered.connect(self.logout)
            profile_menu.addAction(logout_action)
        else:
            login_action = QAction('Войти', self)
            login_action.triggered.connect(self.show_login)
            profile_menu.addAction(login_action)
        
        # Меню Помощь
        help_menu = menubar.addMenu('Помощь')
        
        docs_action = QAction('Документация', self)
        docs_action.setShortcut('F1')
        help_menu.addAction(docs_action)
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Кнопки
        new_btn = QAction(QIcon.fromTheme('document-new'), 'Новый', self)
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)
        
        open_btn = QAction(QIcon.fromTheme('document-open'), 'Открыть', self)
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)
        
        save_btn = QAction(QIcon.fromTheme('document-save'), 'Сохранить', self)
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        run_btn = QAction('▶️ Запустить', self)
        run_btn.triggered.connect(self.run_code)
        toolbar.addAction(run_btn)
        
        stop_btn = QAction('⏹️ Остановить', self)
        stop_btn.triggered.connect(self.stop_code)
        toolbar.addAction(stop_btn)
        
        toolbar.addSeparator()
        
        undo_btn = QAction('↶ Отменить', self)
        undo_btn.triggered.connect(self.code_editor.undo)
        toolbar.addAction(undo_btn)
        
        redo_btn = QAction('↷ Повторить', self)
        redo_btn.triggered.connect(self.code_editor.redo)
        toolbar.addAction(redo_btn)
    
    def apply_dark_theme(self):
        """Применение темной темы"""
        dark_style = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QMenuBar {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #4a4a4a;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #4a4a4a;
        }
        QMenu::item:selected {
            background-color: #4a4a4a;
        }
        QToolBar {
            background-color: #2b2b2b;
            border: none;
        }
        QPushButton {
            background-color: #4a4a4a;
            color: white;
            border: none;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        QTreeView {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
        }
        QTreeView::item:selected {
            background-color: #094771;
        }
        QStatusBar {
            background-color: #007acc;
            color: white;
        }
        QTabWidget::pane {
            background-color: #2b2b2b;
            border: 1px solid #4a4a4a;
        }
        QTabBar::tab {
            background-color: #3a3a3a;
            color: #ffffff;
            padding: 5px;
        }
        QTabBar::tab:selected {
            background-color: #4a4a4a;
        }
        """
        self.setStyleSheet(dark_style)
    
    def new_file(self):
        """Создание нового файла"""
        self.code_editor.clear()
        self.current_file = None
        self.status_bar.showMessage("Создан новый файл")
    
    def open_file(self):
        """Открытие файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            "",
            "Python файлы (*.py);;Все файлы (*.*)"
        )
        
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.code_editor.setText(content)
                self.current_file = file_path
                self.setWindowTitle(f"SuperPython Game IDE - {file_path}")
                self.status_bar.showMessage(f"Открыт файл: {file_path}")
    
    def open_file_from_browser(self, index):
        """Открытие файла из браузера"""
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path) and file_path.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.code_editor.setText(content)
                self.current_file = file_path
                self.setWindowTitle(f"SuperPython Game IDE - {file_path}")
                self.status_bar.showMessage(f"Открыт файл: {file_path}")
    
    def save_file(self):
        """Сохранение файла"""
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.code_editor.text())
                self.status_bar.showMessage(f"Файл сохранен: {self.current_file}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Сохранить как"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            "",
            "Python файлы (*.py);;Все файлы (*.*)"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.code_editor.text())
                self.current_file = file_path
                self.setWindowTitle(f"SuperPython Game IDE - {file_path}")
                self.status_bar.showMessage(f"Файл сохранен: {file_path}")
    
    def run_code(self):
        """Запуск кода"""
        self.preview_widget.run_game()
    
    def stop_code(self):
        """Остановка кода"""
        self.preview_widget.stop_game()
    
    def find_text(self):
        """Поиск текста"""
        text, ok = QInputDialog.getText(self, "Поиск", "Найти:")
        if ok and text:
            self.code_editor.findFirst(text, False, False, False, True)
    
    def replace_text(self):
        """Замена текста"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Заменить")
        layout = QFormLayout()
        
        find_edit = QLineEdit()
        replace_edit = QLineEdit()
        
        layout.addRow("Найти:", find_edit)
        layout.addRow("Заменить на:", replace_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addRow(buttons)
        dialog.setLayout(layout)
        
        if dialog.exec_():
            find_text = find_edit.text()
            replace_text = replace_edit.text()
            
            if find_text:
                content = self.code_editor.text()
                content = content.replace(find_text, replace_text)
                self.code_editor.setText(content)
    
    def open_terminal(self):
        """Открытие терминала"""
        if sys.platform == "win32":
            os.system("start cmd")
        else:
            os.system("gnome-terminal")
    
    def open_pip_manager(self):
        """Менеджер пакетов pip"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Менеджер пакетов")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        package_input = QLineEdit()
        package_input.setPlaceholderText("Введите название пакета...")
        install_btn = QPushButton("Установить")
        
        input_layout.addWidget(package_input)
        input_layout.addWidget(install_btn)
        
        packages_list = QTextEdit()
        packages_list.setReadOnly(True)
        
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True
        )
        packages_list.setText(result.stdout)
        
        def install_package():
            package = package_input.text()
            if package:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True
                )
                QMessageBox.information(dialog, "Результат", result.stdout)
        
        install_btn.clicked.connect(install_package)
        
        layout.addLayout(input_layout)
        layout.addWidget(QLabel("Установленные пакеты:"))
        layout.addWidget(packages_list)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def open_settings(self):
        """Открытие настроек"""
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def show_login(self):
        """Показ окна входа"""
        dialog = LoginDialog(self.user_profile)
        dialog.exec_()
        self.update_profile_menu()
    
    def logout(self):
        """Выход из аккаунта"""
        self.user_profile.current_user = None
        self.update_profile_menu()
        self.status_bar.showMessage("Вы вышли из аккаунта")
    
    def update_profile_menu(self):
        """Обновление меню профиля"""
        self.create_menus()
    
    def show_about(self):
        """О программе"""
        QMessageBox.about(
            self,
            "О программе",
            """<h2>SuperPython Game IDE v1.0</h2>
            <p>Мощная среда разработки для создания игр на Python</p>
            <p><b>Возможности:</b></p>
            <ul>
                <li>Подсветка синтаксиса Python</li>
                <li>Live preview для игр</li>
                <li>Встроенный отладчик</li>
                <li>Система профилей пользователей</li>
                <li>Автосохранение</li>
                <li>Менеджер пакетов</li>
            </ul>
            <p>© 2024 SuperPython IDE Team</p>"""
        )
    
    def setup_autosave(self):
        """Настройка автосохранения"""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(300000)  # Каждые 5 минут
    
    def autosave(self):
        """Автосохранение"""
        if self.current_file and self.code_editor.isModified():
            self.save_file()
            self.status_bar.showMessage("Автосохранение выполнено", 2000)
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        reply = QMessageBox.question(
            self,
            'Выход',
            'Вы действительно хотите выйти?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    app.setApplicationName("SuperPython Game IDE")
    app.setStyle('Fusion')
    
    ide = SuperPythonIDE()
    ide.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

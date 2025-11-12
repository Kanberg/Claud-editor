# dialogs.py
import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LoginDialog(QDialog):
    """Диалог входа в систему"""
    def __init__(self, user_profile):
        super().__init__()
        self.user_profile = user_profile
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        
        # Логотип
        title = QLabel("🚀 SuperPython Game IDE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4a9eff;")
        layout.addWidget(title)
        
        # Табы для входа/регистрации
        tabs = QTabWidget()
        
        # Вкладка входа
        login_tab = QWidget()
        login_layout = QFormLayout()
        
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        
        login_layout.addRow("Имя пользователя:", self.login_username)
        login_layout.addRow("Пароль:", self.login_password)
        
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.login)
        login_layout.addRow(login_btn)
        
        login_tab.setLayout(login_layout)
        tabs.addTab(login_tab, "Вход")
        
        # Вкладка регистрации
        register_tab = QWidget()
        register_layout = QFormLayout()
        
        self.reg_username = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_email = QLineEdit()
        
        register_layout.addRow("Имя пользователя:", self.reg_username)
        register_layout.addRow("Пароль:", self.reg_password)
        register_layout.addRow("Email (опционально):", self.reg_email)
        
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.register)
        register_layout.addRow(register_btn)
        
        register_tab.setLayout(register_layout)
        tabs.addTab(register_tab, "Регистрация")
        
        layout.addWidget(tabs)
        
        # Кнопка пропустить
        skip_btn = QPushButton("Пропустить (гостевой режим)")
        skip_btn.clicked.connect(self.accept)
        layout.addWidget(skip_btn)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        if username and password:
            success, message = self.user_profile.login(username, password)
            if success:
                QMessageBox.information(self, "Успех", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", message)
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
    
    def register(self):
        username = self.reg_username.text()
        password = self.reg_password.text()
        email = self.reg_email.text()
        
        if username and password:
            if len(password) < 6:
                QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 6 символов")
                return
                
            success, message = self.user_profile.register(username, password, email)
            if success:
                QMessageBox.information(self, "Успех", message)
                # Переключаемся на вкладку входа
                self.findChild(QTabWidget).setCurrentIndex(0)
                self.login_username.setText(username)
            else:
                QMessageBox.warning(self, "Ошибка", message)
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")

class SettingsDialog(QDialog):
    """Диалог настроек"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.load_settings()
        
    def initUI(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # Вкладка общих настроек
        general_tab = QWidget()
        general_layout = QFormLayout()
        
        # Тема
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная", "Светлая", "Синяя"])
        general_layout.addRow("Тема:", self.theme_combo)
        
        # Размер шрифта
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(11)
        general_layout.addRow("Размер шрифта:", self.font_size)
        
        # Автосохранение
        self.autosave = QCheckBox("Включить автосохранение")
        self.autosave.setChecked(True)
        general_layout.addRow(self.autosave)
        
        # Интервал автосохранения
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(5)
        self.autosave_interval.setSuffix(" минут")
        general_layout.addRow("Интервал автосохранения:", self.autosave_interval)
        
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "Общие")
        
        # Вкладка редактора
        editor_tab = QWidget()
        editor_layout = QFormLayout()
        
        # Табуляция
        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setValue(4)
        editor_layout.addRow("Ширина табуляции:", self.tab_width)
        
        # Перенос строк
        self.word_wrap = QCheckBox("Перенос строк")
        editor_layout.addRow(self.word_wrap)
        
        # Показывать пробелы
        self.show_whitespace = QCheckBox("Показывать пробелы")
        editor_layout.addRow(self.show_whitespace)
        
        # Подсветка синтаксиса
        self.syntax_highlight = QCheckBox("Подсветка синтаксиса")
        self.syntax_highlight.setChecked(True)
        editor_layout.addRow(self.syntax_highlight)
        
        # Автодополнение
        self.autocomplete = QCheckBox("Автодополнение кода")
        self.autocomplete.setChecked(True)
        editor_layout.addRow(self.autocomplete)
        
        editor_tab.setLayout(editor_layout)
        tabs.addTab(editor_tab, "Редактор")
        
        # Вкладка Python
        python_tab = QWidget()
        python_layout = QFormLayout()
        
        # Путь к Python
        python_path_layout = QHBoxLayout()
        self.python_path = QLineEdit(sys.executable)
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_python)
        python_path_layout.addWidget(self.python_path)
        python_path_layout.addWidget(browse_btn)
        python_layout.addRow("Путь к Python:", python_path_layout)
        
        # Версия Python
        version_label = QLabel(f"Версия: {sys.version.split()[0]}")
        python_layout.addRow(version_label)
        
        # Дополнительные аргументы
        self.python_args = QLineEdit()
        python_layout.addRow("Аргументы:", self.python_args)
        
        python_tab.setLayout(python_layout)
        tabs.addTab(python_tab, "Python")
        
        # Вкладка игрового движка
        game_tab = QWidget()
        game_layout = QFormLayout()
        
        # FPS
        self.fps = QSpinBox()
        self.fps.setRange(30, 144)
        self.fps.setValue(60)
        game_layout.addRow("FPS по умолчанию:", self.fps)
        
        # Разрешение
        self.resolution = QComboBox()
        self.resolution.addItems(["800x600", "1024x768", "1280x720", "1920x1080"])
        game_layout.addRow("Разрешение:", self.resolution)
        
        # Полноэкранный режим
        self.fullscreen = QCheckBox("Полноэкранный режим")
        game_layout.addRow(self.fullscreen)
        
        # Отладочный режим
        self.debug_mode = QCheckBox("Режим отладки")
        self.debug_mode.setChecked(True)
        game_layout.addRow(self.debug_mode)
        
        # VSync
        self.vsync = QCheckBox("Вертикальная синхронизация")
        game_layout.addRow(self.vsync)
        
        game_tab.setLayout(game_layout)
        tabs.addTab(game_tab, "Игровой движок")
        
        layout.addWidget(tabs)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def browse_python(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите интерпретатор Python",
            "",
            "Исполняемые файлы (*.exe);;Все файлы (*.*)"
        )
        if file_path:
            self.python_path.setText(file_path)
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                
                # Применяем загруженные настройки
                if 'theme' in settings:
                    index = self.theme_combo.findText(settings['theme'])
                    if index >= 0:
                        self.theme_combo.setCurrentIndex(index)
                
                if 'font_size' in settings:
                    self.font_size.setValue(settings['font_size'])
                
                if 'autosave' in settings:
                    self.autosave.setChecked(settings['autosave'])
                
                # И так далее для остальных настроек...
                
        except FileNotFoundError:
            pass  # Файл настроек еще не создан
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки: {str(e)}")
    
    def save_settings(self):
        """Сохранение настроек"""
        settings = self.get_settings_dict()
        
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
            
            QMessageBox.information(self, "Успех", "Настройки сохранены!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")
    
    def apply_settings(self):
        """Применение настроек без закрытия окна"""
        settings = self.get_settings_dict()
        
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
            
            QMessageBox.information(self, "Успех", "Настройки применены!")
            
            # Применяем настройки к родительскому окну, если оно есть
            if self.parent:
                self.apply_to_parent(settings)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {str(e)}")
    
    def get_settings_dict(self):
        """Получение словаря с настройками"""
        return {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size.value(),
            'autosave': self.autosave.isChecked(),
            'autosave_interval': self.autosave_interval.value(),
            'tab_width': self.tab_width.value(),
            'word_wrap': self.word_wrap.isChecked(),
            'show_whitespace': self.show_whitespace.isChecked(),
            'syntax_highlight': self.syntax_highlight.isChecked(),
            'autocomplete': self.autocomplete.isChecked(),
            'python_path': self.python_path.text(),
            'python_args': self.python_args.text(),
            'fps': self.fps.value(),
            'resolution': self.resolution.currentText(),
            'fullscreen': self.fullscreen.isChecked(),
            'debug_mode': self.debug_mode.isChecked(),
            'vsync': self.vsync.isChecked()
        }
    
    def apply_to_parent(self, settings):
        """Применение настроек к родительскому окну"""
        if hasattr(self.parent, 'code_editor'):
            # Применяем настройки редактора
            editor = self.parent.code_editor
            
            if settings['tab_width']:
                editor.setIndentationWidth(settings['tab_width'])
            
            if settings['font_size']:
                font = editor.lexer().defaultFont(0)
                font.setPointSize(settings['font_size'])
                editor.lexer().setDefaultFont(font)
            
            # Обновляем автосохранение
            if hasattr(self.parent, 'autosave_timer'):
                if settings['autosave']:
                    interval = settings['autosave_interval'] * 60000  # минуты в миллисекунды
                    self.parent.autosave_timer.setInterval(interval)
                    self.parent.autosave_timer.start()
                else:
                    self.parent.autosave_timer.stop()

# game_preview.py
import sys
import subprocess
import threading
import queue

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GamePreviewWidget(QWidget):
    """Виджет для предпросмотра игры"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.game_process = None
        self.output_queue = queue.Queue()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Панель управления
        control_panel = QHBoxLayout()
        self.run_btn = QPushButton("▶️ Запустить")
        self.stop_btn = QPushButton("⏹️ Остановить")
        self.restart_btn = QPushButton("🔄 Перезапустить")
        
        self.run_btn.clicked.connect(self.run_game)
        self.stop_btn.clicked.connect(self.stop_game)
        self.restart_btn.clicked.connect(self.restart_game)
        
        control_panel.addWidget(self.run_btn)
        control_panel.addWidget(self.stop_btn)
        control_panel.addWidget(self.restart_btn)
        control_panel.addStretch()
        
        # Область предпросмотра
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Встроенное окно для pygame
        self.game_container = QWidget()
        self.game_container.setMinimumSize(800, 600)
        self.game_container.setStyleSheet("background-color: #000000;")
        
        # Разделитель
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.game_container)
        splitter.addWidget(self.preview_area)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        layout.addLayout(control_panel)
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
    def run_game(self):
        """Запуск игры в отдельном процессе"""
        if self.game_process and self.game_process.poll() is None:
            self.preview_area.append("⚠️ Игра уже запущена!")
            return
            
        # Получаем код из редактора
        try:
            code = self.parent().parent().code_editor.text()
        except:
            self.preview_area.append("❌ Не удалось получить код из редактора")
            return
        
        # Сохраняем код во временный файл
        temp_file = "temp_game.py"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            self.preview_area.append(f"❌ Ошибка сохранения: {str(e)}")
            return
        
        # Запускаем в отдельном процессе
        try:
            self.game_process = subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Читаем вывод в отдельном потоке
            threading.Thread(target=self.read_output, daemon=True).start()
            
            self.preview_area.clear()
            self.preview_area.append("🎮 Игра запущена!")
            self.preview_area.append("-" * 50)
            
        except Exception as e:
            self.preview_area.append(f"❌ Ошибка запуска: {str(e)}")
    
    def read_output(self):
        """Чтение вывода из процесса игры"""
        if not self.game_process:
            return
            
        # Читаем stdout
        for line in self.game_process.stdout:
            if line.strip():
                QMetaObject.invokeMethod(
                    self.preview_area,
                    "append",
                    Qt.QueuedConnection,
                    Q_ARG(str, line.strip())
                )
        
        # Читаем stderr
        for line in self.game_process.stderr:
            if line.strip():
                QMetaObject.invokeMethod(
                    self.preview_area,
                    "append",
                    Qt.QueuedConnection,
                    Q_ARG(str, f"⚠️ {line.strip()}")
                )
        
        # Когда процесс завершится
        self.game_process.wait()
        QMetaObject.invokeMethod(
            self.preview_area,
            "append",
            Qt.QueuedConnection,
            Q_ARG(str, "-" * 50)
        )
        QMetaObject.invokeMethod(
            self.preview_area,
            "append",
            Qt.QueuedConnection,
            Q_ARG(str, f"✅ Программа завершена с кодом {self.game_process.returncode}")
        )
    
    def stop_game(self):
        """Остановка игры"""
        if self.game_process and self.game_process.poll() is None:
            self.game_process.terminate()
            self.preview_area.append("-" * 50)
            self.preview_area.append("⏹️ Игра остановлена пользователем")
        else:
            self.preview_area.append("ℹ️ Нет запущенной игры")
    
    def restart_game(self):
        """Перезапуск игры"""
        self.stop_game()
        QTimer.singleShot(500, self.run_game)
        self.preview_area.append("🔄 Перезапуск...")

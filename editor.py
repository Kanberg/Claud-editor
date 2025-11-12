# editor.py
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qsci import *

class CodeEditor(QsciScintilla):
    """Продвинутый редактор кода с подсветкой синтаксиса"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Настройка лексера Python
        lexer = QsciLexerPython()
        lexer.setDefaultFont(QFont('Consolas', 11))
        self.setLexer(lexer)
        
        # Цветовая схема (темная тема)
        self.setStyleSheet("""
            QsciScintilla {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        # Настройка цветов для разных элементов
        lexer.setColor(QColor("#569cd6"), QsciLexerPython.Keyword)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.DoubleQuotedString)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.SingleQuotedString)
        lexer.setColor(QColor("#608b4e"), QsciLexerPython.Comment)
        lexer.setColor(QColor("#4ec9b0"), QsciLexerPython.ClassName)
        lexer.setColor(QColor("#dcdcaa"), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor("#b5cea8"), QsciLexerPython.Number)
        
        # Настройка редактора
        self.setIndentationGuides(True)
        self.setIndentationWidth(4)
        self.setAutoIndent(True)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        # Номера строк
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#2d2d30"))
        self.setMarginsForegroundColor(QColor("#858585"))
        
        # Автодополнение
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        
        # Сворачивание кода
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        
        # Текущая строка
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2a2a2a"))
        
        # Полоса прокрутки
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 1)
        
        # Начальный текст
        self.setText("""# SuperPython Game IDE
# Начните писать ваш код здесь

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH = 800
HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Моя игра")
clock = pygame.time.Clock()

# Игровой цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Обновление
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
""")

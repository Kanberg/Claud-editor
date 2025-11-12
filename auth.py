# auth.py
import hashlib
import sqlite3
from datetime import datetime

class UserProfile:
    """Система профилей пользователей"""
    def __init__(self):
        self.db_path = "users.db"
        self.init_database()
        self.current_user = None
        
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                settings TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email=""):
        """Регистрация нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, self.hash_password(password), email)
            )
            conn.commit()
            return True, "Регистрация успешна!"
        except sqlite3.IntegrityError:
            return False, "Пользователь уже существует!"
        except Exception as e:
            return False, f"Ошибка регистрации: {str(e)}"
        finally:
            conn.close()
    
    def login(self, username, password):
        """Вход в систему"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, self.hash_password(password))
            )
            
            user = cursor.fetchone()
            
            if user:
                self.current_user = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[3] if user[3] else ""
                }
                
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user[0],)
                )
                conn.commit()
                return True, "Вход выполнен успешно!"
            else:
                return False, "Неверное имя пользователя или пароль!"
                
        except Exception as e:
            return False, f"Ошибка входа: {str(e)}"
        finally:
            conn.close()
    
    def save_project(self, name, code):
        """Сохранение проекта пользователя"""
        if not self.current_user:
            return False, "Необходимо войти в систему"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO projects (user_id, name, code) VALUES (?, ?, ?)",
                (self.current_user['id'], name, code)
            )
            conn.commit()
            return True, "Проект сохранен"
        except Exception as e:
            return False, f"Ошибка сохранения: {str(e)}"
        finally:
            conn.close()
    
    def load_projects(self):
        """Загрузка проектов пользователя"""
        if not self.current_user:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, name, modified_at FROM projects WHERE user_id = ? ORDER BY modified_at DESC",
                (self.current_user['id'],)
            )
            return cursor.fetchall()
        except:
            return []
        finally:
            conn.close()
    
    def load_project_code(self, project_id):
        """Загрузка кода проекта"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT code FROM projects WHERE id = ? AND user_id = ?",
                (project_id, self.current_user['id'])
            )
            result = cursor.fetchone()
            return result[0] if result else ""
        except:
            return ""
        finally:
            conn.close()

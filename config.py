import os
from datetime import timedelta

class Config:
    # Основные настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'school-robotics-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///school_robotics.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    
    # Другие настройки
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    
    @staticmethod
    def init_app(app):
        # Создание папок если не существуют
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('instance', exist_ok=True)
import os
from flask import Flask
from init_db import init_database

def create_app():
    app = Flask(__name__)
    app.secret_key = 'school-robotics-secret-key-2024'
    
    # Инициализация базы данных
    with app.app_context():
        init_database()
    
    # Регистрация blueprint'ов
    from modules.auth import auth_bp
    from modules.dashboard import dashboard_bp
    from modules.students import students_bp
    from modules.courses import courses_bp
    from modules.groups import groups_bp
    from modules.lessons import lessons_bp
    from modules.journal import journal_bp
    from modules.projects import projects_bp
    from modules.achievements import achievements_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(achievements_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_database():
    """Инициализация базы данных"""
    db_path = 'instance/school_robotics.db'
    
    # Создаем папку instance если не существует
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Таблица пользователей
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'teacher',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица студентов
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_code TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                birth_date DATE,
                parent_name TEXT,
                parent_phone TEXT,
                parent_email TEXT,
                grade TEXT,
                school TEXT,
                notes TEXT,
                total_exp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица курсов
        conn.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                difficulty_level TEXT,
                duration_weeks INTEGER,
                price DECIMAL(10,2),
                max_students INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица групп
        conn.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_code TEXT UNIQUE NOT NULL,
                course_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                schedule TEXT,
                start_date DATE,
                end_date DATE,
                classroom TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (course_id) REFERENCES courses (id),
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица записи студентов в группы
        conn.execute('''
            CREATE TABLE IF NOT EXISTS student_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                enrolled_date DATE DEFAULT CURRENT_DATE,
                completion_status TEXT DEFAULT 'studying',
                final_grade TEXT,
                notes TEXT,
                current_exp INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (group_id) REFERENCES groups (id),
                UNIQUE(student_id, group_id)
            )
        ''')
        
        # Таблица занятий
        conn.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                lesson_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                lesson_date DATE NOT NULL,
                start_time TIME,
                end_time TIME,
                topic TEXT,
                materials TEXT,
                homework TEXT,
                status TEXT DEFAULT 'planned',
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        ''')
        
        # Таблица журнала
        conn.execute('''
            CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                grade INTEGER,
                behavior TEXT DEFAULT 'good',
                participation TEXT DEFAULT 'active',
                comments TEXT,
                exp_earned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                FOREIGN KEY (student_id) REFERENCES students (id),
                UNIQUE(lesson_id, student_id)
            )
        ''')
        
        # Таблица проектов
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                project_type TEXT,
                technologies TEXT,
                github_url TEXT,
                demo_url TEXT,
                images TEXT,
                video_url TEXT,
                status TEXT DEFAULT 'completed',
                rating INTEGER,
                featured BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        ''')
        
        # Таблица достижений
        conn.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                exp_reward INTEGER DEFAULT 100,
                criteria_type TEXT,
                criteria_value INTEGER,
                rarity TEXT DEFAULT 'common'
            )
        ''')
        
        # Таблица полученных достижений
        conn.execute('''
            CREATE TABLE IF NOT EXISTS student_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                group_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id),
                FOREIGN KEY (group_id) REFERENCES groups (id),
                UNIQUE(student_id, achievement_id, group_id)
            )
        ''')
        
        # Таблица уровней
        conn.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                level INTEGER PRIMARY KEY,
                exp_required INTEGER NOT NULL,
                title TEXT
            )
        ''')
        
        # Создаем администратора по умолчанию
        admin_exists = conn.execute(
            'SELECT id FROM users WHERE username = ?', ('admin',)
        ).fetchone()
        
        if not admin_exists:
            password_hash = generate_password_hash('admin123')
            conn.execute(
                'INSERT INTO users (username, password_hash, email, full_name, role) VALUES (?, ?, ?, ?, ?)',
                ('admin', password_hash, 'admin@robotics-school.ru', 'Администратор', 'admin')
            )
        
        # Добавляем достижения по умолчанию - ИСПРАВЛЕННЫЙ ЗАПРОС
        default_achievements = [
            ('first_project', 'Первый проект', 'Создал первый проект', '🏆', 100, 'projects_count', 1, 'common'),
            ('perfect_attendance', 'Идеальная посещаемость', 'Посетил 10 занятий подряд', '⭐', 150, 'attendance_streak', 10, 'rare'),
            ('coding_master', 'Мастер кода', 'Получил 5 пятерок подряд', '💻', 200, 'high_grades_streak', 5, 'epic'),
            ('robot_builder', 'Строитель роботов', 'Завершил 3 проекта с роботами', '🤖', 250, 'robot_projects', 3, 'legendary'),
            ('quick_learner', 'Быстрый ученик', 'Достиг 5 уровня', '🚀', 300, 'level', 5, 'rare'),
            ('team_player', 'Командный игрок', 'Участвовал в 5 групповых проектах', '👥', 150, 'team_projects', 5, 'common'),
            ('creative_mind', 'Творческий ум', 'Создал проект с инновационным решением', '💡', 200, 'innovative_projects', 1, 'epic')
        ]
        
        for achievement in default_achievements:
            conn.execute('''
                INSERT OR IGNORE INTO achievements 
                (name, description, icon, exp_reward, criteria_type, criteria_value, rarity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', achievement[:7])  # Берем только 7 значений, так как rarity уже есть в таблице по умолчанию
        
        # Добавляем уровни
        levels = [
            (1, 0, 'Новичок'),
            (2, 100, 'Ученик'),
            (3, 300, 'Исследователь'),
            (4, 600, 'Изобретатель'),
            (5, 1000, 'Инженер'),
            (6, 1500, 'Мастер'),
            (7, 2100, 'Эксперт'),
            (8, 2800, 'Гуру'),
            (9, 3600, 'Виртуоз'),
            (10, 4500, 'Легенда')
        ]
        
        for level in levels:
            conn.execute('''
                INSERT OR IGNORE INTO levels (level, exp_required, title)
                VALUES (?, ?, ?)
            ''', level)
        
        conn.commit()
        print("✅ База данных успешно инициализирована!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
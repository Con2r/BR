from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager

courses_bp = Blueprint('courses', __name__)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('instance/school_robotics.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@courses_bp.route('/courses')
@login_required
def list_courses():
    try:
        with get_db_connection() as conn:
            courses = conn.execute('''
                SELECT c.*, COUNT(g.id) as group_count
                FROM courses c
                LEFT JOIN groups g ON c.id = g.course_id AND g.status = 'active'
                WHERE c.status = 'active'
                GROUP BY c.id
                ORDER BY c.title
            ''').fetchall()
            
        return render_template('courses/list.html', courses=courses)
        
    except Exception as e:
        flash('Ошибка загрузки списка курсов', 'error')
        return render_template('courses/list.html', courses=[])

@courses_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        try:
            course_data = {
                'course_code': request.form.get('course_code'),
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'difficulty_level': request.form.get('difficulty_level'),
                'duration_weeks': request.form.get('duration_weeks', type=int) or 8,
                'price': request.form.get('price', type=float) or 0,
                'max_students': request.form.get('max_students', type=int) or 12
            }
            
            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO courses 
                    (course_code, title, description, difficulty_level, duration_weeks, price, max_students)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', tuple(course_data.values()))
                conn.commit()
                
            flash('Курс успешно добавлен', 'success')
            return redirect(url_for('courses.list_courses'))
            
        except sqlite3.IntegrityError:
            flash('Курс с таким кодом уже существует', 'error')
        except Exception as e:
            flash('Ошибка при добавлении курса', 'error')
    
    return render_template('courses/add.html')
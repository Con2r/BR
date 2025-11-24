from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager

lessons_bp = Blueprint('lessons', __name__)

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

@lessons_bp.route('/lessons')
@login_required
def list_lessons():
    try:
        with get_db_connection() as conn:
            lessons = conn.execute('''
                SELECT l.*, g.group_code, c.title as course_title
                FROM lessons l
                JOIN groups g ON l.group_id = g.id
                JOIN courses c ON g.course_id = c.id
                ORDER BY l.lesson_date DESC, l.start_time
            ''').fetchall()
            
        return render_template('lessons/list.html', lessons=lessons)
                             
    except Exception as e:
        flash('Ошибка загрузки списка занятий', 'error')
        return render_template('lessons/list.html', lessons=[])
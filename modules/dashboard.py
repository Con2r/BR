from flask import Blueprint, render_template, session
import sqlite3
from contextlib import contextmanager
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('instance/school_robotics.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        with get_db_connection() as conn:
            stats = conn.execute('''
                SELECT 
                    (SELECT COUNT(*) FROM students WHERE status = 'active') as active_students,
                    (SELECT COUNT(*) FROM courses WHERE status = 'active') as active_courses,
                    (SELECT COUNT(*) FROM groups WHERE status = 'active') as active_groups,
                    (SELECT COUNT(*) FROM users WHERE role = 'teacher') as teachers_count,
                    (SELECT COUNT(*) FROM lessons WHERE lesson_date = date('now')) as today_lessons
            ''').fetchone()
            
            recent_students = conn.execute('''
                SELECT * FROM students 
                WHERE status = 'active'
                ORDER BY created_at DESC 
                LIMIT 5
            ''').fetchall()
            
            upcoming_lessons = conn.execute('''
                SELECT l.*, g.group_code, c.title as course_title
                FROM lessons l
                JOIN groups g ON l.group_id = g.id
                JOIN courses c ON g.course_id = c.id
                WHERE l.lesson_date >= date('now')
                ORDER BY l.lesson_date, l.start_time
                LIMIT 5
            ''').fetchall()
            
        return render_template('dashboard/dashboard.html', 
                             stats=stats, 
                             recent_students=recent_students,
                             upcoming_lessons=upcoming_lessons)
                             
    except Exception as e:
        return render_template('dashboard/dashboard.html', stats=None, recent_students=[], upcoming_lessons=[])
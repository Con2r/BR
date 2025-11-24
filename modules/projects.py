from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager

projects_bp = Blueprint('projects', __name__)

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

@projects_bp.route('/projects')
@login_required
def list_projects():
    try:
        with get_db_connection() as conn:
            projects = conn.execute('''
                SELECT p.*, s.full_name as student_name, g.group_code
                FROM projects p
                JOIN students s ON p.student_id = s.id
                JOIN groups g ON p.group_id = g.id
                ORDER BY p.rating DESC, p.created_at DESC
            ''').fetchall()
            
        return render_template('projects/list.html', projects=projects)
        
    except Exception as e:
        flash('Ошибка загрузки проектов', 'error')
        return render_template('projects/list.html', projects=[])
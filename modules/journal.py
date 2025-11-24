from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager

journal_bp = Blueprint('journal', __name__)

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

@journal_bp.route('/journal')
@login_required
def journal_main():
    try:
        group_id = request.args.get('group_id', type=int)
        
        with get_db_connection() as conn:
            groups = conn.execute('''
                SELECT g.*, c.title as course_title 
                FROM groups g 
                JOIN courses c ON g.course_id = c.id 
                WHERE g.status = "active"
            ''').fetchall()
            
            if group_id:
                students = conn.execute('''
                    SELECT s.*, sg.current_exp
                    FROM student_groups sg
                    JOIN students s ON sg.student_id = s.id
                    WHERE sg.group_id = ? AND sg.completion_status = 'studying'
                    ORDER BY s.full_name
                ''', (group_id,)).fetchall()
                
                return render_template('journal/journal.html', 
                                     groups=groups, 
                                     selected_group=group_id,
                                     students=students)
            else:
                return render_template('journal/journal.html', 
                                     groups=groups, 
                                     selected_group=None,
                                     students=[])
                             
    except Exception as e:
        flash('Ошибка загрузки журнала', 'error')
        return render_template('journal/journal.html', groups=[], students=[])
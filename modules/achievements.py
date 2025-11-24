from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager

achievements_bp = Blueprint('achievements', __name__)

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

@achievements_bp.route('/achievements')
@login_required
def list_achievements():
    try:
        with get_db_connection() as conn:
            achievements = conn.execute('SELECT * FROM achievements ORDER BY rarity, exp_reward DESC').fetchall()
            
        return render_template('achievements/list.html', achievements=achievements)
        
    except Exception as e:
        flash('Ошибка загрузки достижений', 'error')
        return render_template('achievements/list.html', achievements=[])
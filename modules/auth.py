from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import sqlite3
from contextlib import contextmanager

auth_bp = Blueprint('auth', __name__)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('instance/school_robotics.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            with get_db_connection() as conn:
                user = conn.execute(
                    'SELECT * FROM users WHERE username = ?', (username,)
                ).fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session['full_name'] = user['full_name']
                    
                    flash(f'Добро пожаловать, {user["full_name"]}!', 'success')
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    flash('Неверное имя пользователя или пароль', 'error')
                    
        except Exception as e:
            flash('Ошибка входа в систему', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))
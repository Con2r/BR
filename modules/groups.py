from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager

groups_bp = Blueprint('groups', __name__)

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

@groups_bp.route('/groups')
@login_required
def list_groups():
    try:
        with get_db_connection() as conn:
            groups = conn.execute('''
                SELECT g.*, c.title as course_title, u.full_name as teacher_name,
                       COUNT(sg.id) as student_count
                FROM groups g
                JOIN courses c ON g.course_id = c.id
                JOIN users u ON g.teacher_id = u.id
                LEFT JOIN student_groups sg ON g.id = sg.group_id AND sg.completion_status = 'studying'
                WHERE g.status = 'active'
                GROUP BY g.id
                ORDER BY g.start_date DESC
            ''').fetchall()
            
        return render_template('groups/list.html', groups=groups)
        
    except Exception as e:
        flash('Ошибка загрузки списка групп', 'error')
        return render_template('groups/list.html', groups=[])

@groups_bp.route('/groups/add', methods=['GET', 'POST'])
@login_required
def add_group():
    if request.method == 'POST':
        try:
            group_data = {
                'group_code': request.form.get('group_code'),
                'course_id': request.form.get('course_id', type=int),
                'teacher_id': 1,
                'schedule': request.form.get('schedule'),
                'start_date': request.form.get('start_date'),
                'end_date': request.form.get('end_date'),
                'classroom': request.form.get('classroom')
            }
            
            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO groups 
                    (group_code, course_id, teacher_id, schedule, start_date, end_date, classroom)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', tuple(group_data.values()))
                conn.commit()
                
            flash('Группа успешно создана', 'success')
            return redirect(url_for('groups.list_groups'))
            
        except sqlite3.IntegrityError:
            flash('Группа с таким кодом уже существует', 'error')
        except Exception as e:
            flash('Ошибка при создании группы', 'error')
    
    # Получаем список курсов для формы
    try:
        with get_db_connection() as conn:
            courses = conn.execute('SELECT id, title FROM courses WHERE status = "active"').fetchall()
    except:
        courses = []
    
    return render_template('groups/add.html', courses=courses)
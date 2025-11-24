from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from contextlib import contextmanager
from datetime import date

students_bp = Blueprint('students', __name__)

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

@students_bp.route('/students')
@login_required
def list_students():
    status_filter = request.args.get('status', 'active')
    
    try:
        with get_db_connection() as conn:
            if status_filter == 'all':
                students = conn.execute('''
                    SELECT s.*, COUNT(sg.id) as group_count
                    FROM students s
                    LEFT JOIN student_groups sg ON s.id = sg.student_id AND sg.completion_status = 'studying'
                    GROUP BY s.id
                    ORDER BY s.full_name
                ''').fetchall()
            else:
                students = conn.execute('''
                    SELECT s.*, COUNT(sg.id) as group_count
                    FROM students s
                    LEFT JOIN student_groups sg ON s.id = sg.student_id AND sg.completion_status = 'studying'
                    WHERE s.status = ?
                    GROUP BY s.id
                    ORDER BY s.full_name
                ''', (status_filter,)).fetchall()
            
        return render_template('students/list.html', 
                             students=students, 
                             current_status=status_filter)
                             
    except Exception as e:
        flash('Ошибка загрузки списка студентов', 'error')
        return render_template('students/list.html', students=[])

@students_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        try:
            student_data = {
                'student_code': request.form.get('student_code'),
                'full_name': request.form.get('full_name'),
                'birth_date': request.form.get('birth_date'),
                'parent_name': request.form.get('parent_name'),
                'parent_phone': request.form.get('parent_phone'),
                'parent_email': request.form.get('parent_email'),
                'grade': request.form.get('grade'),
                'school': request.form.get('school'),
                'notes': request.form.get('notes')
            }
            
            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO students 
                    (student_code, full_name, birth_date, parent_name, parent_phone, parent_email, grade, school, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', tuple(student_data.values()))
                conn.commit()
                
            flash('Студент успешно добавлен', 'success')
            return redirect(url_for('students.list_students'))
            
        except sqlite3.IntegrityError:
            flash('Студент с таким кодом уже существует', 'error')
        except Exception as e:
            flash('Ошибка при добавлении студента', 'error')
    
    return render_template('students/add.html')

@students_bp.route('/students/<int:student_id>')
@login_required
def student_detail(student_id):
    try:
        with get_db_connection() as conn:
            student = conn.execute(
                'SELECT * FROM students WHERE id = ?', (student_id,)
            ).fetchone()
            
            if not student:
                flash('Студент не найден', 'error')
                return redirect(url_for('students.list_students'))
            
            groups = conn.execute('''
                SELECT g.*, c.title as course_title, sg.enrolled_date, sg.completion_status
                FROM student_groups sg
                JOIN groups g ON sg.group_id = g.id
                JOIN courses c ON g.course_id = c.id
                WHERE sg.student_id = ?
                ORDER BY sg.enrolled_date DESC
            ''', (student_id,)).fetchall()
            
        return render_template('students/detail.html', 
                             student=student, 
                             groups=groups)
                             
    except Exception as e:
        flash('Ошибка загрузки информации о студенте', 'error')
        return redirect(url_for('students.list_students'))
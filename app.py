from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import logging
from models import db, User, Student, Group, Grade, Mission, StudentProgress, Achievement, StudentAchievement, Challenge, ChallengeSubmission
from forms import LoginForm, StudentForm, GroupForm, GradeForm
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


# Инициализация расширений
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему'

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    with app.app_context():
        db.create_all()

        # Создание администратора
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            logger.info("Создан пользователь-администратор")

        # Создание тестового ученика и группы
        student_email = 'student@example.com'
        if not User.query.filter_by(username=student_email).first():
            student_user = User(username=student_email, is_admin=False)
            student_user.set_password('student123')
            db.session.add(student_user)
            db.session.flush()

            group = Group.query.first()
            if not group:
                group = Group(name='Юные робототехники', description='Группа для начинающих робототехников')
                db.session.add(group)
                db.session.flush()

            student = Student(
                first_name='Алексей',
                last_name='Иванов',
                email=student_email,
                group_id=group.id
            )
            db.session.add(student)

        # Создание миссий
        if not Mission.query.first():
            missions = [
                Mission(title="Основы программирования роботов", description="Изучите базовые команды для управления роботами...", difficulty="beginner", category="programming", points_reward=100, level=1),
                Mission(title="Сборка первого робота", description="Практическое занятие по сборке мобильного робота...", difficulty="beginner", category="mechanics", points_reward=150, level=2),
                Mission(title="Электронные схемы и датчики", description="Работа с электронными компонентами...", difficulty="intermediate", category="electronics", points_reward=200, level=3),
                Mission(title="Автономная навигация", description="Программирование робота для автономного движения...", difficulty="intermediate", category="programming", points_reward=250, level=4),
                Mission(title="Соревновательный робот", description="Проектирование и создание робота для участия в соревнованиях...", difficulty="advanced", category="mechanics", points_reward=300, level=5)
            ]
            db.session.add_all(missions)
            logger.info("Созданы тестовые миссии")

        # Создание достижений
        if not Achievement.query.first():
            achievements = [
                Achievement(name="Первый шаг", description="Завершите первую миссию", icon="🚀", points_reward=50, criteria_type="missions_completed", criteria_value=1),
                Achievement(name="Начинающий робототехник", description="Завершите 5 миссий", icon="🤖", points_reward=100, criteria_type="missions_completed", criteria_value=5),
                Achievement(name="Опытный инженер", description="Завершите 10 миссий", icon="🔧", points_reward=200, criteria_type="missions_completed", criteria_value=10),
                Achievement(name="Мастер кода", description="Решите 3 программистских челленджа", icon="💻", points_reward=150, criteria_type="challenges_solved", criteria_value=3),
                Achievement(name="Собиратель знаний", description="Заработайте 1000 очков опыта", icon="⭐", points_reward=100, criteria_type="points_earned", criteria_value=1000),
                Achievement(name="Секретное достижение", description="Найдите скрытое достижение", icon="🔍", points_reward=500, criteria_type="secret", criteria_value=1, is_secret=True)
            ]
            db.session.add_all(achievements)
            logger.info("Созданы тестовые достижения")

        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Система достижений ---
def check_achievements(student_id, achievement_type, value=1):
    student = Student.query.get(student_id)
    if not student:
        return None

    achievements = Achievement.query.filter_by(criteria_type=achievement_type).all()
    for achievement in achievements:
        condition_met = False

        if achievement_type == "missions_completed":
            count = StudentProgress.query.filter_by(student_id=student_id, completed=True).count()
            condition_met = count >= achievement.criteria_value
        elif achievement_type == "points_earned":
            condition_met = student.experience_points >= achievement.criteria_value
        elif achievement_type == "challenges_solved":
            count = ChallengeSubmission.query.filter_by(student_id=student_id, passed=True).count()
            condition_met = count >= achievement.criteria_value
        elif achievement_type == "secret":
            condition_met = True

        if condition_met:
            if not StudentAchievement.query.filter_by(student_id=student_id, achievement_id=achievement.id).first():
                student_achievement = StudentAchievement(student_id=student_id, achievement_id=achievement.id)
                db.session.add(student_achievement)
                student.experience_points += achievement.points_reward
                update_student_level(student)
                db.session.commit()
                logger.info(f"Выдано достижение '{achievement.name}' для ученика {student_id}")
                return achievement
    return None

def update_student_level(student):
    levels = {1: 0, 2: 500, 3: 1000, 4: 2000, 5: 4000}
    new_level = 1
    for level, required_xp in levels.items():
        if student.experience_points >= required_xp:
            new_level = level

    if new_level > student.level:
        student.level = new_level
        db.session.add(student)
        db.session.commit()
        return True
    return False

# --- Маршруты ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            logger.info(f"Вход выполнен: {user.username}")
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Неверный логин или пароль', 'error')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logger.info(f"Выход: {current_user.username}")
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    missions = Mission.query.filter_by(is_active=True).order_by(Mission.level).all()
    completed_levels = []
    current_level = 1

    if current_user.is_authenticated and not current_user.is_admin:
        student = Student.query.filter_by(email=current_user.username).first()
        if student:
            completed_levels = [p.mission.level for p in student.progress if p.completed]
            current_level = (max(completed_levels) + 1) if completed_levels else 1

    return render_template('index.html', missions=missions, current_level=current_level, completed_levels=completed_levels)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    student = Student.query.filter_by(email=current_user.username).first()
    if not student:
        flash('Профиль ученика не найден.', 'error')
        return redirect(url_for('logout'))

    completed_levels = [p.mission.level for p in student.progress if p.completed]
    current_level = (max(completed_levels) + 1) if completed_levels else 1
    missions = Mission.query.filter_by(is_active=True).order_by(Mission.level).all()

    student_achievements = StudentAchievement.query.filter_by(student_id=student.id).all()
    all_achievements = Achievement.query.filter_by(is_secret=False).all()

    return render_template('dashboard.html',
                         student=student,
                         missions=missions,
                         completed_levels=completed_levels,
                         current_level=current_level,
                         student_achievements=student_achievements,
                         all_achievements=all_achievements)

@app.route('/mission/<int:level>')
@login_required
def mission_detail(level):
    if current_user.is_admin:
        return redirect(url_for('index'))

    mission = Mission.query.filter_by(level=level, is_active=True).first_or_404()
    student = Student.query.filter_by(email=current_user.username).first()
    if not student:
        flash('Ученик не найден', 'error')
        return redirect(url_for('index'))

    completed_levels = [p.mission.level for p in student.progress if p.completed]
    if level > (max(completed_levels) + 1 if completed_levels else 1):
        flash('Эта миссия еще не доступна', 'error')
        return redirect(url_for('index'))

    is_completed = any(p.completed and p.mission_id == mission.id for p in student.progress)
    return render_template('mission_detail.html', mission=mission, level=level, is_completed=is_completed, student=student)

@app.route('/complete/<int:level>', methods=['POST'])
@login_required
def complete_mission(level):
    if current_user.is_admin:
        return redirect(url_for('index'))

    mission = Mission.query.filter_by(level=level, is_active=True).first_or_404()
    student = Student.query.filter_by(email=current_user.username).first()
    if not student:
        flash('Ученик не найден', 'error')
        return redirect(url_for('index'))

    existing = StudentProgress.query.filter_by(student_id=student.id, mission_id=mission.id).first()

    if existing and existing.completed:
        flash('Миссия уже выполнена', 'info')
        return redirect(url_for('dashboard'))

    if existing:
        existing.completed = True
        existing.completed_at = datetime.utcnow()
        existing.score = mission.points_reward
    else:
        progress = StudentProgress(
            student_id=student.id,
            mission_id=mission.id,
            completed=True,
            completed_at=datetime.utcnow(),
            score=mission.points_reward
        )
        db.session.add(progress)

    student.experience_points += mission.points_reward
    new_achievement = check_achievements(student.id, "missions_completed")
    level_up = update_student_level(student)

    db.session.commit()

    flash('Миссия отмечена как выполненная!', 'success')
    if level_up:
        flash(f'🎉 Поздравляем! Вы достигли {student.level} уровня!', 'success')
    if new_achievement:
        flash(f'🏆 Новое достижение: {new_achievement.name}! +{new_achievement.points_reward} XP', 'success')

    return redirect(url_for('dashboard'))

@app.route('/achievements')
@login_required
def achievements_page():
    if current_user.is_admin:
        return redirect(url_for('index'))

    student = Student.query.filter_by(email=current_user.username).first()
    if not student:
        return redirect(url_for('index'))

    all_achievements = Achievement.query.all()
    earned_ids = [sa.achievement_id for sa in StudentAchievement.query.filter_by(student_id=student.id).all()]

    return render_template('achievements.html',
                         student=student,
                         all_achievements=all_achievements,
                         earned_achievement_ids=earned_ids)

# === Админ-панель ===
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))

    stats = {
        'students_count': Student.query.count(),
        'groups_count': Group.query.count(),
        'missions_count': Mission.query.count(),
        'recent_grades': Grade.query.order_by(Grade.created_at.desc()).limit(5).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/students', methods=['GET', 'POST'])
@login_required
def admin_students():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))

    form = StudentForm()
    form.group_id.choices = [(g.id, g.name) for g in Group.query.all()]

    # ИСПРАВЛЕНИЕ: Используем правильную проверку формы
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(username=form.email.data).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('admin/students.html', form=form, students=Student.query.all())

        user = User(username=form.email.data, is_admin=False)
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()

        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            group_id=form.group_id.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Ученик успешно добавлен', 'success')
        return redirect(url_for('admin_students'))

    students = Student.query.all()
    return render_template('admin/students.html', form=form, students=students)

@app.route('/admin/groups', methods=['GET', 'POST'])
@login_required
def admin_groups():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))

    form = GroupForm()
    # ИСПРАВЛЕНИЕ: Используем правильную проверку формы
    if request.method == 'POST' and form.validate():
        group = Group(name=form.name.data, description=form.description.data)
        db.session.add(group)
        db.session.commit()
        flash('Группа создана', 'success')
        return redirect(url_for('admin_groups'))

    groups = Group.query.all()
    return render_template('admin/groups.html', form=form, groups=groups)

@app.route('/admin/grades', methods=['GET', 'POST'])
@login_required
def admin_grades():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))

    form = GradeForm()
    form.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in Student.query.all()]

    # ИСПРАВЛЕНИЕ: Используем правильную проверку формы
    if request.method == 'POST' and form.validate():
        grade = Grade(
            student_id=form.student_id.data,
            lesson_date=form.lesson_date.data,
            task_grade=form.task_grade.data,
            behavior_grade=form.behavior_grade.data,
            notes=form.notes.data
        )
        db.session.add(grade)
        db.session.commit()
        flash('Оценка добавлена', 'success')
        return redirect(url_for('admin_grades'))

    grades = Grade.query.order_by(Grade.lesson_date.desc()).all()
    return render_template('admin/grades.html', form=form, grades=grades)

@app.route('/admin/student/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        # обновить данные
        form.populate_obj(student)
        db.session.commit()
        return redirect(url_for('admin_students'))
    return render_template('admin/edit_student.html', form=form)

# Запуск приложения
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
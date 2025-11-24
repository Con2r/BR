from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)  # Увеличено до 128 для надёжности
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        """Хэширование пароля перед сохранением"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    students = db.relationship('Student', back_populates='group', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Group {self.name}>"


class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    experience_points = db.Column(db.Integer, default=0, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)

    # Связи (явное указание back_populates)
    group = db.relationship('Group', back_populates='students')
    grades = db.relationship('Grade', back_populates='student', lazy='select', cascade='all, delete-orphan')
    progress = db.relationship('StudentProgress', back_populates='student', lazy='select', cascade='all, delete-orphan')
    achievements = db.relationship('StudentAchievement', back_populates='student', lazy='select', cascade='all, delete-orphan')
    challenge_submissions = db.relationship('ChallengeSubmission', back_populates='student', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"


class Grade(db.Model):
    __tablename__ = 'grade'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False)
    task_grade = db.Column(db.Integer, nullable=True)
    behavior_grade = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', back_populates='grades')

    def __repr__(self):
        return f"<Grade student_id={self.student_id} date={self.lesson_date}>"


class Mission(db.Model):
    __tablename__ = 'mission'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='beginner', nullable=False)
    category = db.Column(db.String(50), default='programming', nullable=False)
    points_reward = db.Column(db.Integer, default=100, nullable=False)
    level = db.Column(db.Integer, unique=True, nullable=False, index=True)  # Индекс для быстрого поиска по уровню
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    progress_records = db.relationship('StudentProgress', back_populates='mission', lazy='select')

    def __repr__(self):
        return f"<Mission {self.title} (Level {self.level})>"


class StudentProgress(db.Model):
    __tablename__ = 'student_progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', back_populates='progress')
    mission = db.relationship('Mission', back_populates='progress_records')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'mission_id', name='uq_student_mission'),
    )

    def __repr__(self):
        return f"<StudentProgress student_id={self.student_id} mission_id={self.mission_id} completed={self.completed}>"


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='🏆', nullable=False)
    points_reward = db.Column(db.Integer, default=50, nullable=False)
    criteria_type = db.Column(db.String(50), nullable=True)  # Может быть NULL для секретных
    criteria_value = db.Column(db.Integer, nullable=True)
    is_secret = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student_achievements = db.relationship('StudentAchievement', back_populates='achievement', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Achievement {self.name}>"


class StudentAchievement(db.Model):
    __tablename__ = 'student_achievement'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', back_populates='achievements')
    achievement = db.relationship('Achievement', back_populates='student_achievements')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'achievement_id', name='uq_student_achievement'),
    )

    def __repr__(self):
        return f"<StudentAchievement student_id={self.student_id} achievement_id={self.achievement_id}>"


class Challenge(db.Model):
    __tablename__ = 'challenge'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='beginner', nullable=False)
    category = db.Column(db.String(50), default='programming', nullable=False)
    points_reward = db.Column(db.Integer, default=50, nullable=False)
    test_cases = db.Column(db.Text, nullable=True)  # JSON-строка с тестами
    solution_template = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    submissions = db.relationship('ChallengeSubmission', back_populates='challenge', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Challenge {self.title}>"


class ChallengeSubmission(db.Model):
    __tablename__ = 'challenge_submission'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    passed = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', back_populates='challenge_submissions')
    challenge = db.relationship('Challenge', back_populates='submissions')

    __table_args__ = (
        db.CheckConstraint('score >= 0 AND score <= 100', name='ck_score_range'),
    )

    def __repr__(self):
        return f"<ChallengeSubmission student_id={self.student_id} challenge_id={self.challenge_id} passed={self.passed}>"

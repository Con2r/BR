from flask import Blueprint, request, jsonify
from models import db, Student, StudentProgress, Group
from datetime import datetime, timedelta

leaderboards_bp = Blueprint('leaderboards', __name__)

class LeaderboardSystem:
    def get_group_leaderboard(self, group_id=None, period_days=7):
        """Получение лидерборда по группам"""
        # Базовый запрос
        query = db.session.query(
            Student.id,
            Student.first_name,
            Student.last_name,
            Group.name.label('group_name'),
            db.func.count(StudentProgress.id).label('completed_count')
        ).join(
            StudentProgress, Student.id == StudentProgress.student_id
        ).join(
            Group, Student.group_id == Group.id
        ).filter(
            StudentProgress.completed == True
        )
        
        # Фильтр по периоду
        if period_days:
            start_date = datetime.utcnow() - timedelta(days=period_days)
            query = query.filter(StudentProgress.completed_at >= start_date)
        
        # Фильтр по группе
        if group_id:
            query = query.filter(Student.group_id == group_id)
        
        results = query.group_by(
            Student.id, Student.first_name, Student.last_name, Group.name
        ).order_by(
            db.desc('completed_count')
        ).limit(20).all()
        
        leaderboard = []
        for i, (student_id, first_name, last_name, group_name, completed_count) in enumerate(results, 1):
            leaderboard.append({
                'rank': i,
                'student_id': student_id,
                'name': f"{first_name} {last_name}",
                'group': group_name,
                'completed_levels': completed_count,
                'badge': self.get_rank_badge(i)
            })
        
        return leaderboard
    
    def get_rank_badge(self, rank):
        """Получение бейджа для ранга"""
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        elif rank <= 10:
            return "⭐"
        else:
            return "🔹"
    
    def get_student_stats(self, student_id):
        """Получение статистики ученика"""
        student = Student.query.get(student_id)
        if not student:
            return None
        
        total_completed = StudentProgress.query.filter_by(
            student_id=student_id,
            completed=True
        ).count()
        
        # Позиция в лидерборде
        all_students = db.session.query(
            Student.id,
            db.func.count(StudentProgress.id).label('completed_count')
        ).join(
            StudentProgress, Student.id == StudentProgress.student_id
        ).filter(
            StudentProgress.completed == True
        ).group_by(Student.id).all()
        
        student_completed = total_completed
        better_students = sum(1 for _, completed in all_students if completed > student_completed)
        rank = better_students + 1 if student_completed > 0 else None
        
        return {
            'student_id': student_id,
            'name': f"{student.first_name} {student.last_name}",
            'total_completed': total_completed,
            'rank': rank,
            'group': student.group.name,
            'progress_percentage': min(100, (total_completed / 5) * 100)  # 5 - максимальное количество уровней
        }

@leaderboards_bp.route('/leaderboard/group/<int:group_id>')
def get_group_leaderboard(group_id):
    period = request.args.get('period', 30, type=int)
    
    system = LeaderboardSystem()
    leaderboard = system.get_group_leaderboard(group_id, period)
    
    return jsonify({
        'group_id': group_id,
        'period_days': period,
        'leaderboard': leaderboard
    })

@leaderboards_bp.route('/leaderboard/global')
def get_global_leaderboard():
    period = request.args.get('period', 30, type=int)
    
    system = LeaderboardSystem()
    leaderboard = system.get_group_leaderboard(None, period)
    
    return jsonify({
        'period_days': period,
        'leaderboard': leaderboard
    })

@leaderboards_bp.route('/leaderboard/student/<int:student_id>')
def get_student_stats(student_id):
    system = LeaderboardSystem()
    stats = system.get_student_stats(student_id)
    
    if stats:
        return jsonify(stats)
    else:
        return jsonify({'error': 'Student not found'}), 404
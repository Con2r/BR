from flask import Blueprint, request, jsonify
from models import db, User, Student, MentorRelationship
from datetime import datetime

mentorship_bp = Blueprint('mentorship', __name__)

class MentorshipSystem:
    def assign_mentor(self, student_id, mentor_skill_level=2):
        """Автоматически назначает ментора ученику"""
        # Находим подходящих менторов (учеников с высоким уровнем)
        potential_mentors = Student.query.join(User).filter(
            User.is_admin == False
        ).all()
        
        # Сортируем по прогрессу (количество завершенных уровней)
        mentor_scores = []
        for mentor in potential_mentors:
            if mentor.id == student_id:
                continue  # Пропускаем самого себя
                
            completed_levels = len([p for p in mentor.progress if p.completed])
            if completed_levels >= mentor_skill_level:
                mentor_scores.append((mentor, completed_levels))
        
        # Сортируем по убыванию прогресса
        mentor_scores.sort(key=lambda x: x[1], reverse=True)
        
        if mentor_scores:
            mentor, _ = mentor_scores[0]
            
            # Проверяем, нет ли уже активных отношений
            existing = MentorRelationship.query.filter_by(
                student_id=student_id,
                is_active=True
            ).first()
            
            if not existing:
                relationship = MentorRelationship(
                    mentor_id=mentor.id,
                    student_id=student_id,
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(relationship)
                db.session.commit()
                return mentor
        
        return None
    
    def get_mentor_advice(self, mentor_id, question):
        """Получение совета от ментора"""
        # В реальной системе здесь была бы интеграция с чатом
        advice_responses = [
            "Попробуй разбить задачу на меньшие части и решать их по очереди!",
            "Обрати внимание на базовые принципы - они помогут найти решение.",
            "Не бойся экспериментировать с разными подходами.",
            "Почитай документацию по этой теме, там много полезных примеров.",
            "Попробуй объяснить проблему вслух - это часто помогает найти решение.",
            "Сделай перерыв и вернись к задаче со свежей головой."
        ]
        
        import random
        return random.choice(advice_responses)

@mentorship_bp.route('/mentor/request', methods=['POST'])
def request_mentor():
    data = request.json
    student_id = data.get('student_id')
    
    system = MentorshipSystem()
    mentor = system.assign_mentor(student_id)
    
    if mentor:
        return jsonify({
            'success': True,
            'mentor': {
                'id': mentor.id,
                'name': f"{mentor.first_name} {mentor.last_name}",
                'email': mentor.email
            },
            'message': f'Вам назначен ментор: {mentor.first_name} {mentor.last_name}'
        })
    else:
        return jsonify({
            'success': False, 
            'message': 'В данный момент нет доступных менторов. Попробуйте позже.'
        })

@mentorship_bp.route('/mentor/<int:mentor_id>/advice', methods=['POST'])
def get_advice(mentor_id):
    question = request.json.get('question', '')
    
    system = MentorshipSystem()
    advice = system.get_mentor_advice(mentor_id, question)
    
    return jsonify({'advice': advice})

@mentorship_bp.route('/mentor/relationships/<int:student_id>')
def get_mentor_relationships(student_id):
    relationships = MentorRelationship.query.filter_by(
        student_id=student_id,
        is_active=True
    ).all()
    
    mentors = []
    for rel in relationships:
        mentor = Student.query.get(rel.mentor_id)
        if mentor:
            mentors.append({
                'id': mentor.id,
                'name': f"{mentor.first_name} {mentor.last_name}",
                'email': mentor.email
            })
    
    return jsonify({'mentors': mentors})
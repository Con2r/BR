from flask import Blueprint, request, jsonify
from models import db, MoodRecord
from datetime import datetime, timedelta
import json

mood_bp = Blueprint('mood', __name__)

class MoodTracker:
    def record_mood(self, student_id, mood_value, notes=""):
        """Записывает настроение ученика"""
        if not 1 <= mood_value <= 5:
            return None
            
        record = MoodRecord(
            student_id=student_id,
            mood_value=mood_value,
            notes=notes,
            recorded_at=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        return record
    
    def get_mood_analytics(self, student_id, days=7):
        """Аналитика настроения за период"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        records = MoodRecord.query.filter(
            MoodRecord.student_id == student_id,
            MoodRecord.recorded_at >= start_date
        ).order_by(MoodRecord.recorded_at).all()
        
        if not records:
            return None
        
        # Статистика
        avg_mood = sum(r.mood_value for r in records) / len(records)
        mood_trend = self.calculate_trend(records)
        
        # Распределение по дням
        daily_mood = {}
        for record in records:
            date_str = record.recorded_at.strftime('%Y-%m-%d')
            if date_str not in daily_mood:
                daily_mood[date_str] = []
            daily_mood[date_str].append(record.mood_value)
        
        # Усредняем по дням
        daily_avg = {date: sum(moods)/len(moods) for date, moods in daily_mood.items()}
        
        return {
            'average_mood': round(avg_mood, 2),
            'trend': mood_trend,
            'total_records': len(records),
            'daily_averages': daily_avg,
            'records': [
                {
                    'date': r.recorded_at.strftime('%Y-%m-%d %H:%M'),
                    'mood': r.mood_value,
                    'notes': r.notes,
                    'mood_emoji': ['😢', '😕', '😐', '😊', '🤩'][r.mood_value - 1]
                } for r in records
            ]
        }
    
    def calculate_trend(self, records):
        """Вычисляет тренд настроения"""
        if len(records) < 2:
            return 'stable'
        
        first_half = records[:len(records)//2]
        second_half = records[len(records)//2:]
        
        avg_first = sum(r.mood_value for r in first_half) / len(first_half)
        avg_second = sum(r.mood_value for r in second_half) / len(second_half)
        
        if avg_second > avg_first + 0.3:
            return 'improving'
        elif avg_second < avg_first - 0.3:
            return 'declining'
        else:
            return 'stable'

@mood_bp.route('/mood/record', methods=['POST'])
def record_mood():
    data = request.json
    student_id = data.get('student_id')
    mood_value = data.get('mood_value')
    notes = data.get('notes', '')
    
    if not student_id or not mood_value:
        return jsonify({'error': 'Missing student_id or mood_value'}), 400
    
    tracker = MoodTracker()
    record = tracker.record_mood(student_id, mood_value, notes)
    
    if record:
        return jsonify({
            'success': True,
            'record_id': record.id,
            'message': 'Настроение записано! 🎉'
        })
    else:
        return jsonify({'error': 'Invalid mood value'}), 400

@mood_bp.route('/mood/analytics/<int:student_id>')
def get_mood_analytics(student_id):
    days = request.args.get('days', 7, type=int)
    
    tracker = MoodTracker()
    analytics = tracker.get_mood_analytics(student_id, days)
    
    if analytics:
        return jsonify(analytics)
    else:
        return jsonify({'message': 'No mood data available for this period'})

@mood_bp.route('/mood/recommendations/<int:student_id>')
def get_mood_recommendations(student_id):
    """Получение рекомендаций на основе настроения"""
    tracker = MoodTracker()
    analytics = tracker.get_mood_analytics(student_id, 7)
    
    if not analytics:
        return jsonify({'recommendations': ['Начните записывать свое настроение для получения персонализированных рекомендаций!']})
    
    avg_mood = analytics['average_mood']
    
    recommendations = []
    
    if avg_mood <= 2:
        recommendations = [
            "Похоже, вам сложно. Попробуйте сделать перерыв и заняться чем-то приятным.",
            "Разбейте большую задачу на маленькие шаги - это сделает ее менее пугающей.",
            "Не стесняйтесь обратиться за помощью к ментору или преподавателю."
        ]
    elif avg_mood <= 3:
        recommendations = [
            "Попробуйте новый подход к решению задачи - иногда смена перспективы помогает.",
            "Вспомните свои прошлые успехи - вы справлялись с трудностями раньше!",
            "Сделайте короткую паузу и вернитесь к задаче со свежими силами."
        ]
    else:
        recommendations = [
            "Отличное настроение! Это прекрасное время для изучения новых сложных тем.",
            "Попробуйте помочь другим ученикам - это укрепит ваши собственные знания.",
            "Не забывайте делать перерывы, даже когда все идет хорошо."
        ]
    
    return jsonify({
        'average_mood': avg_mood,
        'recommendations': recommendations
    })
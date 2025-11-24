from flask import Blueprint, request, jsonify, send_file
import os
from datetime import datetime
import uuid

voice_bp = Blueprint('voice', __name__)

class VoiceNoteSystem:
    def __init__(self):
        self.upload_folder = 'static/audio/'
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def save_audio_note(self, audio_file, student_id, brainrot_id=None):
        """Сохраняет аудио файл"""
        if not audio_file:
            return {'error': 'No audio file provided'}
        
        filename = f"{uuid.uuid4()}_{audio_file.filename}"
        filepath = os.path.join(self.upload_folder, filename)
        
        try:
            audio_file.save(filepath)
            
            # В реальном приложении здесь было бы преобразование речи в текст
            # Для демо просто возвращаем информацию о файле
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'message': 'Аудио заметка сохранена успешно',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'error': f'Ошибка при сохранении файла: {str(e)}'}

@voice_bp.route('/voice/upload', methods=['POST'])
def upload_voice_note():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    student_id = request.form.get('student_id')
    brainrot_id = request.form.get('brainrot_id')
    
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    system = VoiceNoteSystem()
    result = system.save_audio_note(audio_file, student_id, brainrot_id)
    
    return jsonify(result)

@voice_bp.route('/voice/notes/<int:student_id>')
def get_voice_notes(student_id):
    # Здесь должна быть логика получения списка голосовых заметок ученика
    # Для демо возвращаем заглушку
    return jsonify({
        'notes': [
            {
                'id': 1,
                'filename': 'note1.wav',
                'created_at': '2024-01-15T10:30:00',
                'brainrot_title': 'Основы алгоритмов'
            }
        ]
    })
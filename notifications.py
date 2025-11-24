from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__)

class NotificationSystem:
    def __init__(self):
        self.notifications = {}
    
    def add_notification(self, user_id, title, message, notification_type="info"):
        """Добавление уведомления"""
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        notification = {
            'id': len(self.notifications[user_id]) + 1,
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat(),
            'read': False
        }
        
        self.notifications[user_id].insert(0, notification)  # Добавляем в начало
        return notification
    
    def get_notifications(self, user_id, limit=10):
        """Получение уведомлений пользователя"""
        if user_id not in self.notifications:
            return []
        
        # Ограничиваем количество и возвращаем непрочитанные сначала
        notifications = self.notifications[user_id]
        unread = [n for n in notifications if not n['read']]
        read = [n for n in notifications if n['read']]
        
        return (unread + read)[:limit]
    
    def mark_as_read(self, user_id, notification_id):
        """Пометить уведомление как прочитанное"""
        if user_id in self.notifications:
            for notification in self.notifications[user_id]:
                if notification['id'] == notification_id:
                    notification['read'] = True
                    return True
        return False
    
    def mark_all_as_read(self, user_id):
        """Пометить все уведомления как прочитанные"""
        if user_id in self.notifications:
            for notification in self.notifications[user_id]:
                notification['read'] = True
            return True
        return False

# Глобальный экземпляр системы уведомлений
notification_system = NotificationSystem()

@notifications_bp.route('/notifications/<int:user_id>')
def get_user_notifications(user_id):
    limit = request.args.get('limit', 10, type=int)
    
    notifications = notification_system.get_notifications(user_id, limit)
    unread_count = sum(1 for n in notifications if not n['read'])
    
    return jsonify({
        'notifications': notifications,
        'unread_count': unread_count
    })

@notifications_bp.route('/notifications/<int:user_id>/read/<int:notification_id>', methods=['POST'])
def mark_notification_read(user_id, notification_id):
    success = notification_system.mark_as_read(user_id, notification_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Notification not found'}), 404

@notifications_bp.route('/notifications/<int:user_id>/read-all', methods=['POST'])
def mark_all_notifications_read(user_id):
    success = notification_system.mark_all_as_read(user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'All notifications marked as read'})
    else:
        return jsonify({'error': 'No notifications found'}), 404

@notifications_bp.route('/notifications/<int:user_id>/add', methods=['POST'])
def add_notification(user_id):
    data = request.json
    title = data.get('title', '')
    message = data.get('message', '')
    notification_type = data.get('type', 'info')
    
    notification = notification_system.add_notification(user_id, title, message, notification_type)
    
    return jsonify({
        'success': True,
        'notification': notification
    })
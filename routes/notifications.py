# Notification Routes
from flask import Blueprint, request, jsonify
from models.database import get_db_connection
from routes.auth import get_user_from_token

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications', methods=['GET'])
def get_notifications():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 50
        """, (user['user_id'],))
        
        notifications = cursor.fetchall()
        
        cursor.execute("""
            SELECT COUNT(*) as unread_count 
            FROM notifications 
            WHERE user_id = ? AND read_status = 0
        """, (user['user_id'],))
        unread_count = cursor.fetchone()[0]
        
        result = []
        for notif in notifications:
            notif_dict = dict(notif)
            notif_dict['created_at'] = str(notif_dict['created_at'])
            result.append(notif_dict)
        
        return jsonify({
            'notifications': result,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@notifications_bp.route('/notifications', methods=['POST'])
def create_notification():
    data = request.get_json()
    target_user_id = data.get('user_id')
    message = data.get('message')
    notif_type = data.get('type', 'general')
    
    if not all([target_user_id, message]):
        return jsonify({'error': 'user_id and message required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (user_id, type, message)
            VALUES (?, ?, ?)
        """, (target_user_id, notif_type, message))
        
        connection.commit()
        
        return jsonify({'message': 'Notification created'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

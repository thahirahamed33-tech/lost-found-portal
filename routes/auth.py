# Authentication Routes
from flask import Blueprint, request, jsonify
from models.database import get_db_connection
import jwt
import bcrypt

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = "campus_lost_found_secret_key_2026"

def get_user_from_token(token):
    """Decode token and return user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (name, email, phone, password)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, hashed_password.decode('utf-8')))
        
        connection.commit()
        user_id = cursor.lastrowid
        
        # Generate token
        token = jwt.encode({'user_id': user_id, 'email': email, 'role': 'user'}, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {'id': user_id, 'name': name, 'email': email, 'role': 'user'}
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                token = jwt.encode({
                    'user_id': user['id'],
                    'email': user['email'],
                    'role': user['role']
                }, SECRET_KEY, algorithm='HS256')
                
                return jsonify({
                    'message': 'Login successful',
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'phone': user['phone'],
                        'role': user['role']
                    }
                }), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        except:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@auth_bp.route('/notifications', methods=['GET'])
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
            LIMIT 20
        """, (user['user_id'],))
        
        notifications = cursor.fetchall()
        
        # Get unread count
        cursor.execute("""
            SELECT COUNT(*) as count FROM notifications
            WHERE user_id = ? AND read_status = 0
        """, (user['user_id'],))
        unread_count = cursor.fetchone()[0]
        
        result = []
        for notif in notifications:
            notif_dict = dict(notif)
            if notif_dict.get('created_at'):
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

@auth_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
def mark_notification_read(notif_id):
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
            UPDATE notifications
            SET read_status = 1
            WHERE id = ? AND user_id = ?
        """, (notif_id, user['user_id']))
        
        connection.commit()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@auth_bp.route('/notifications/read-all', methods=['PUT'])
def mark_all_notifications_read():
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
            UPDATE notifications
            SET read_status = 1
            WHERE user_id = ?
        """, (user['user_id'],))
        
        connection.commit()
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

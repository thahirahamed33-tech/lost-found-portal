# API Routes for CampusLost (SQLite)
from flask import Flask, request, jsonify
from models import get_db_connection
import jwt
import bcrypt

SECRET_KEY = "campus_lost_found_secret_key_2026"

# ==================== AUTH ROUTES ====================

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

# ==================== HELPER FUNCTIONS ====================

def get_user_from_token(token):
    """Decode token and return user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

# ==================== ITEMS ROUTES ====================

def get_items():
    item_type = request.args.get('type')
    category = request.args.get('category')
    search = request.args.get('search')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        query = """
            SELECT i.*, u.name as user_name, u.email as user_email
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if item_type:
            query += " AND i.type = ?"
            params.append(item_type)
        
        if category:
            query += " AND i.category = ?"
            params.append(category)
        
        if search:
            query += " AND (i.name LIKE ? OR i.description LIKE ? OR i.location LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY i.created_at DESC"
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        # Convert to dict
        result = []
        for item in items:
            item_dict = dict(item)
            if item_dict.get('date'):
                item_dict['date'] = str(item_dict['date'])
            if item_dict.get('created_at'):
                item_dict['created_at'] = str(item_dict['created_at'])
            result.append(item_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def get_item(item_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT i.*, u.name as user_name, u.email as user_email, u.phone as user_phone
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.id = ?
        """, (item_id,))
        
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        item_dict = dict(item)
        if item_dict.get('date'):
            item_dict['date'] = str(item_dict['date'])
        if item_dict.get('created_at'):
            item_dict['created_at'] = str(item_dict['created_at'])
        
        return jsonify(item_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def create_item():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    
    item_type = data.get('type')
    name = data.get('name')
    category = data.get('category')
    description = data.get('description')
    location = data.get('location')
    date = data.get('date')
    image = data.get('image')
    
    if not all([item_type, name, category, description, location, date]):
        return jsonify({'error': 'All fields are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO items (type, name, category, description, location, date, image, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_type, name, category, description, location, date, image, user['user_id']))
        
        connection.commit()
        item_id = cursor.lastrowid
        
        return jsonify({
            'message': 'Item created successfully',
            'item_id': item_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def update_item(item_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    status = data.get('status')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if user owns the item or is admin
        cursor.execute("SELECT user_id FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item[0] != user['user_id'] and user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        cursor.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
        connection.commit()
        
        return jsonify({'message': 'Item updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def delete_item(item_id):
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
        
        cursor.execute("SELECT user_id FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item[0] != user['user_id'] and user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        connection.commit()
        
        return jsonify({'message': 'Item deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ==================== USER ITEMS ROUTES ====================

def get_my_items():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    item_type = request.args.get('type')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT * FROM items WHERE user_id = ?"
        params = [user['user_id']]
        
        if item_type:
            query += " AND type = ?"
            params.append(item_type)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        result = []
        for item in items:
            item_dict = dict(item)
            if item_dict.get('date'):
                item_dict['date'] = str(item_dict['date'])
            if item_dict.get('created_at'):
                item_dict['created_at'] = str(item_dict['created_at'])
            result.append(item_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ==================== CLAIMS ROUTES ====================

def create_claim():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    
    item_id = data.get('item_id')
    proof = data.get('proof')
    contact = data.get('contact')
    
    if not all([item_id, proof]):
        return jsonify({'error': 'Item ID and proof are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if item exists
        cursor.execute("SELECT id, status FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item[1] in ['claimed', 'resolved']:
            return jsonify({'error': 'Item already claimed or resolved'}), 400
        
        # Check if user already claimed
        cursor.execute("SELECT id FROM claims WHERE item_id = ? AND user_id = ?", (item_id, user['user_id']))
        if cursor.fetchone():
            return jsonify({'error': 'You have already claimed this item'}), 400
        
        # Create claim
        cursor.execute("""
            INSERT INTO claims (item_id, user_id, proof, contact)
            VALUES (?, ?, ?, ?)
        """, (item_id, user['user_id'], proof, contact))
        
        # Update item status
        cursor.execute("UPDATE items SET status = 'claimed' WHERE id = ?", (item_id,))
        
        connection.commit()
        
        return jsonify({'message': 'Claim submitted successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def get_my_claims():
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
            SELECT c.*, i.name as item_name, i.type as item_type
            FROM claims c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        """, (user['user_id'],))
        
        claims = cursor.fetchall()
        
        result = []
        for claim in claims:
            claim_dict = dict(claim)
            if claim_dict.get('created_at'):
                claim_dict['created_at'] = str(claim_dict['created_at'])
            result.append(claim_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ==================== ADMIN ROUTES ====================

def get_all_claims():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT c.*, i.name as item_name, u.name as claimant_name, u.email as claimant_email
            FROM claims c
            JOIN items i ON c.item_id = i.id
            JOIN users u ON c.user_id = u.id
            ORDER BY c.created_at DESC
        """)
        
        claims = cursor.fetchall()
        
        result = []
        for claim in claims:
            claim_dict = dict(claim)
            if claim_dict.get('created_at'):
                claim_dict['created_at'] = str(claim_dict['created_at'])
            result.append(claim_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def update_claim(claim_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    status = data.get('status')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("UPDATE claims SET status = ? WHERE id = ?", (status, claim_id))
        
        if status == 'approved':
            cursor.execute("SELECT item_id FROM claims WHERE id = ?", (claim_id,))
            claim = cursor.fetchone()
            if claim:
                cursor.execute("UPDATE items SET status = 'resolved' WHERE id = ?", (claim[0],))
        
        connection.commit()
        
        return jsonify({'message': 'Claim updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def get_stats():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()[0]
        
        # Lost items
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE type = 'lost'")
        lost_items = cursor.fetchone()[0]
        
        # Found items
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE type = 'found'")
        found_items = cursor.fetchone()[0]
        
        # Pending claims
        cursor.execute("SELECT COUNT(*) as count FROM claims WHERE status = 'pending'")
        pending_claims = cursor.fetchone()[0]
        
        # Resolved
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE status IN ('resolved', 'claimed')")
        resolved = cursor.fetchone()[0]
        
        return jsonify({
            'total_users': total_users,
            'lost_items': lost_items,
            'found_items': found_items,
            'pending_claims': pending_claims,
            'resolved': resolved
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ==================== NOTIFICATIONS ROUTES ====================

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

def health_check():
    return jsonify({'status': 'ok', 'message': 'CampusLost API is running'}), 200

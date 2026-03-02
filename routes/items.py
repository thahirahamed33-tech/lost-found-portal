# Items Routes
from flask import Blueprint, request, jsonify
from models.database import get_db_connection
from routes.auth import get_user_from_token

items_bp = Blueprint('items', __name__)

@items_bp.route('/items', methods=['GET'])
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

@items_bp.route('/items/<int:item_id>', methods=['GET'])
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

@items_bp.route('/items', methods=['POST'])
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
    item_date = data.get('date')
    image = data.get('image')
    
    if not all([item_type, name, category, description, location, item_date]):
        return jsonify({'error': 'All fields are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO items (type, name, category, description, location, date, image, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_type, name, category, description, location, item_date, image, user['user_id']))
        
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

@items_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization required'}), 401
    
    user = get_user_from_token(token.replace('Bearer ', ''))
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    status = data.get('status')
    item_type = data.get('type')  # Allow changing type (lost -> found)
    
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
        
        # Build update query
        update_fields = []
        params = []
        
        if status:
            update_fields.append("status = ?")
            params.append(status)
        
        if item_type:
            update_fields.append("type = ?")
            params.append(item_type)
        
        if update_fields:
            params.append(item_id)
            query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            connection.commit()
        
        return jsonify({'message': 'Item updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@items_bp.route('/items/<int:item_id>/convert', methods=['POST'])
def convert_item_to_found(item_id):
    """Convert a lost item to found status"""
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
        
        # Check if user owns the item or is admin
        cursor.execute("SELECT user_id, type FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item[0] != user['user_id'] and user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Convert lost to found
        cursor.execute("UPDATE items SET type = 'found', status = 'resolved' WHERE id = ?", (item_id,))
        connection.commit()
        
        return jsonify({'message': 'Item converted to found successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@items_bp.route('/items/<int:item_id>', methods=['DELETE'])
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

@items_bp.route('/my-items', methods=['GET'])
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

# Claims Routes
@items_bp.route('/claims', methods=['POST'])
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

@items_bp.route('/my-claims', methods=['GET'])
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

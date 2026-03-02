# Admin Routes
from flask import Blueprint, request, jsonify
from models.database import get_db_connection
from routes.auth import get_user_from_token

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
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

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
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
            SELECT id, name, email, phone, role, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        result = []
        for u in users:
            user_dict = dict(u)
            if user_dict.get('created_at'):
                user_dict['created_at'] = str(user_dict['created_at'])
            result.append(user_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@admin_bp.route('/claims', methods=['GET'])
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

@admin_bp.route('/claims/<int:claim_id>', methods=['PUT'])
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

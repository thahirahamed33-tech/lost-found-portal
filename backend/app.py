 # CampusLost - Flask Application Entry Point
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from models import init_database
from routes import (
    register, login, get_items, get_item, create_item, update_item, delete_item,
    get_my_items, create_claim, get_my_claims, get_all_claims, update_claim,
    get_stats, get_notifications, mark_notification_read, mark_all_notifications_read,
    health_check
)

app = Flask(__name__)
CORS(app)

# Register routes
app.add_url_rule('/api/register', 'register', register, methods=['POST'])
app.add_url_rule('/api/login', 'login', login, methods=['POST'])
app.add_url_rule('/api/items', 'get_items', get_items, methods=['GET'])
app.add_url_rule('/api/items', 'create_item', create_item, methods=['POST'])
app.add_url_rule('/api/items/<int:item_id>', 'get_item', get_item, methods=['GET'])
app.add_url_rule('/api/items/<int:item_id>', 'update_item', update_item, methods=['PUT'])
app.add_url_rule('/api/items/<int:item_id>', 'delete_item', delete_item, methods=['DELETE'])
app.add_url_rule('/api/my-items', 'get_my_items', get_my_items, methods=['GET'])
app.add_url_rule('/api/claims', 'create_claim', create_claim, methods=['POST'])
app.add_url_rule('/api/my-claims', 'get_my_claims', get_my_claims, methods=['GET'])
app.add_url_rule('/api/admin/claims', 'get_all_claims', get_all_claims, methods=['GET'])
app.add_url_rule('/api/admin/claims/<int:claim_id>', 'update_claim', update_claim, methods=['PUT'])
app.add_url_rule('/api/admin/stats', 'get_stats', get_stats, methods=['GET'])
app.add_url_rule('/api/notifications', 'get_notifications', get_notifications, methods=['GET'])
app.add_url_rule('/api/notifications/<int:notif_id>/read', 'mark_notification_read', mark_notification_read, methods=['PUT'])
app.add_url_rule('/api/notifications/read-all', 'mark_all_notifications_read', mark_all_notifications_read, methods=['PUT'])
app.add_url_rule('/api/health', 'health_check', health_check, methods=['GET'])

# Serve frontend - SPA catch-all for all non-API routes
@app.route('/')
@app.route('/lost')
@app.route('/found')
@app.route('/myitems')
@app.route('/report')
@app.route('/dashboard')
@app.route('/admin')
def index():
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database (creates tables if they don't exist)
    print("Initializing database...")
    init_database()
    
    # Run the Flask app
    print("Starting CampusLost API server...")
    print("API available at: http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)

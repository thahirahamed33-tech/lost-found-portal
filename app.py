# CampusLost - Flask Application Entry Point
import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from models.database import init_database
from routes.auth import auth_bp
from routes.items import items_bp
from routes.admin import admin_bp
from routes.notifications import notifications_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'campus_lost_found_secret_key_2026')
CORS(app)

# Register Blueprints
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'campus_lost_found_secret_key_2026')
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(items_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(notifications_bp, url_prefix='/api')

# Main routes
@app.route('/')
def index():
    return render_template('index.html', page='home')

@app.route('/lost')
def lost():
    return render_template('index.html', page='lost')

@app.route('/found')
def found():
    return render_template('index.html', page='found')

@app.route('/myitems')
def myitems():
    return render_template('index.html', page='myitems')

@app.route('/report')
def report():
    return render_template('index.html', page='report')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html', page='dashboard')

@app.route('/admin')
def admin():
    return render_template('index.html', page='admin')

@app.route('/api')
def api_index():
    return jsonify({
        'message': 'CampusLost API',
        'version': '1.0',
        'endpoints': {
            'auth': ['POST /api/register', 'POST /api/login', 'GET /api/notifications'],
            'items': ['GET /api/items', 'POST /api/items', 'GET /api/my-items', 'POST /api/claims'],
            'admin': ['GET /api/admin/stats', 'GET /api/admin/claims']
        }
    }), 200

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'message': 'CampusLost API is running'}), 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    print("Initializing database...")
    init_database()
    
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    print(f"Starting CampusLost API server on port {port}...")
    app.run(host='0.0.0.0', port=port)

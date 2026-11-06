from flask import jsonify, render_template

from app.main import main_bp  # use the package blueprint; a second Blueprint here left every route unregistered (all 404)

@main_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/chat')
def chat():
    return render_template('ui-components.html')

@main_bp.route('/assistants')
def assistants():
    return render_template('industry-standard-components.html')

from flask import Blueprint, jsonify


main_bp = Blueprint('main', __name__)

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

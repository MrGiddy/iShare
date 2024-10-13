from flask import Blueprint

base_bp = Blueprint('base_bp', __name__)

# Main route
@base_bp.route('/')
def home():
    return {"message": "Welcome to the Picture Sharing Web App!"}, 200

@base_bp.route('/health-check')
def health_check():
    return {"status": "Healthyyyy"}, 200

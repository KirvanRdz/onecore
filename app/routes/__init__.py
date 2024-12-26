from app.routes.authRoutes import auth_bp
from app.routes.dataRoutes import upload_bp
from app.routes.documentRoutes import document_bp
from app.routes.logRoutes import log_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api/data')
    app.register_blueprint(document_bp, url_prefix='/documents')    
    app.register_blueprint(log_bp, url_prefix='/logs')    
    
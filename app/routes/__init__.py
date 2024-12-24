from app.routes.authRoutes import auth_bp
from app.routes.uploadRoutes import upload_bp
from app.routes.documentRoutes import document_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(document_bp, url_prefix='/api/documents')    
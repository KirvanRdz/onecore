from app.routes.authRoutes import auth_bp
from app.routes.refreshTokenRoutes import refresh_bp
from app.routes.uploadRoutes import upload_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(refresh_bp, url_prefix='/api/refresh')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')

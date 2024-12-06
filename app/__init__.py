from flask import Flask
from app.extensions import db, jwt, migrate
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Registrar blueprints
    register_blueprints(app)

    return app
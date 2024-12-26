from app.extensions import db

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(255), nullable=False)
    Edad = db.Column(db.Integer, nullable=False)
    Fecha_nacimiento = db.Column(db.Date, nullable=False)

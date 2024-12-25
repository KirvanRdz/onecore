from app.extensions import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    classification = db.Column(db.String(50), nullable=False)
    extracted_data = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f"<Document {self.filename}: {self.classification}>"

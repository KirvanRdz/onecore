from app.models.api.dataModel import Data
from app.extensions import db

def save_data(df):
    try:
        for _, row in df.iterrows():
            data_entry = Data(
                Nombre=row['Nombre'],
                Edad=row['Edad'],
                Fecha_nacimiento=row['Fecha_nacimiento']
            )
            db.session.add(data_entry)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        raise e

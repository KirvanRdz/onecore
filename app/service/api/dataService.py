from app.models.api.dataModel import Data
from app.extensions import db

def save_data(df):
    """
    Guarda los datos de un DataFrame en la base de datos.

    Parámetros:
    - df (pandas.DataFrame): DataFrame que contiene los datos a guardar. 
      Debe incluir las columnas 'Nombre', 'Edad' y 'Fecha_nacimiento'.

    Retorna:
    - bool: Devuelve `True` si los datos se guardaron correctamente.
    """
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

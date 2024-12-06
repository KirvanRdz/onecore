import pandas as pd

def validate_csv(df):
    errors = []
    required_columns = ['Nombre', 'Edad', 'Fecha_nacimiento']

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        errors.append(f"Faltan columnas obligatorias: {', '.join(missing_columns)}")
    
    if df.empty:
        errors.append("El archivo CSV está vacío")
    
    if df.isnull().values.any():
        errors.append("El archivo contiene valores vacíos")
    
    if df.duplicated().any():
        errors.append("El archivo contiene filas duplicadas")
    
    try:
        df['Nombre'] = df['Nombre'].astype(str)
        df['Edad'] = df['Edad'].astype(int)
        df['Fecha_nacimiento'] = pd.to_datetime(df['Fecha_nacimiento'])
    except Exception as e:
        errors.append(f"Error en tipos de datos: {str(e)}")
    
    return errors

import pandas as pd

def validate_csv(df):
    """
    Valida un DataFrame cargado desde un archivo CSV para garantizar que cumpla con los requisitos establecidos.

    Parámetros:
    - df (pandas.DataFrame): El DataFrame que contiene los datos del archivo CSV a validar.

    Retorna:
    - list: Una lista de errores encontrados durante la validación. Si no se encuentran errores, la lista estará vacía.
    """
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

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """
    Verifica si el archivo tiene una extensión permitida.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
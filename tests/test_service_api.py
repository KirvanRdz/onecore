import pytest
from app import create_app  # Asegúrate de importar tu función de creación de la app
from app.service.api.authService import create_tokens 
from unittest import mock
import pandas as pd
from app.service.api.dataService import save_data  # Asegúrate de importar la función correctamente
from app.extensions import db

@pytest.fixture
def app():
    # Crea una instancia de la aplicación Flask para las pruebas
    app = create_app()  # Asegúrate de tener una función create_app() en tu aplicación
    yield app

@pytest.fixture
def client(app):
    # Configura el cliente de prueba
    with app.test_client() as client:
        yield client

def test_create_tokens(app):
    with app.app_context():
        username = "testuser"
        user_data = {"id_usuario": 1, "rol": "admin"}
        access_token, refresh_token = create_tokens(username, user_data)
        
        # Asegúrate de que los tokens se generen correctamente
        assert access_token is not None
        assert refresh_token is not None

# Fixture para crear un DataFrame de prueba
@pytest.fixture
def mock_dataframe():
    data = {
        'Nombre': ['Juan', 'Maria'],
        'Edad': [25, 30],
        'Fecha_nacimiento': ['1999-01-01', '1994-05-12']
    }
    return pd.DataFrame(data)

# Prueba unitaria para save_data sin interactuar con la base de datos real
def test_save_data(mock_dataframe):
    # Mock de db.session.add y db.session.commit para evitar interacciones reales con la base de datos
    with mock.patch.object(db.session, 'add') as mock_add, \
         mock.patch.object(db.session, 'commit') as mock_commit, \
         mock.patch.object(db.session, 'rollback') as mock_rollback:

        # Llamar a la función que estamos probando
        result = save_data(mock_dataframe)

        # Verificar que db.session.add fue llamado correctamente para cada fila del DataFrame
        assert mock_add.call_count == len(mock_dataframe)  # Debe ser llamado por cada fila

        # Verificar que db.session.commit fue llamado una vez
        mock_commit.assert_called_once()

        # Asegurarse de que la función devuelve True cuando no hay errores
        assert result is True

        # Verificar que rollback no se llama si todo sale bien
        mock_rollback.assert_not_called()

# Prueba para el caso de error (cuando ocurre una excepción)
def test_save_data_with_error(mock_dataframe):
    # Mock de db.session.add y db.session.commit para simular un error
    with mock.patch.object(db.session, 'add') as mock_add, \
         mock.patch.object(db.session, 'commit') as mock_commit, \
         mock.patch.object(db.session, 'rollback') as mock_rollback:

        # Simulamos un error en db.session.commit
        mock_commit.side_effect = Exception("Error al guardar en la base de datos")

        # Verificar que se lanza la excepción y que rollback se llama
        with pytest.raises(Exception):
            save_data(mock_dataframe)

        # Verificar que rollback fue llamado debido al error
        mock_rollback.assert_called_once()
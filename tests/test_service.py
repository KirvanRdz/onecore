import pytest
from unittest import mock
from io import BytesIO
from PIL import Image
from app.service.documentService import analyze_document, extract_text_from_images, document_classification
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app

# Mocks para las funciones y servicios externos
@pytest.fixture
def mock_pdf_file():
    # Crear un archivo PDF simulado
    pdf_file = mock.MagicMock()
    pdf_file.filename = "documento.pdf"
    pdf_file.read.return_value = b"contenido del pdf"
    return pdf_file


@pytest.fixture
def mock_textract_response():
    return {
        'Blocks': [
            {'BlockType': 'LINE', 'Text': 'Texto extraído del documento'}
        ]
    }

@pytest.fixture
def mock_gemini_response():
    # Simular la respuesta de Gemini
    return {
        "Tipo": "Factura",
        "Factura": {"item1": "value1", "item2": "value2"}
    }
@pytest.fixture
def mock_image_file():
    # Crear una imagen en memoria
    img = Image.new('RGB', (100, 100))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)  # Volver al principio del archivo en memoria

    # Simulamos un archivo con la propiedad 'filename'
    image_file = mock.MagicMock()
    image_file.filename = "mock_image.jpg"
    image_file.__enter__.return_value = img_byte_arr  # Usamos BytesIO en lugar de abrir un archivo real
    return image_file

# Prueba para la función analyze_document (con un archivo PDF)
def test_analyze_document_pdf(mock_pdf_file, mock_textract_response, mock_gemini_response):
    with mock.patch('app.service.documentService.extract_text_from_pdf', return_value="Texto del PDF") as mock_extract_pdf, \
         mock.patch('app.service.documentService.document_classification', return_value=mock_gemini_response), \
         mock.patch('app.service.documentService.db.session.add'), \
         mock.patch('app.service.documentService.db.session.commit'):

        classification, extracted_data = analyze_document(mock_pdf_file)

        # Verificar que la función de clasificación fue llamada
        mock_extract_pdf.assert_called_once_with(mock_pdf_file)
        assert classification == "Factura"
        assert extracted_data == mock_gemini_response["Factura"]


def test_extract_text_from_images(mock_image_file, mock_textract_response, app):
    with app.app_context():
        with mock.patch('app.service.documentService.textract_aws') as mock_textract:
            mock_textract.return_value.detect_document_text.return_value = mock_textract_response
            text = extract_text_from_images([mock_image_file])
            assert text == "Texto extraído del documento\n"

# Prueba para document_classification
def test_document_classification(mock_gemini_response, app):
    with app.app_context():
        with mock.patch('app.service.documentService.genai.GenerativeModel') as mock_model:
            mock_instance = mock.MagicMock()
            mock_instance.generate_content.return_value.text = '{"Tipo": "Factura", "Factura": {"item1": "value1"}}'
            mock_model.return_value = mock_instance

            response = document_classification("Texto de prueba")
            assert response["Tipo"] == "Factura"
            assert response["Factura"] == {"item1": "value1"}


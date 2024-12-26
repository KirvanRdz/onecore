import json
import os
from io import BytesIO
from PIL import Image
import google.generativeai as genai

from app.models.documentModel import Document
from app.utils.aws import textract_aws
from app.utils.prompts import extract_invoice_items
from app.extensions import db
from config import Config

def analyze_document(file):
    """
    Procesa el documento cargado, clasifica y extrae datos según el tipo utilizando AWS Textract y GEMINI.

    Args:
        file: Archivo cargado (PDF, JPG, PNG).

    Returns:
        Tuple (classification, extracted_data):
            - classification: "Factura" o "Información".
            - extracted_data: Datos extraídos del documento.
    """
    file_extension = os.path.splitext(file.filename)[-1].lower()
    text_content = ""


    if file_extension == '.pdf':
        text_content = extract_text_from_pdf(file)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        image = Image.open(file)
        text_content = extract_text_from_images([image])
    
    # Clasificación del documento
    extracted_data=document_classification(text_content)
    
    if extracted_data["Tipo"]== "Factura":
            classification = "Factura"
            extracted_data = extracted_data["Factura"]
    
    elif extracted_data["Tipo"]== "Informacion":
            classification = "Información"
            extracted_data = extracted_data["Informacion"]

    else:
        return None, None
    
    # Guardar en la base de datos
    document = Document(filename=file.filename, classification=classification, extracted_data=extracted_data)
    db.session.add(document)
    db.session.commit()
    return classification, extracted_data

def extract_text_from_images(images):
    """
    Extrae texto de una lista de imágenes usando AWS Textract.

    Args:
        images: Lista de objetos PIL.Image.

    Returns:
        str: Texto extraído de las imágenes.
    """
    # Inicializa el cliente de Textract
    textract = textract_aws()
    text_content = ""

    for image in images:
        # Convertir la imagen a modo RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convertir la imagen a bytes
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        # Llamar a AWS Textract
        response = textract.detect_document_text(Document={'Bytes': buffer.read()})
        
        # Extraer texto de la respuesta
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                text_content += item['Text'] + "\n"
    
    return text_content


def extract_text_from_pdf(file):
    
    """
    Extrae texto de un PDF usando AWS Textract.

    Args:
        file: Archivo PDF cargado.

    Returns:
        str: Texto extraído del PDF.
    """

    # Inicializa el cliente de Textract
    textract = textract_aws()
   
    # Lee los bytes del archivo directamente desde el objeto FileStorage
    pdf_bytes = file.read()

    # Llama a Textract para analizar el documento
    response = textract.analyze_document(
        Document={'Bytes': pdf_bytes},
        FeatureTypes=['TABLES', 'FORMS']  # incluye tablas y formularios si es necesario
    )

    # Extrae el texto del resultado
    text = ""
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':  # Cada línea de texto
            text += block['Text'] + "\n"
    
    return text

def document_classification(text):
    """
    El LLM clasifica el tipo de documento y devuelve los datos en formato JSON

    Args:
        text: Texto extraído del documento.

    Returns:
        dict: Datos extraídos del documento segun la clasificación.
    """

    genai.configure(api_key=Config.SECRET_KEY_GEMINI)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=extract_invoice_items)
    response = model.generate_content(text)
    
    data = parse_llm_response(response.text)

    return data
    

def parse_llm_response(response_text):
    """
    Convierte la salida JSON del LLM en un diccionario de Python.

    Args:
        response_text (str): La salida del LLM en formato JSON con posibles comillas triples.

    Returns:
        dict: Diccionario de Python con los datos extraídos o None si falla.
    """
    try:
        # Limpia el texto eliminando las comillas triples y la palabra "json" si está presente
        cleaned_json = response_text.strip().strip("```").strip()
        
        # Elimina la palabra "json" al inicio del texto si está presente
        if cleaned_json.lower().startswith("json"):
            cleaned_json = cleaned_json[4:].strip()

        # Verifica si el contenido está vacío después de limpiar
        if not cleaned_json:
            raise ValueError("El texto proporcionado está vacío o no contiene JSON válido.")
        
        # Intenta cargar el JSON
        data_dict = json.loads(cleaned_json)
        return data_dict
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    return None

import json
import os
from io import BytesIO
from pdf2image import convert_from_bytes
from PIL import Image
import re
import google.generativeai as genai

from app.models.documentModel import Document
from app.utils.aws import textract_aws
from app.utils.prompts import extract_invoice_items
from app.extensions import db

def analyze_document(file):
    """
    Procesa el documento cargado, clasifica y extrae datos según el tipo utilizando AWS Textract.

    Args:
        file: Archivo cargado (PDF, JPG, PNG).

    Returns:
        Tuple (classification, extracted_data):
            - classification: "Factura" o "Información".
            - extracted_data: Datos extraídos del documento.
    """
    file_extension = os.path.splitext(file.filename)[-1].lower()
    text_content = ""

    # Convertir PDF a imágenes si es necesario
    if file_extension == '.pdf':
        images = convert_from_bytes(file.read())
        text_content = extract_text_from_images(images)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        image = Image.open(file)
        text_content = extract_text_from_images([image])
    else:
        raise ValueError("Formato no soportado. Use PDF, JPG o PNG.")

    # Clasificación del documento
    if "factura" in text_content.lower() or "total" in text_content.lower():
        classification = "Factura"
        extracted_data = extract_invoice_data(text_content)
    else:
        classification = "Información"
        extracted_data = extract_information_data(text_content)

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
    textract = textract_aws()  #credenciales de AWS configuradas
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
    print(text_content)
    return text_content

def extract_invoice_data(text):
    """
    Extrae datos de una factura.

    Args:
        text: Texto extraído del documento.

    Returns:
        dict: Datos extraídos de la factura.
    """

    genai.configure(api_key="AIzaSyD-fOs_ghfTMpNnkkvzmU24d5nkTPRRios")
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=extract_invoice_items)
    response = model.generate_content(text)
    print(response.text)
    data = parse_llm_response(response.text)
    return data
    

def extract_information_data(text):
    """
    Extrae datos de un documento de información general.

    Args:
        text: Texto extraído del documento.

    Returns:
        dict: Datos extraídos de la información general.
    """
    data = {}
    data['descripcion'] = text[:200]
    data['resumen'] = "\n".join(text.splitlines()[:5])
    data['sentimiento'] = analyze_sentiment(text)
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

# Ejemplo de uso con salida JSON

def analyze_sentiment(text):
    """
    Analiza el sentimiento del texto.

    Args:
        text: Texto a analizar.

    Returns:
        str: Sentimiento (Positivo, Negativo o Neutral).
    """
    if "bueno" in text.lower() or "excelente" in text.lower():
        return "Positivo"
    elif "malo" in text.lower() or "terrible" in text.lower():
        return "Negativo"
    else:
        return "Neutral"

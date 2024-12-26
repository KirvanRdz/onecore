from flask import Blueprint, render_template, request, jsonify
from app.services.documentService import analyze_document
from app.utils.validation import allowed_file
document_bp = Blueprint('documents', __name__)

@document_bp.route('/', methods=['GET', 'POST'])
def document_analysis():
    if request.method == 'POST':
        
        file = request.files.get('file')

        if not allowed_file(file.filename):
            return render_template(
                'document_analysis.html', 
                classification=None, 
                extracted_data=None, 
                error="Tipo de archivo invalido. Solo se acepta PNG, JPG o PDF"
            )
    
        classification, extracted_data = analyze_document(file)

        if classification is None:
            return render_template(
                'document_analysis.html', 
                classification=classification, 
                extracted_data=extracted_data,
                error="No se pudo clasificar el documento"
        )

        return render_template(
            'document_analysis.html', 
            classification=classification, 
            extracted_data=extracted_data,
            error=None
        )

    return render_template('document_analysis.html', classification=None, extracted_data=None, error=None)



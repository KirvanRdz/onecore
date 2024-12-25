from flask import Blueprint, render_template, request, jsonify
from app.services.documentService import analyze_document

document_bp = Blueprint('documents', __name__)

@document_bp.route('/', methods=['GET', 'POST'])
def document_analysis():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        classification, extracted_data = analyze_document(file)

        return render_template('document_analysis.html', 
                               classification=classification, 
                               extracted_data=extracted_data)

    return render_template('document_analysis.html', classification=None, extracted_data=None)



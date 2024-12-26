# app/routes/logRoutes.py
from io import BytesIO
from flask import Blueprint, render_template, request
import pandas as pd
from flask import make_response
from app.models.logModel import Log

log_bp = Blueprint('logs', __name__)

@log_bp.route('/', methods=['GET'])
def view_logs():
    """
    Renderiza una vista con los registros de eventos filtrados según los parámetros proporcionados.

    Parámetros:
        - event_type (str, opcional): Tipo de evento a filtrar (parcial o completo).
        - description (str, opcional): Descripción del evento a filtrar (parcial o completa).
        - start_date (str, opcional): Fecha de inicio para el rango de filtrado (formato ISO-8601).
        - end_date (str, opcional): Fecha de fin para el rango de filtrado (formato ISO-8601).

    Retorna:
        - str: Una plantilla HTML renderizada que muestra los registros de eventos.
    """
    # Obtener filtros de la solicitud
    event_type = request.args.get('event_type')
    description = request.args.get('description')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Construir consulta
    query = Log.query
    if event_type:
        query = query.filter(Log.event_type.ilike(f'%{event_type}%'))
    if description:
        query = query.filter(Log.description.ilike(f'%{description}%'))
    if start_date and end_date:
        query = query.filter(Log.timestamp.between(start_date, end_date))
    
    logs = query.all()
    return render_template('log_view.html', logs=[log.to_dict() for log in logs])


@log_bp.route('/export/', methods=['GET'])
def export_logs():
    """
    Exporta los registros de eventos en formato Excel.

    Parámetros:
        - Ninguno.

    Retorna:
        - Response: Un archivo Excel generado a partir de los registros de eventos, que se descarga como un archivo adjunto con el nombre 'logs.xlsx'.
    
    """
    logs = Log.query.all()
    log_data = [log.to_dict() for log in logs]

    # Crear DataFrame y exportar a Excel
    df = pd.DataFrame(log_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Logs')

    output.seek(0)
    response = make_response(output.read())
    response.headers['Content-Disposition'] = 'attachment; filename=logs.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

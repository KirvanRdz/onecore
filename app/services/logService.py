from app.models.logModel import Log
from app.extensions import db

def log_event(event_type, description):
    """
    Registra un evento en el sistema.
    
    Args:
        event_type (str): Tipo de evento (e.g., 'Carga de documento', 'IA', 'Interacción del usuario').
        description (str): Descripción del evento.
    """
    log = Log(event_type=event_type, description=description)
    db.session.add(log)
    db.session.commit()

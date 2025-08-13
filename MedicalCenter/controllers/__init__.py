# Controllers package
from .auth_controller import auth_bp, login_required, admin_required
from .cita_controller import cita_bp
from .paciente_controller import paciente_bp
from .medico_controller import medico_bp
from .exploracion_controller import exploracion_bp
from .expediente_controller import expediente_bp
from .usuario_controller import usuario_bp

__all__ = [
    'auth_bp',
    'cita_bp',
    'paciente_bp',
    'medico_bp',
    'exploracion_bp',
    'expediente_bp',
    'usuario_bp',
    'login_required',
    'admin_required'
]
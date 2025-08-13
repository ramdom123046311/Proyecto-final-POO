
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from controllers import (
    auth_bp, cita_bp, paciente_bp, medico_bp, 
    exploracion_bp, expediente_bp, usuario_bp
)

app = Flask(__name__)
app.secret_key = 'medical12345'

# Configuración CSRF
csrf = CSRFProtect(app)
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(cita_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(medico_bp)
app.register_blueprint(exploracion_bp)
app.register_blueprint(expediente_bp)
app.register_blueprint(usuario_bp)

# Filtros personalizados para templates
@app.template_filter('calcular_edad')
def calcular_edad_filter(fecha_nacimiento):
    """Filtro para calcular la edad basada en la fecha de nacimiento"""
    from models.paciente import Paciente
    return Paciente.calculate_age(fecha_nacimiento)

@app.template_filter('formato_fecha_input')
def formato_fecha_input_filter(fecha):
    """Filtro para formatear fechas para inputs HTML de tipo date"""
    if fecha:
        if isinstance(fecha, str):
            from datetime import datetime
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                return fecha_obj.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    fecha_obj = datetime.strptime(fecha, '%d/%m/%Y')
                    return fecha_obj.strftime('%Y-%m-%d')
                except ValueError:
                    return fecha
        else:
            return fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else str(fecha)
    return ''

@app.template_filter('fecha_hoy')
def fecha_hoy_filter(value):
    """Filtro para obtener la fecha actual en formato YYYY-MM-DD"""
    from datetime import date
    return date.today().strftime('%Y-%m-%d')

# Configuración de contexto para templates
@app.context_processor
def inject_user():

    from flask import session
    return {
        'user_logged_in': 'user_id' in session,
        'user_name': session.get('user_name', ''),
        'user_privilege': session.get('user_privilege', 0)
    }

if __name__ == '__main__':
    app.run(debug=True, port=4000)
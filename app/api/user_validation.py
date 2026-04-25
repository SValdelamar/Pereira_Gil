"""
Endpoint de diagnóstico y validación de datos de usuarios
Implementa buenas prácticas de desarrollo para troubleshooting
"""

from flask import Blueprint, jsonify, request, session
from app.utils.user_session_validator import UserSessionValidator, SessionManager
import logging

# Crear blueprint
user_validation_bp = Blueprint('user_validation', __name__, url_prefix='/api/user-validation')

logger = logging.getLogger(__name__)

@user_validation_bp.route('/check-integrity', methods=['GET'])
def check_user_integrity():
    """
    Verifica la integridad de datos del usuario actual
    
    Returns:
        JSON con estado de integridad y recomendaciones
    """
    if not session.get('user_id'):
        return jsonify({
            'success': False,
            'message': 'Usuario no autenticado'
        }), 401
    
    connection = None
    cursor = None
    try:
        # Obtener conexión y cursor de forma segura
        connection = db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obtener datos actuales del usuario
        cursor.execute("""
            SELECT id, nombre, email, nivel_acceso, a_cargo_inventario, laboratorio_id, tipo
            FROM usuarios 
            WHERE id = %s
        """, (session.get('user_id'),))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado en base de datos'
            }), 404
        
        # Validar integridad
        is_valid, validation_msg = UserSessionValidator.validate_instructor_integrity(user_data)
        
        # Obtener datos del laboratorio si aplica
        lab_info = None
        if user_data['laboratorio_id']:
            cursor.execute("""
                SELECT id, nombre, responsable_id
                FROM laboratorios 
                WHERE id = %s
            """, (user_data['laboratorio_id'],))
            lab_info = cursor.fetchone()
        
        # Construir respuesta detallada
        response = {
            'success': True,
            'user_data': {
                'id': user_data['id'],
                'nombre': user_data['nombre'],
                'email': user_data['email'],
                'nivel_acceso': user_data['nivel_acceso'],
                'tipo': user_data['tipo'],
                'a_cargo_inventario': bool(user_data['a_cargo_inventario']),
                'laboratorio_id': user_data['laboratorio_id']
            },
            'laboratorio_info': lab_info,
            'integrity_check': {
                'is_valid': is_valid,
                'message': validation_msg
            },
            'session_data': {
                'user_level': session.get('user_level'),
                'user_type': session.get('user_type'),
                'a_cargo_inventario': session.get('a_cargo_inventario'),
                'laboratorio_id': session.get('laboratorio_id')
            },
            'session_sync': {
                'needs_sync': (
                    user_data['nivel_acceso'] != session.get('user_level') or
                    user_data['tipo'] != session.get('user_type') or
                    bool(user_data['a_cargo_inventario']) != session.get('a_cargo_inventario') or
                    user_data['laboratorio_id'] != session.get('laboratorio_id')
                )
            },
            'recommendations': _generate_recommendations(user_data, lab_info, is_valid)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en verificación de integridad: {e}")
        return jsonify({
            'success': False,
            'message': f'Error en verificación: {str(e)}'
        }), 500
    finally:
        # Cerrar cursor de forma segura
        if cursor:
            cursor.close()
        # No cerrar la conexión aquí, dejar que el db_manager la gestione

@user_validation_bp.route('/fix-integrity', methods=['POST'])
def fix_user_integrity():
    """
    Corrige automáticamente la integridad de datos del usuario
    
    Returns:
        JSON con resultado de la corrección
    """
    if not session.get('user_id'):
        return jsonify({
            'success': False,
            'message': 'Usuario no autenticado'
        }), 401
    
    try:
        # Usar el validador para corregir integridad
        fixed, message = UserSessionValidator.fix_instructor_integrity(
            session.get('user_id'), 
            db_manager
        )
        
        if fixed:
            # Forzar sincronización de sesión después de corrección
            sync_result = SessionManager.sync_session_with_db(
                session, 
                session.get('user_id'), 
                db_manager
            )
            
            return jsonify({
                'success': True,
                'message': message,
                'sync_result': sync_result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error corrigiendo integridad: {e}")
        return jsonify({
            'success': False,
            'message': f'Error en corrección: {str(e)}'
        }), 500

@user_validation_bp.route('/sync-session', methods=['POST'])
def force_sync_session():
    """
    Fuerza la sincronización manual de la sesión
    
    Returns:
        JSON con resultado de la sincronización
    """
    if not session.get('user_id'):
        return jsonify({
            'success': False,
            'message': 'Usuario no autenticado'
        }), 401
    
    try:
        sync_result = SessionManager.sync_session_with_db(
            session, 
            session.get('user_id'), 
            db_manager
        )
        
        return jsonify(sync_result), 200
        
    except Exception as e:
        logger.error(f"Error en sincronización manual: {e}")
        return jsonify({
            'success': False,
            'message': f'Error en sincronización: {str(e)}'
        }), 500

def _generate_recommendations(user_data, lab_info, is_valid):
    """Genera recomendaciones basadas en el estado del usuario"""
    recommendations = []
    
    if not is_valid:
        recommendations.append({
            'type': 'error',
            'message': 'Se detectaron inconsistencias en los datos del usuario',
            'action': 'fix_integrity',
            'action_text': 'Corregir automáticamente'
        })
    
    if user_data['nivel_acceso'] == 5:
        if not user_data['laboratorio_id']:
            recommendations.append({
                'type': 'warning',
                'message': 'Instructor nivel 5 sin laboratorio asignado',
                'action': 'assign_lab',
                'action_text': 'Asignar laboratorio'
            })
        elif lab_info and lab_info['responsible_id'] != user_data['id']:
            recommendations.append({
                'type': 'warning',
                'message': 'No eres responsable del laboratorio asignado',
                'action': 'fix_responsibility',
                'action_text': 'Asignar como responsable'
            })
    
    # Recomendaciones generales
    if user_data['tipo'] != UserSessionValidator._get_tipo_esperado(user_data['nivel_acceso']):
        recommendations.append({
            'type': 'info',
            'message': f'Tipo de usuario "{user_data["tipo"]}" no coincide con nivel {user_data["nivel_acceso"]}',
            'action': 'fix_type',
            'action_text': 'Corregir tipo'
        })
    
    return recommendations

# Registrar blueprint
def register_user_validation_routes(app):
    """Registra las rutas de validación en la app Flask"""
    app.register_blueprint(user_validation_bp)

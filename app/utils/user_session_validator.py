"""
Utils de validación y sincronización de datos de usuarios
Implementa buenas prácticas de desarrollo para integridad de datos
"""

from typing import Dict, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserSessionValidator:
    """Validador de integridad de sesión de usuario"""
    
    @staticmethod
    def validate_instructor_integrity(user_data: Dict) -> Tuple[bool, str]:
        """
        Valida la integridad de datos de instructor según reglas de negocio
        
        Args:
            user_data: Diccionario con datos del usuario
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        try:
            # Regla 1: Instructor nivel 5 debe tener laboratorio asignado
            if user_data.get('nivel_acceso') == 5:
                if not user_data.get('laboratorio_id'):
                    return False, "Instructor nivel 5 requiere laboratorio asignado"
                
                if not user_data.get('a_cargo_inventario'):
                    return False, "Instructor nivel 5 debe estar a cargo de inventario"
            
            # Regla 2: Si está a cargo de inventario, debe ser nivel 5
            if user_data.get('a_cargo_inventario'):
                if user_data.get('nivel_acceso') != 5:
                    return False, "Usuario a cargo de inventario debe ser nivel 5"
            
            # Regla 3: Consistencia entre nivel y tipo
            nivel = user_data.get('nivel_acceso', 0)
            tipo = user_data.get('tipo', '')
            
            tipo_esperado = UserSessionValidator._get_tipo_esperado(nivel)
            if tipo != tipo_esperado:
                return False, f"Tipo '{tipo}' no coincide con nivel {nivel} (debe ser '{tipo_esperado}')"
            
            return True, "Datos válidos"
            
        except Exception as e:
            logger.error(f"Error validando integridad de usuario: {e}")
            return False, f"Error en validación: {str(e)}"
    
    @staticmethod
    def _get_tipo_esperado(nivel_acceso: int) -> str:
        """Obtiene el tipo esperado según nivel de acceso"""
        tipos = {
            6: 'administrador',
            5: 'instructor',
            4: 'coordinador',
            3: 'instructor',
            2: 'usuario',
            1: 'aprendiz'
        }
        return tipos.get(nivel_acceso, 'usuario')
    
    @staticmethod
    def fix_instructor_integrity(user_id: str, db_manager) -> Tuple[bool, str]:
        """
        Corrige automáticamente la integridad de datos de instructor
        
        Args:
            user_id: ID del usuario a corregir
            db_manager: Gestor de base de datos
            
        Returns:
            Tuple[bool, str]: (se_corrigió, mensaje)
        """
        connection = None
        cursor = None
        try:
            # Obtener conexión y cursor de forma segura
            connection = db_manager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Obtener datos actuales
            cursor.execute("""
                SELECT id, nombre, nivel_acceso, a_cargo_inventario, laboratorio_id, tipo
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            if not user:
                return False, "Usuario no encontrado"
            
            corrections = []
            
            # Corrección 1: Consistencia nivel-tipo
            tipo_esperado = UserSessionValidator._get_tipo_esperado(user['nivel_acceso'])
            if user['tipo'] != tipo_esperado:
                cursor.execute("""
                    UPDATE usuarios SET tipo = %s WHERE id = %s
                """, (tipo_esperado, user_id))
                corrections.append(f"tipo corregido: {user['tipo']} → {tipo_esperado}")
            
            # Corrección 2: Instructor nivel 5 sin laboratorio
            if user['nivel_acceso'] == 5 and not user['laboratorio_id']:
                # Buscar laboratorio disponible
                cursor.execute("""
                    SELECT id, nombre FROM laboratorios 
                    WHERE responsable_id IS NULL 
                    ORDER BY nombre 
                    LIMIT 1
                """)
                lab_disponible = cursor.fetchone()
                
                if lab_disponible:
                    # Asignar laboratorio al usuario
                    cursor.execute("""
                        UPDATE usuarios SET laboratorio_id = %s WHERE id = %s
                    """, (lab_disponible['id'], user_id))
                    
                    # Asignar como responsable del laboratorio
                    cursor.execute("""
                        UPDATE laboratorios SET responsable_id = %s WHERE id = %s
                    """, (user_id, lab_disponible['id']))
                    
                    corrections.append(f"laboratorio asignado: {lab_disponible['nombre']}")
                else:
                    return False, "No hay laboratorios disponibles para instructor"
            
            # Corrección 3: Asegurar a_cargo_inventario para nivel 5
            if user['nivel_acceso'] == 5 and not user['a_cargo_inventario']:
                cursor.execute("""
                    UPDATE usuarios SET a_cargo_inventario = 1 WHERE id = %s
                """, (user_id,))
                corrections.append("a_cargo_inventario activado")
            
            # Corrección 4: Remover a_cargo_inventario si no es nivel 5
            if user['nivel_acceso'] != 5 and user['a_cargo_inventario']:
                cursor.execute("""
                    UPDATE usuarios SET a_cargo_inventario = 0, laboratorio_id = NULL WHERE id = %s
                """, (user_id,))
                corrections.append("a_cargo_inventario removido (no es nivel 5)")
            
            if corrections:
                connection.commit()
                mensaje = f"Corregido: {', '.join(corrections)}"
                logger.info(f"Integridad corregida para usuario {user_id}: {mensaje}")
                return True, mensaje
            else:
                return True, "Sin correcciones necesarias"
            
        except Exception as e:
            logger.error(f"Error corrigiendo integridad de usuario {user_id}: {e}")
            if connection:
                connection.rollback()
            return False, f"Error: {str(e)}"
        finally:
            # Cerrar cursor y conexión de forma segura
            if cursor:
                cursor.close()
            # No cerrar la conexión aquí, dejar que el db_manager la gestione

class SessionManager:
    """Gestor de sesión con validación automática"""
    
    @staticmethod
    def sync_session_with_db(session: Dict, user_id: str, db_manager) -> Dict:
        """
        Sincroniza sesión con base de datos aplicando validaciones
        
        Args:
            session: Sesión Flask actual
            user_id: ID del usuario
            db_manager: Gestor de base de datos
            
        Returns:
            Dict: Estado de sincronización
        """
        connection = None
        cursor = None
        try:
            # Obtener conexión y cursor de forma segura
            connection = db_manager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Obtener datos actualizados
            cursor.execute("""
                SELECT id, nombre, nivel_acceso, a_cargo_inventario, laboratorio_id, tipo
                FROM usuarios 
                WHERE id = %s AND activo = TRUE
            """, (user_id,))
            
            user_db = cursor.fetchone()
            
            if not user_db:
                return {
                    'success': False,
                    'message': 'Usuario no encontrado o inactivo',
                    'action': 'logout'
                }
            
            # Validar integridad
            is_valid, validation_msg = UserSessionValidator.validate_instructor_integrity(user_db)
            
            if not is_valid:
                # Intentar corregir automáticamente
                fixed, fix_msg = UserSessionValidator.fix_instructor_integrity(user_id, db_manager)
                
                if fixed:
                    # Recargar datos después de corrección
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT id, nombre, nivel_acceso, a_cargo_inventario, laboratorio_id, tipo
                        FROM usuarios 
                        WHERE id = %s AND activo = TRUE
                    """, (user_id,))
                    user_db = cursor.fetchone()
                    
                    logger.info(f"Datos corregidos para usuario {user_id}: {fix_msg}")
                else:
                    logger.error(f"No se pudo corregir integridad de usuario {user_id}: {fix_msg}")
            
            # Actualizar sesión si hay cambios
            changes = []
            
            if user_db['nivel_acceso'] != session.get('user_level'):
                session['user_level'] = user_db['nivel_acceso']
                changes.append('user_level')
            
            if user_db['tipo'] != session.get('user_type'):
                session['user_type'] = user_db['tipo']
                changes.append('user_type')
            
            if bool(user_db['a_cargo_inventario']) != session.get('a_cargo_inventario'):
                session['a_cargo_inventario'] = bool(user_db['a_cargo_inventario'])
                changes.append('a_cargo_inventario')
            
            if user_db['laboratorio_id'] != session.get('laboratorio_id'):
                session['laboratorio_id'] = user_db['laboratorio_id']
                changes.append('laboratorio_id')
            
            return {
                'success': True,
                'message': f"Sesión sincronizada. Cambios: {', '.join(changes) if changes else 'ninguno'}",
                'changes': changes,
                'user_data': user_db
            }
            
        except Exception as e:
            logger.error(f"Error sincronizando sesión: {e}")
            return {
                'success': False,
                'message': f'Error en sincronización: {str(e)}',
                'action': 'continue'
            }
        finally:
            # Cerrar cursor de forma segura
            if cursor:
                cursor.close()
            # No cerrar la conexión aquí, dejar que el db_manager la gestione

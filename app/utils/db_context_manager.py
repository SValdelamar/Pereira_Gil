"""
Context Manager para gestión segura de conexiones a base de datos
Implementa buenas prácticas de desarrollo para manejo de recursos
"""

from contextlib import contextmanager
from typing import Generator, Any
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db_cursor(db_manager, dictionary=True) -> Generator[Any, None, None]:
    """
    Context manager para obtener y gestionar cursor de base de datos de forma segura
    
    Args:
        db_manager: Gestor de base de datos
        dictionary: Si el cursor debe ser dictionary=True
        
    Yields:
        cursor: Cursor de base de datos listo para usar
        
    Example:
        with get_db_cursor(db_manager) as cursor:
            cursor.execute("SELECT * FROM usuarios")
            results = cursor.fetchall()
    """
    connection = None
    cursor = None
    try:
        # Obtener conexión de forma segura
        connection = db_manager.get_connection()
        cursor = connection.cursor(dictionary=dictionary)
        
        # Yield el cursor para uso en el bloque with
        yield cursor
        
    except Exception as e:
        logger.error(f"Error en operación de base de datos: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        # Cerrar cursor de forma segura
        if cursor:
            cursor.close()
        # No cerrar la conexión aquí, dejar que el db_manager la gestione

@contextmanager
def get_db_connection(db_manager) -> Generator[Any, None, None]:
    """
    Context manager para obtener conexión completa (para transacciones)
    
    Args:
        db_manager: Gestor de base de datos
        
    Yields:
        connection: Conexión de base de datos
        
    Example:
        with get_db_connection(db_manager) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nombre = %s", ("Nuevo",))
            conn.commit()
    """
    connection = None
    try:
        connection = db_manager.get_connection()
        yield connection
    except Exception as e:
        logger.error(f"Error en operación de base de datos: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        # No cerrar la conexión aquí, dejar que el db_manager la gestione

# Ejemplo de uso en el validador:
def validate_user_safe(user_id: str, db_manager) -> dict:
    """Ejemplo de uso del context manager"""
    try:
        with get_db_cursor(db_manager) as cursor:
            cursor.execute("""
                SELECT id, nombre, nivel_acceso
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            return user or {}
            
    except Exception as e:
        logger.error(f"Error validando usuario {user_id}: {e}")
        return {}

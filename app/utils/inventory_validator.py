"""
Clase de validación unificada para permisos de inventario
Implementa la lógica simplificada: solo responsables de inventario
"""

class InventoryPermissionsValidator:
    """Validador unificado de permisos de inventario"""
    
    def __init__(self, db_manager, permissions_manager):
        self.db_manager = db_manager
        self.permissions_manager = permissions_manager
    
    def validar_permiso_inventario(self, user_id, item_laboratorio_id, accion="gestionar"):
        """
        Validar permiso de inventario de forma unificada y robusta
        
        Args:
            user_id: ID del usuario
            item_laboratorio_id: ID del laboratorio del item
            accion: Descripción de la acción (para mensajes)
            
        Returns:
            dict: {
                'autorizado': bool,
                'mensaje': str,
                'user_level': int,
                'lab_instructor': int|None,
                'es_instructor': bool
            }
        """
        
        try:
            # 1. Obtener nivel del usuario
            user_level = self.permissions_manager.get_nivel_usuario(user_id)
            
            # 2. Administradores pueden gestionar todo
            if user_level == 6:
                return {
                    'autorizado': True,
                    'mensaje': f'Administrador autorizado para {accion}',
                    'user_level': user_level,
                    'lab_instructor': None,
                    'es_instructor': False
                }
            
            # 3. Verificar si es instructor con inventario
            es_instructor, lab_instructor = self.permissions_manager.es_instructor_con_inventario(user_id)
            
            if not es_instructor:
                return {
                    'autorizado': False,
                    'mensaje': f'Solo instructores a cargo de inventario pueden {accion}',
                    'user_level': user_level,
                    'lab_instructor': None,
                    'es_instructor': False
                }
            
            # 4. Validar que el item tenga laboratorio asignado
            if not item_laboratorio_id:
                return {
                    'autorizado': False,
                    'mensaje': 'El item no tiene laboratorio asignado. Contacte al administrador.',
                    'user_level': user_level,
                    'lab_instructor': lab_instructor,
                    'es_instructor': es_instructor
                }
            
            # 5. Validar coincidencia de laboratorios
            if item_laboratorio_id != lab_instructor:
                # Obtener nombres para mensaje claro
                query_nombres = """
                    SELECT 
                        (SELECT nombre FROM laboratorios WHERE id = %s) as lab_user,
                        (SELECT nombre FROM laboratorios WHERE id = %s) as lab_item
                """
                resultado = self.db_manager.execute_query(query_nombres, (lab_instructor, item_laboratorio_id))
                
                lab_user_name = f"Lab {lab_instructor}"
                lab_item_name = f"Lab {item_laboratorio_id}"
                
                if resultado and len(resultado) > 0:
                    lab_user_name = resultado[0]['lab_user'] or lab_user_name
                    lab_item_name = resultado[0]['lab_item'] or lab_item_name
                
                return {
                    'autorizado': False,
                    'mensaje': f'No tienes autorización para {accion} este laboratorio. Tu laboratorio: {lab_user_name}, Laboratorio del item: {lab_item_name}',
                    'user_level': user_level,
                    'lab_instructor': lab_instructor,
                    'es_instructor': es_instructor
                }
            
            # 6. Todo válido
            return {
                'autorizado': True,
                'mensaje': f'Instructor autorizado para {accion}',
                'user_level': user_level,
                'lab_instructor': lab_instructor,
                'es_instructor': es_instructor
            }
            
        except Exception as e:
            # En caso de error, denegar por seguridad
            return {
                'autorizado': False,
                'mensaje': f'Error de validación: {str(e)}',
                'user_level': 0,
                'lab_instructor': None,
                'es_instructor': False
            }
    
    def obtener_info_laboratorio(self, laboratorio_id):
        """
        Obtener información completa del laboratorio
        
        Returns:
            dict: Información del laboratorio o None si no existe
        """
        if not laboratorio_id:
            return None
            
        try:
            query = """
                SELECT id, nombre, tipo, estado, descripcion
                FROM laboratorios 
                WHERE id = %s
            """
            resultado = self.db_manager.execute_query(query, (laboratorio_id,))
            
            if resultado:
                return resultado[0]
            return None
            
        except Exception as e:
            print(f"Error obteniendo info laboratorio: {e}")
            return None
    
    def obtener_items_por_laboratorio(self, laboratorio_id, limite=None):
        """
        Obtener items de inventario por laboratorio con paginación
        
        Args:
            laboratorio_id: ID del laboratorio
            limite: Límite de resultados (opcional)
            
        Returns:
            list: Items del laboratorio
        """
        if not laboratorio_id:
            return []
            
        try:
            query = """
                SELECT i.*, l.nombre as laboratorio_nombre, l.tipo as laboratorio_tipo
                FROM inventario i
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                WHERE i.laboratorio_id = %s
                ORDER BY i.nombre
            """
            
            if limite:
                query += f" LIMIT {limite}"
            
            return self.db_manager.execute_query(query, (laboratorio_id,))
            
        except Exception as e:
            print(f"Error obteniendo items por laboratorio: {e}")
            return []
    
    def validar_item_con_laboratorio(self, item_id):
        """
        Validar que un item tenga laboratorio asignado
        
        Args:
            item_id: ID del item
            
        Returns:
            dict: {
                'valido': bool,
                'item': dict|None,
                'mensaje': str
            }
        """
        try:
            query = """
                SELECT i.*, l.nombre as laboratorio_nombre, l.tipo as laboratorio_tipo
                FROM inventario i
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                WHERE i.id = %s
            """
            resultado = self.db_manager.execute_query(query, (item_id,))
            
            if not resultado:
                return {
                    'valido': False,
                    'item': None,
                    'mensaje': 'Item no encontrado'
                }
            
            item = resultado[0]
            
            if not item['laboratorio_id']:
                return {
                    'valido': False,
                    'item': item,
                    'mensaje': 'El item no tiene laboratorio asignado. Contacte al administrador.'
                }
            
            return {
                'valido': True,
                'item': item,
                'mensaje': 'Item válido con laboratorio asignado'
            }
            
        except Exception as e:
            return {
                'valido': False,
                'item': None,
                'mensaje': f'Error validando item: {str(e)}'
            }

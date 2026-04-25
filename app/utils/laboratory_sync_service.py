"""
Servicio de Sincronización de Laboratorios y Usuarios
Mantiene la consistencia entre las asignaciones de laboratorios y los permisos de usuarios
"""

class LaboratorySyncService:
    """Servicio para sincronizar asignaciones de laboratorios con permisos de usuarios"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def sincronizar_instructor_laboratorio(self, laboratorio_id, nuevo_instructor_id):
        """
        Sincronizar la asignación de instructor responsable de un laboratorio
        con los permisos del usuario en la tabla de usuarios
        
        Args:
            laboratorio_id: ID del laboratorio
            nuevo_instructor_id: ID del nuevo instructor responsable
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'anterior_instructor': int|None,
                'datos_actualizados': dict
            }
        """
        try:
            # 1. Obtener información actual del laboratorio
            query_lab = """
                SELECT id, nombre
                FROM laboratorios 
                WHERE id = %s
            """
            resultado_lab = self.db_manager.execute_query(query_lab, (laboratorio_id,))
            
            if not resultado_lab:
                return {
                    'success': False,
                    'message': f'Laboratorio {laboratorio_id} no encontrado',
                    'anterior_instructor': None,
                    'datos_actualizados': {}
                }
            
            laboratorio = resultado_lab[0]
            
            # 2. Obtener instructor anterior asignado a este laboratorio
            query_instructor_anterior = """
                SELECT id, nombre 
                FROM usuarios 
                WHERE laboratorio_id = %s AND a_cargo_inventario = TRUE AND activo = TRUE
            """
            resultado_instructor_anterior = self.db_manager.execute_query(query_instructor_anterior, (laboratorio_id,))
            
            anterior_instructor = resultado_instructor_anterior[0]['id'] if resultado_instructor_anterior else None
            
            # 2. Si no hay cambios, retornar éxito
            if anterior_instructor == nuevo_instructor_id:
                return {
                    'success': True,
                    'message': f'No hay cambios en el instructor del laboratorio {laboratorio["nombre"]}',
                    'anterior_instructor': anterior_instructor,
                    'datos_actualizados': {}
                }
            
            # 3. Iniciar transacción para consistencia
            conn = self.db_manager.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            try:
                cursor.execute("START TRANSACTION")
                
                # 4. Revocar permisos del instructor anterior
                if anterior_instructor:
                    cursor.execute("""
                        UPDATE usuarios 
                        SET a_cargo_inventario = 0, laboratorio_id = NULL
                        WHERE id = %s
                    """, (anterior_instructor,))
                    
                    print(f"🔄 Revocados permisos de inventario al instructor anterior: {anterior_instructor}")
                
                # 5. Si hay un nuevo instructor, asignarlo
                if nuevo_instructor_id:
                    # Verificar que el usuario exista y sea instructor
                    cursor.execute("""
                        SELECT id, nombre, nivel_acceso
                        FROM usuarios 
                        WHERE id = %s
                    """, (nuevo_instructor_id,))
                    
                    usuario_result = cursor.fetchone()
                    
                    if not usuario_result:
                        cursor.execute("ROLLBACK")
                        return {
                            'success': False,
                            'message': f'Usuario {nuevo_instructor_id} no encontrado',
                            'anterior_instructor': anterior_instructor,
                            'datos_actualizados': {}
                        }
                    
                    # Verificar que sea instructor (nivel 2-5)
                    if usuario_result['nivel_acceso'] < 2 or usuario_result['nivel_acceso'] > 5:
                        cursor.execute("ROLLBACK")
                        return {
                            'success': False,
                            'message': f'El usuario {usuario_result["nombre"]} no es instructor (nivel: {usuario_result["nivel_acceso"]})',
                            'anterior_instructor': anterior_instructor,
                            'datos_actualizados': {}
                        }
                    
                    # Otorgar permisos de inventario
                    cursor.execute("""
                        UPDATE usuarios 
                        SET a_cargo_inventario = 1, laboratorio_id = %s
                        WHERE id = %s
                    """, (laboratorio_id, nuevo_instructor_id))
                    
                    print(f"✅ Otorgados permisos de inventario al nuevo instructor: {nuevo_instructor_id}")
                
                # 6. Registrar cambio en auditoría
                cursor.execute("""
                    INSERT INTO auditoría_laboratorios 
                    (laboratorio_id, usuario_id, accion, descripcion_anterior, descripcion_nueva, fecha)
                    VALUES (%s, %s, 'cambio_instructor', %s, %s, NOW())
                """, (
                    laboratorio_id,
                    1, # ID del admin (debería venir de sesión)
                    f"Instructor anterior: {anterior_instructor}",
                    f"Nuevo instructor: {nuevo_instructor_id}"
                ))
                
                cursor.execute("COMMIT")
                
                # 8. Preparar respuesta
                datos_actualizados = {
                    'laboratorio': laboratorio['nombre'],
                    'anterior_instructor': anterior_instructor,
                    'nuevo_instructor': nuevo_instructor_id,
                    'nuevo_instructor_nombre': usuario_result['nombre'] if nuevo_instructor_id else None
                }
                
                return {
                    'success': True,
                    'message': f'Laboratorio {laboratorio["nombre"]} actualizado correctamente. Instructor: {usuario_result["nombre"] if nuevo_instructor_id else "Sin asignar"}',
                    'anterior_instructor': anterior_instructor,
                    'datos_actualizados': datos_actualizados
                }
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"❌ Error sincronizando instructor de laboratorio: {e}")
            return {
                'success': False,
                'message': f'Error de sincronización: {str(e)}',
                'anterior_instructor': None,
                'datos_actualizados': {}
            }
    
    def verificar_consistencia_laboratorios(self):
        """
        Verificar consistencia entre laboratorios y usuarios
        Identificar discrepancias en las asignaciones
        
        Returns:
            dict: {
                'total_laboratorios': int,
                'inconsistencias': list,
                'mensaje': str
            }
        """
        try:
            # Buscar inconsistencias - laboratorios con instructores asignados pero sin consistencia
            query_inconsistencias = """
                SELECT 
                    l.id as lab_id,
                    l.nombre as lab_nombre,
                    u.id as user_id,
                    u.nombre as user_nombre,
                    u.laboratorio_id as user_lab_id,
                    u.a_cargo_inventario as user_inventario
                FROM laboratorios l
                LEFT JOIN usuarios u ON u.laboratorio_id = l.id AND u.a_cargo_inventario = TRUE
                WHERE 
                    u.id IS NULL OR 
                    u.laboratorio_id != l.id OR 
                    u.a_cargo_inventario != 1
            """
            
            inconsistencias = self.db_manager.execute_query(query_inconsistencias)
            
            # Contar laboratorios totales
            query_total = "SELECT COUNT(*) as total FROM laboratorios"
            resultado_total = self.db_manager.execute_query(query_total)
            total_laboratorios = resultado_total[0]['total'] if resultado_total else 0
            
            mensaje = f"Verificación completada. {len(inconsistencias)} inconsistencias encontradas de {total_laboratorios} laboratorios."
            
            return {
                'total_laboratorios': total_laboratorios,
                'inconsistencias': inconsistencias or [],
                'mensaje': mensaje
            }
            
        except Exception as e:
            print(f"❌ Error verificando consistencia: {e}")
            return {
                'total_laboratorios': 0,
                'inconsistencias': [],
                'mensaje': f'Error en verificación: {str(e)}'
            }
    
    def sincronizar_masivo(self):
        """
        Sincronizar masivamente todas las asignaciones
        Útil para reparar datos inconsistentes
        
        Returns:
            dict: Resultado de la sincronización masiva
        """
        try:
            # Obtener todos los usuarios que son instructores con inventario
            query_asignaciones = """
                SELECT id, nombre, laboratorio_id
                FROM usuarios 
                WHERE a_cargo_inventario = TRUE AND activo = TRUE
                AND laboratorio_id IS NOT NULL
            """
            
            asignaciones = self.db_manager.execute_query(query_asignaciones)
            
            resultados = []
            errores = []
            
            for asignacion in asignaciones:
                resultado = self.sincronizar_instructor_laboratorio(
                    asignacion['laboratorio_id'], 
                    asignacion['id']
                )
                
                if resultado['success']:
                    resultados.append(resultado)
                else:
                    errores.append(resultado)
            
            return {
                'success': len(errores) == 0,
                'message': f'Sincronización masiva completada. {len(resultados)} exitosos, {len(errores)} errores.',
                'resultados': resultados,
                'errores': errores
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error en sincronización masiva: {str(e)}',
                'resultados': [],
                'errores': []
            }

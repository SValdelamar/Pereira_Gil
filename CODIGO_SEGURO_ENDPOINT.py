# =====================================================================
# ENDPOINT SEGURO - REGISTRO COMPLETO
# Reemplazar en web_app.py líneas 4764-4958
# =====================================================================

from app.utils.security_validators import SecurityValidator, create_error_response, create_success_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiter (agregar al inicio de web_app.py)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.route('/api/registro-completo', methods=['POST'])
@require_login
@require_level(4)
@limiter.limit("10 per minute")  # ← Rate limiting
def api_registro_completo_seguro():
    """
    API SEGURA para guardar registro completo (equipo/item + fotos + IA)
    
    MEJORAS DE SEGURIDAD:
    - ✅ Validación estricta de todos los campos
    - ✅ Sanitización de nombres de archivo
    - ✅ Validación de imágenes (tamaño, tipo, dimensiones)
    - ✅ Prevención de path traversal
    - ✅ Rate limiting
    - ✅ Manejo seguro de errores
    - ✅ Logs de seguridad mejorados
    """
    import json
    import uuid
    import base64
    import io
    import os
    from datetime import datetime
    
    try:
        # ==================================================================
        # PASO 1: OBTENER Y VALIDAR DATOS
        # ==================================================================
        
        data = request.get_json()
        
        if not data:
            return create_error_response('No se recibieron datos', 400)
        
        # Validación completa usando SecurityValidator
        es_valido, mensaje, datos_sanitizados = SecurityValidator.validate_registro_completo(data)
        
        if not es_valido:
            # Log de intento fallido
            try:
                log_security_event(
                    user_id=session.get('user_id'),
                    action='registro_completo_validacion_fallida',
                    detail=mensaje,
                    ip=request.remote_addr,
                    success=False
                )
            except:
                pass
            
            return create_error_response(mensaje, 400)
        
        # Extraer datos sanitizados
        tipo_registro = datos_sanitizados['tipo_registro']
        nombre = datos_sanitizados['nombre']
        categoria = datos_sanitizados['categoria']
        descripcion = datos_sanitizados['descripcion']
        laboratorio_id = datos_sanitizados['laboratorio_id']
        ubicacion = datos_sanitizados['ubicacion']
        estado = datos_sanitizados['estado']
        cantidad = datos_sanitizados['cantidad']
        fotos = datos_sanitizados['fotos']
        
        # ==================================================================
        # PASO 2: VALIDAR LABORATORIO EXISTE
        # ==================================================================
        
        query_lab_check = "SELECT id FROM laboratorios WHERE id = %s"
        lab_exists = db_manager.execute_query(query_lab_check, (laboratorio_id,))
        
        if not lab_exists:
            return create_error_response('Laboratorio no existe', 400)
        
        # ==================================================================
        # PASO 3: INICIAR TRANSACCIÓN
        # ==================================================================
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # ==============================================================
            # PASO 4: CREAR REGISTRO EN EQUIPOS O INVENTARIO
            # ==============================================================
            
            if tipo_registro == 'equipo':
                # Crear equipo con ID único
                equipo_id = f"EQ_{str(uuid.uuid4())[:8].upper()}"
                
                query_equipo = """
                    INSERT INTO equipos (id, nombre, tipo, estado, ubicacion, laboratorio_id, especificaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_equipo, (
                    equipo_id,
                    nombre,
                    categoria,
                    estado,
                    ubicacion,
                    laboratorio_id,
                    json.dumps({'descripcion': descripcion}, ensure_ascii=False)
                ))
                registro_id = equipo_id
                
            else:  # item de inventario
                # Crear item con ID único
                item_id = f"ITEM_{str(uuid.uuid4())[:8].upper()}"
                
                query_item = """
                    INSERT INTO inventario (id, nombre, categoria, laboratorio_id, cantidad)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query_item, (
                    item_id,
                    nombre,
                    categoria,
                    laboratorio_id,
                    cantidad
                ))
                registro_id = item_id
            
            # ==============================================================
            # PASO 5: CREAR OBJETO PARA IA
            # ==============================================================
            
            objeto_id = None
            imagenes_guardadas = []
            
            if fotos:
                query_objeto = """
                    INSERT INTO objetos (nombre, categoria, descripcion, equipo_id)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_objeto, (
                    nombre,
                    categoria,
                    descripcion,
                    equipo_id if tipo_registro == 'equipo' else None
                ))
                objeto_id = cursor.lastrowid
                
                # ==========================================================
                # PASO 6: GUARDAR IMÁGENES DE FORMA SEGURA
                # ==========================================================
                
                # Crear nombre de carpeta seguro
                nombre_carpeta = SecurityValidator.sanitize_filename(nombre)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_carpeta = f"{nombre_carpeta}_{timestamp}"
                
                # Determinar directorio base seguro
                BASE_IMAGENES_DIR = os.path.abspath('imagenes')
                tipo_dir = 'equipo' if tipo_registro == 'equipo' else 'item'
                
                # Validar path (prevenir path traversal)
                objeto_dir_relativo = os.path.join(tipo_dir, nombre_carpeta)
                es_valido_path, objeto_dir = SecurityValidator.validate_path(
                    BASE_IMAGENES_DIR,
                    objeto_dir_relativo
                )
                
                if not es_valido_path:
                    raise ValueError('Path de destino inválido (posible ataque)')
                
                # Crear directorio
                os.makedirs(objeto_dir, exist_ok=True)
                
                # Procesar cada imagen
                for vista, imagen_base64 in fotos.items():
                    # Validar imagen
                    es_valida, mensaje_img, imagen = SecurityValidator.validate_image(imagen_base64)
                    
                    if not es_valida:
                        raise ValueError(f'Imagen inválida en vista {vista}: {mensaje_img}')
                    
                    # Nombre de archivo seguro
                    filename = f"{SecurityValidator.sanitize_filename(vista)}.jpg"
                    filepath = os.path.join(objeto_dir, filename)
                    
                    # Guardar imagen con calidad optimizada
                    imagen.save(filepath, 'JPEG', quality=85, optimize=True)
                    
                    # Ruta relativa para BD
                    ruta_relativa = os.path.join('imagenes', tipo_dir, nombre_carpeta, filename)
                    
                    # Insertar en base de datos
                    query_imagen = """
                        INSERT INTO objetos_imagenes (objeto_id, path, vista)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query_imagen, (objeto_id, ruta_relativa, vista))
                    
                    imagenes_guardadas.append(vista)
                
                # ==========================================================
                # PASO 7: CREAR METADATOS PARA IA
                # ==========================================================
                
                # Obtener información del laboratorio
                lab_query = "SELECT nombre, ubicacion FROM laboratorios WHERE id = %s"
                lab_result = db_manager.execute_query(lab_query, (laboratorio_id,))
                laboratorio_nombre = lab_result[0]['nombre'] if lab_result else 'Desconocido'
                laboratorio_ubicacion = lab_result[0]['ubicacion'] if lab_result else 'Desconocido'
                
                metadatos = {
                    'id': objeto_id,
                    'nombre': nombre,
                    'tipo': tipo_registro,
                    'categoria': categoria,
                    'descripcion': descripcion,
                    'ubicacion': ubicacion,
                    'laboratorio_id': laboratorio_id,
                    'laboratorio_nombre': laboratorio_nombre,
                    'laboratorio_ubicacion': laboratorio_ubicacion,
                    'cantidad': cantidad if tipo_registro == 'item' else None,
                    'estado': estado if tipo_registro == 'equipo' else None,
                    'equipo_id': equipo_id if tipo_registro == 'equipo' else None,
                    'fotos_capturadas': imagenes_guardadas,
                    'total_fotos': len(imagenes_guardadas),
                    'entrenado_ia': len(imagenes_guardadas) == 6,
                    'ruta_imagenes': os.path.join('imagenes', tipo_dir, nombre_carpeta),
                    'fecha_creacion': datetime.now().isoformat(),
                    'creado_por': session.get('user_id')
                }
                
                metadata_path = os.path.join(objeto_dir, 'metadata.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadatos, f, indent=2, ensure_ascii=False)
                
                # ==========================================================
                # PASO 8: ACTUALIZAR EQUIPO CON OBJETO_ID Y ENTRENADO_IA
                # ==========================================================
                
                if tipo_registro == 'equipo' and objeto_id:
                    entrenado_ia = len(imagenes_guardadas) == 6
                    query_update = """
                        UPDATE equipos 
                        SET objeto_id = %s, entrenado_ia = %s
                        WHERE id = %s
                    """
                    cursor.execute(query_update, (objeto_id, entrenado_ia, equipo_id))
            
            # ==============================================================
            # PASO 9: COMMIT DE LA TRANSACCIÓN
            # ==============================================================
            
            conn.commit()
            
            # ==============================================================
            # PASO 10: LOG DE AUDITORÍA EXITOSO
            # ==============================================================
            
            try:
                log_security_event(
                    user_id=session.get('user_id'),
                    action='registro_completo',
                    detail=f"Registro exitoso: {nombre} ({tipo_registro}) - {len(imagenes_guardadas)} fotos",
                    ip=request.remote_addr,
                    success=True
                )
            except Exception as log_err:
                # No fallar por error en logging
                print(f"[WARNING] Error al guardar log: {log_err}")
            
            # ==============================================================
            # PASO 11: RESPUESTA EXITOSA
            # ==============================================================
            
            return create_success_response({
                'message': 'Registro guardado exitosamente',
                'id': registro_id,
                'objeto_id': objeto_id,
                'entrenado_ia': len(imagenes_guardadas) == 6 if fotos else False,
                'imagenes_guardadas': len(imagenes_guardadas)
            }, 201)
            
        except Exception as e:
            # Rollback en caso de error
            conn.rollback()
            cursor.close()
            conn.close()
            
            # Log de error
            try:
                log_security_event(
                    user_id=session.get('user_id'),
                    action='registro_completo_error',
                    detail=f"Error: {type(e).__name__}",
                    ip=request.remote_addr,
                    success=False
                )
            except:
                pass
            
            raise e
            
    except ValueError as e:
        # Error de validación
        return create_error_response(str(e), 400)
        
    except Exception as e:
        # Error genérico - NO EXPONER DETALLES
        print(f"[ERROR] Error en registro completo: {type(e).__name__}")
        
        # En desarrollo, mostrar más detalles
        if app.debug:
            import traceback
            traceback.print_exc()
            return create_error_response(f'Error interno: {str(e)}', 500)
        else:
            # En producción, mensaje genérico
            return create_error_response('Error al procesar el registro. Por favor intente nuevamente.', 500)


# =====================================================================
# FUNCIÓN AUXILIAR PARA LOGGING
# =====================================================================

def log_security_event(user_id, action, detail, ip, success):
    """Registra eventos de seguridad en la base de datos"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        log_query = """
            INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso, fecha)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(log_query, (user_id, action, detail, ip, success))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[WARNING] Error al guardar log de seguridad: {e}")


# =====================================================================
# INSTALACIÓN DE DEPENDENCIAS NECESARIAS
# =====================================================================
# 
# Agregar a requirements.txt:
#   Flask-Limiter==3.5.0
# 
# Instalar con:
#   pip install Flask-Limiter
# 
# =====================================================================

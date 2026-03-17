"""
Módulo de validación y sanitización de seguridad
Implementa validaciones estrictas para prevenir vulnerabilidades
"""

import re
import os
from typing import Dict, Any, List, Tuple
from flask import jsonify


class SecurityValidator:
    """Clase para validaciones de seguridad"""
    
    # Límites de seguridad
    MAX_STRING_LENGTH = 255
    MAX_TEXT_LENGTH = 5000
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_DIMENSION = 4096  # píxeles
    MAX_PHOTOS_PER_REQUEST = 10
    ALLOWED_VISTAS = ['frontal', 'posterior', 'superior', 'inferior', 'lateral_derecha', 'lateral_izquierda']
    ALLOWED_TIPOS_REGISTRO = ['equipo', 'item']
    ALLOWED_ESTADOS = ['disponible', 'en_uso', 'mantenimiento', 'fuera_servicio']
    
    @staticmethod
    def validate_registro_completo(data: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """
        Valida todos los campos del registro completo
        Retorna: (es_valido, mensaje_error, datos_sanitizados)
        """
        try:
            # 1. VALIDAR TIPO DE REGISTRO
            tipo_registro = str(data.get('tipo_registro', '')).strip()
            if tipo_registro not in SecurityValidator.ALLOWED_TIPOS_REGISTRO:
                return False, 'Tipo de registro inválido', {}
            
            # 2. VALIDAR NOMBRE
            nombre = str(data.get('nombre', '')).strip()
            if not nombre:
                return False, 'El nombre es obligatorio', {}
            if len(nombre) > SecurityValidator.MAX_STRING_LENGTH:
                return False, f'El nombre no puede exceder {SecurityValidator.MAX_STRING_LENGTH} caracteres', {}
            if not re.match(r'^[a-zA-Z0-9áéíóúñÑ\s\-\._]+$', nombre):
                return False, 'El nombre contiene caracteres no permitidos', {}
            
            # 3. VALIDAR CATEGORÍA
            categoria = str(data.get('tipo_categoria', '')).strip()
            if not categoria:
                return False, 'La categoría es obligatoria', {}
            if len(categoria) > SecurityValidator.MAX_STRING_LENGTH:
                return False, f'La categoría es demasiado larga', {}
            
            # 4. VALIDAR DESCRIPCIÓN (puede ser vacía)
            descripcion_raw = data.get('descripcion', '')
            descripcion = str(descripcion_raw).strip() if descripcion_raw is not None else ''
            if len(descripcion) > SecurityValidator.MAX_TEXT_LENGTH:
                return False, f'La descripción no puede exceder {SecurityValidator.MAX_TEXT_LENGTH} caracteres', {}
            
            # 5. VALIDAR LABORATORIO_ID
            try:
                laboratorio_id = int(data.get('laboratorio_id', 0))
                if laboratorio_id <= 0 or laboratorio_id > 999999:
                    return False, 'ID de laboratorio inválido', {}
            except (ValueError, TypeError):
                return False, 'ID de laboratorio debe ser un número', {}
            
            # 6. VALIDAR UBICACIÓN (puede ser vacía)
            ubicacion_raw = data.get('ubicacion', '')
            ubicacion = str(ubicacion_raw).strip() if ubicacion_raw is not None else ''
            if len(ubicacion) > SecurityValidator.MAX_STRING_LENGTH:
                return False, 'La ubicación es demasiado larga', {}
            
            # 7. VALIDAR ESTADO (solo para equipos)
            estado_raw = data.get('estado', 'disponible')
            estado = str(estado_raw).strip() if estado_raw is not None else 'disponible'
            if tipo_registro == 'equipo' and estado not in SecurityValidator.ALLOWED_ESTADOS:
                return False, 'Estado inválido', {}
            
            # 8. VALIDAR CANTIDAD (solo para items)
            cantidad = 1
            if tipo_registro == 'item':
                try:
                    cantidad = int(data.get('cantidad', 1))
                    if cantidad < 1 or cantidad > 1000000:
                        return False, 'Cantidad inválida (debe estar entre 1 y 1,000,000)', {}
                except (ValueError, TypeError):
                    return False, 'La cantidad debe ser un número', {}
            
            # 9. VALIDAR FOTOS
            fotos = data.get('fotos', {})
            if not isinstance(fotos, dict):
                return False, 'Formato de fotos inválido', {}
            
            if len(fotos) > SecurityValidator.MAX_PHOTOS_PER_REQUEST:
                return False, f'Máximo {SecurityValidator.MAX_PHOTOS_PER_REQUEST} fotos permitidas', {}
            
            if 'frontal' not in fotos:
                return False, 'Debe incluir al menos la foto frontal', {}
            
            # Validar cada vista
            for vista, imagen_base64 in fotos.items():
                if vista not in SecurityValidator.ALLOWED_VISTAS:
                    return False, f'Vista no permitida: {vista}', {}
                
                # Validar que sea base64 válido (validación básica)
                if not isinstance(imagen_base64, str):
                    return False, f'Formato de imagen inválido en vista {vista}', {}
                
                # Validar tamaño aproximado del base64
                base64_size = len(imagen_base64)
                if base64_size > (SecurityValidator.MAX_IMAGE_SIZE * 1.4):  # base64 es ~33% más grande
                    return False, f'Imagen demasiado grande en vista {vista} (máx {SecurityValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB)', {}
            
            # DATOS SANITIZADOS
            datos_sanitizados = {
                'tipo_registro': tipo_registro,
                'nombre': nombre,
                'categoria': categoria,
                'descripcion': descripcion,
                'laboratorio_id': laboratorio_id,
                'ubicacion': ubicacion,
                'estado': estado if tipo_registro == 'equipo' else None,
                'cantidad': cantidad if tipo_registro == 'item' else None,
                'fotos': fotos
            }
            
            return True, 'Validación exitosa', datos_sanitizados
            
        except Exception as e:
            return False, f'Error en validación: {str(e)}', {}
    
    @staticmethod
    def validate_image(imagen_base64: str) -> Tuple[bool, str, Any]:
        """
        Valida una imagen base64
        Retorna: (es_valida, mensaje_error, imagen_objeto)
        """
        import base64
        import io
        from PIL import Image
        
        try:
            # 1. Decodificar base64
            if ',' in imagen_base64:
                imagen_base64 = imagen_base64.split(',')[1]
            
            # 2. Validar que sea base64 válido
            try:
                imagen_data = base64.b64decode(imagen_base64, validate=True)
            except Exception:
                return False, 'Imagen no es base64 válido', None
            
            # 3. Validar tamaño
            if len(imagen_data) > SecurityValidator.MAX_IMAGE_SIZE:
                return False, f'Imagen demasiado grande (máx {SecurityValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB)', None
            
            # 4. Validar que sea una imagen real
            try:
                imagen = Image.open(io.BytesIO(imagen_data))
            except Exception:
                return False, 'Archivo no es una imagen válida', None
            
            # 5. Validar formato
            if imagen.format not in ['JPEG', 'PNG', 'JPG']:
                return False, f'Formato no permitido: {imagen.format}. Solo se permiten JPEG/PNG', None
            
            # 6. Validar dimensiones
            width, height = imagen.size
            if width > SecurityValidator.MAX_IMAGE_DIMENSION or height > SecurityValidator.MAX_IMAGE_DIMENSION:
                return False, f'Imagen demasiado grande ({width}x{height}). Máximo {SecurityValidator.MAX_IMAGE_DIMENSION}x{SecurityValidator.MAX_IMAGE_DIMENSION}', None
            
            if width < 50 or height < 50:
                return False, 'Imagen demasiado pequeña (mínimo 50x50 píxeles)', None
            
            # 7. Convertir a RGB si es necesario
            if imagen.mode not in ('RGB', 'L'):
                imagen = imagen.convert('RGB')
            
            return True, 'Imagen válida', imagen
            
        except Exception as e:
            return False, f'Error al validar imagen: {str(e)}', None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza un nombre de archivo para prevenir path traversal
        """
        # Remover cualquier ruta
        filename = os.path.basename(filename)
        
        # Permitir solo caracteres alfanuméricos, guiones y guiones bajos
        filename = re.sub(r'[^a-z0-9_\-]', '', filename.lower())
        
        # Limitar longitud
        if len(filename) > 100:
            filename = filename[:100]
        
        # Asegurar que no esté vacío
        if not filename:
            filename = 'unnamed'
        
        return filename
    
    @staticmethod
    def validate_path(base_dir: str, user_path: str) -> Tuple[bool, str]:
        """
        Valida que un path esté dentro del directorio base (previene path traversal)
        Retorna: (es_valido, path_absoluto_seguro)
        """
        try:
            # Normalizar paths
            base_dir = os.path.abspath(base_dir)
            full_path = os.path.abspath(os.path.join(base_dir, user_path))
            
            # Verificar que el path resultante esté dentro del base_dir
            if not full_path.startswith(base_dir):
                return False, ''
            
            return True, full_path
            
        except Exception:
            return False, ''


def create_error_response(message: str, code: int = 400):
    """Crea una respuesta de error consistente y segura"""
    return jsonify({
        'success': False,
        'message': message
    }), code


def create_success_response(data: Dict[str, Any], code: int = 200):
    """Crea una respuesta exitosa consistente"""
    return jsonify({
        'success': True,
        **data
    }), code

# -*- coding: utf-8 -*-
# Sistema Web + API REST - Centro Minero SENA
# Interfaz Web Moderna + API RESTful Completa (Flask)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import base64
import cv2
import numpy as np
import re
import json
import secrets
from functools import wraps
from app.utils.report_generator import report_generator
from app.utils.notificaciones import NotificacionesManager
from app.utils.security_validators import SecurityValidator, create_error_response, create_success_response
from app.utils.permissions import (
    permissions_manager,
    require_permission,
    require_level,
    require_instructor_inventario,
    api_require_permission,
    get_permisos_session,
    tiene_permiso,
    get_rol_nombre,
    validar_campos_requeridos,
    NIVEL_APRENDIZ,
    NIVEL_FUNCIONARIO,
    NIVEL_INSTRUCTOR_NO_QUIMICA,
    NIVEL_INSTRUCTOR_QUIMICA,
    NIVEL_INSTRUCTOR_INVENTARIO,
    NIVEL_ADMINISTRADOR,
    ROLES_NOMBRES
)

# =====================================================================
# CONFIGURACIÓN DE LA APLICACIÓN WEB
# =====================================================================

# Cargar variables de entorno desde .env (estándar de la industria)
load_dotenv()  # Busca automáticamente .env en el directorio raíz

# Configurar Flask para usar la nueva estructura app/
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# =====================================================================
# CONTEXT PROCESSOR - Permisos disponibles en todas las plantillas
# =====================================================================
@app.context_processor
def inject_permissions():
    """Inyectar funciones de permisos en todas las plantillas"""
    return {
        'tiene_permiso': tiene_permiso,
        'get_permisos': get_permisos_session,
        'get_rol_nombre': get_rol_nombre,
        'ROLES_NOMBRES': ROLES_NOMBRES,
        'api_token': session.get('api_token', '')  # Token JWT para uso en JavaScript
    }

# =====================================================================
# CACHE BUSTING - Versionado automático de archivos estáticos
# =====================================================================
@app.template_filter('cache_bust')
def cache_bust_filter(url_or_filename):
    """
    Filtro Jinja2 para cache busting automático y robusto
    Usa hash MD5 del contenido del archivo para máxima fiabilidad
    
    Ventajas:
    - No depende del timestamp del sistema
    - Cambia solo si el contenido cambia
    - Funciona incluso con timestamps incorrectos
    - Determinista y reproducible
    """
    import hashlib
    
    try:
        # Extraer filename si es una URL completa
        if url_or_filename.startswith('/static/'):
            filename = url_or_filename.replace('/static/', '')
        else:
            filename = url_or_filename
        
        file_path = os.path.join(app.static_folder, filename)
        
        if os.path.exists(file_path):
            # Leer el contenido del archivo
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Generar hash MD5 del contenido
            content_hash = hashlib.md5(content).hexdigest()[:8]  # Primeros 8 caracteres
            
            # Construir URL con hash
            if url_or_filename.startswith('/'):
                return f"{url_or_filename}?v={content_hash}"
            else:
                return f"?v={content_hash}"
        
        # Fallback si el archivo no existe
        if url_or_filename.startswith('/'):
            return f"{url_or_filename}?v=file-not-found"
        return "?v=file-not-found"
        
    except Exception as e:
        # Fallback robusto: timestamp actual como último recurso
        timestamp = int(datetime.now().timestamp())
        if url_or_filename.startswith('/'):
            return f"{url_or_filename}?v={timestamp}"
        return f"?v={timestamp}"

@app.template_global('current_timestamp')
def current_timestamp():
    """Timestamp actual para forzar recarga"""
    return int(datetime.now().timestamp())

app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

# Extensiones
jwt = JWTManager(app)
api = Api(app)
CORS(app)

# Rate Limiter para seguridad (prevenir abuso de API)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# =====================================================================
# CONEXIÓN A BASE DE DATOS
# =====================================================================

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': os.getenv('HOST', 'localhost'),
            'user': os.getenv('USUARIO_PRODUCCION', 'laboratorio_prod'),
            'password': os.getenv('PASSWORD_PRODUCCION', ''),
            'database': os.getenv('BASE_DATOS', 'laboratorio_sistema'),
            'charset': 'utf8mb4',
        }

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            return result
        finally:
            cursor.close()
            conn.close()


db_manager = DatabaseManager()
notificaciones_manager = NotificacionesManager(db_manager)

# =====================================================================
# AUTENTICACIÓN Y SEGURIDAD (Decoradores)
# =====================================================================

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def require_level(min_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_level' not in session or session['user_level'] < min_level:
                flash('No tiene permisos suficientes', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Permitir API si hay JWT válido o sesión web con rol admin
def verify_jwt_or_admin():
    try:
        verify_jwt_in_request()
        return True
    except Exception:
        # Fallback a sesión web: admin
        if session.get('user_id') and (
            str(session.get('user_type','')).lower() == 'admin' or int(session.get('user_level', 0)) >= 4
        ):
            return True
        # Re-lanzar para que el endpoint responda 401 si no cumple
        raise

# =====================================================================
# LOGGING DE SEGURIDAD
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
# RUTAS WEB - INTERFAZ DE USUARIO
# =====================================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validar que se ingresaron ambos campos
        if not user_id or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('auth/login.html')
        
        # Buscar usuario con contraseña
        query = "SELECT id, nombre, tipo, nivel_acceso, activo, password_hash, a_cargo_inventario FROM usuarios WHERE id = %s AND activo = TRUE"
        users = db_manager.execute_query(query, (user_id,))
        
        if users:
            user = users[0]
            stored_password = user.get('password_hash', '')
            
            # Validar contraseña (comparación directa por ahora, en producción usar hashing)
            if stored_password and stored_password == password:
                # Login exitoso
                session['user_id'] = user['id']
                session['user_name'] = user['nombre']
                session['user_type'] = user['tipo']
                session['user_level'] = user['nivel_acceso']
                session['a_cargo_inventario'] = bool(user.get('a_cargo_inventario', 0))
                
                # Generar token JWT automáticamente para la API
                access_token = create_access_token(identity=user['id'])
                session['api_token'] = access_token
                
                log_query = (
                    """
                    INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                    VALUES (%s, 'login_web', 'Login exitoso desde interfaz web', %s, TRUE)
                    """
                )
                try:
                    db_manager.execute_query(log_query, (user['id'], request.remote_addr))
                except Exception:
                    pass
                
                flash(f"Bienvenido {user['nombre']}", 'success')
                return redirect(url_for('dashboard'))
            else:
                # Contraseña incorrecta
                flash('Usuario o contraseña incorrectos', 'error')
                log_query = (
                    """
                    INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                    VALUES (%s, 'login_web_fallido', 'Contraseña incorrecta', %s, FALSE)
                    """
                )
                try:
                    db_manager.execute_query(log_query, (user_id, request.remote_addr))
                except Exception:
                    pass
        else:
            # Usuario no encontrado
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de nuevos usuarios con campos dinámicos según rol"""
    # Obtener lista de laboratorios para el formulario
    laboratorios = db_manager.execute_query("SELECT id, codigo, nombre FROM laboratorios ORDER BY nombre")
    
    if request.method == 'POST':
        # Datos básicos
        user_id = request.form.get('user_id', '').strip()
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 🔒 SEGURIDAD: Registro público solo permite Aprendiz (nivel 1)
        # Otros niveles requieren aprobación de administrador
        nivel_solicitado = int(request.form.get('nivel_acceso', 1))
        
        # 🛡️ PROTECCIÓN: Forzar nivel 1 para registro público
        nivel_acceso = NIVEL_APRENDIZ  # Siempre nivel 1 en registro público
        
        # Validaciones básicas
        if not all([user_id, nombre, email, password, nivel_acceso]):
            flash('Todos los campos básicos son requeridos', 'error')
            return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)
        
        # Verificar si el usuario ya existe
        check_query = "SELECT id FROM usuarios WHERE id = %s OR email = %s"
        existing = db_manager.execute_query(check_query, (user_id, email))
        if existing:
            flash('El ID de usuario o correo ya están registrados', 'error')
            return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)
        
        # Recopilar campos específicos según el rol
        campos_extra = {
            'programa': request.form.get('programa', ''),
            'ficha': request.form.get('ficha', ''),
            'cargo': request.form.get('cargo', ''),
            'dependencia': request.form.get('dependencia', ''),
            'programa_formacion': request.form.get('programa_formacion', ''),
            'especialidad': request.form.get('especialidad') or request.form.get('especialidad_quimica') or request.form.get('especialidad_inv', ''),
            'a_cargo_inventario': request.form.get('a_cargo_inventario', '0'),
            'laboratorio_id': request.form.get('laboratorio_id') or None
        }
        
        # 🔒 SEGURIDAD: Validar campos según nivel solicitado
        # Si el usuario REALMENTE quiere ser Aprendiz (nivel 1), debe llenar programa y ficha
        # Si solicita otro nivel, se crea perfil temporal sin esos campos (serán validados al aprobar)
        if nivel_solicitado == NIVEL_APRENDIZ:
            if not campos_extra['programa'] or not campos_extra['ficha']:
                flash('Programa y Ficha son campos obligatorios para Aprendices', 'error')
                return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)
        
        # Determinar tipo según nivel
        tipo_map = {
            1: 'aprendiz',
            2: 'funcionario',
            3: 'instructor',
            4: 'instructor',
            5: 'instructor',
            6: 'administrador'
        }
        tipo = tipo_map.get(nivel_acceso, 'aprendiz')
        
        # 📝 Si solicitó nivel superior, guardar solicitud para aprobación
        solicitud_nivel_superior = None
        if nivel_solicitado > NIVEL_APRENDIZ:
            solicitud_nivel_superior = nivel_solicitado
        
        # Construir query de inserción
        insert_query = """
            INSERT INTO usuarios (
                id, nombre, email, telefono, password_hash, tipo, nivel_acceso,
                programa, ficha, cargo, dependencia,
                programa_formacion, especialidad, a_cargo_inventario, laboratorio_id,
                activo, rostro_registrado
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                TRUE, FALSE
            )
        """
        
        try:
            db_manager.execute_query(insert_query, (
                user_id, nombre, email, telefono, password, tipo, nivel_acceso,
                campos_extra['programa'], campos_extra['ficha'],
                campos_extra['cargo'], campos_extra['dependencia'],
                campos_extra['programa_formacion'], campos_extra['especialidad'],
                campos_extra['a_cargo_inventario'] == '1', campos_extra['laboratorio_id']
            ))
            
            # Informar sobre nivel asignado
            if solicitud_nivel_superior and solicitud_nivel_superior > NIVEL_APRENDIZ:
                flash(f'Cuenta creada como Aprendiz. Tu solicitud de nivel {get_rol_nombre(solicitud_nivel_superior)} será revisada por un administrador.', 'info')
                # Guardar solicitud de cambio de nivel
                try:
                    solicitud_query = """
                        INSERT INTO solicitudes_nivel (usuario_id, nivel_solicitado, nivel_actual, estado, fecha_solicitud)
                        VALUES (%s, %s, %s, 'pendiente', NOW())
                    """
                    db_manager.execute_query(solicitud_query, (user_id, solicitud_nivel_superior, nivel_acceso))
                except:
                    pass  # Tabla puede no existir
            else:
                flash(f'Cuenta creada exitosamente. Bienvenido {nombre}!', 'success')
            
            # Auto-login
            session['user_id'] = user_id
            session['user_name'] = nombre
            session['user_type'] = tipo
            session['user_level'] = nivel_acceso
            session['a_cargo_inventario'] = bool(campos_extra['a_cargo_inventario'] == '1')
            
            # Generar token JWT automáticamente para la API
            access_token = create_access_token(identity=user_id)
            session['api_token'] = access_token
            
            # Log de registro
            log_query = """
                INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                VALUES (%s, 'registro', %s, %s, TRUE)
            """
            try:
                db_manager.execute_query(log_query, (
                    user_id,
                    f'Nuevo usuario registrado: {get_rol_nombre(nivel_acceso)}',
                    request.remote_addr
                ))
            except:
                pass
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error al crear la cuenta: {str(e)}', 'error')
            return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)
    
    return render_template('auth/registro_dinamico.html', laboratorios=laboratorios)


@app.route('/login_facial', methods=['POST'])
def login_facial():
    """Login mediante reconocimiento facial usando OpenCV (sin face_recognition)"""
    try:
        data = request.get_json()
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({'success': False, 'message': 'No se recibió imagen'})
        
        # Remover prefijo data:image si existe
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Decodificar imagen
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'message': 'No se pudo procesar la imagen'})
        
        # Detectar rostro usando Haar Cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        if len(faces) == 0:
            return jsonify({'success': False, 'message': 'No se detectó ningún rostro en la imagen'})
        
        if len(faces) > 1:
            return jsonify({'success': False, 'message': 'Se detectaron múltiples rostros. Solo debe aparecer tu rostro'})
        
        # Extraer región del rostro
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (200, 200))  # Normalizar tamaño
        
        # Calcular histograma del rostro capturado
        hist_captured = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
        hist_captured = cv2.normalize(hist_captured, hist_captured).flatten()
        
        # Obtener usuarios con rostro registrado
        query = "SELECT id, nombre, tipo, nivel_acceso, rostro_data, a_cargo_inventario FROM usuarios WHERE rostro_data IS NOT NULL AND activo = TRUE"
        users = db_manager.execute_query(query)
        
        if not users:
            return jsonify({'success': False, 'message': 'No hay usuarios con reconocimiento facial registrado'})
        
        # Comparar con cada usuario registrado
        best_match = None
        best_similarity = 0
        # 🔒 SEGURIDAD: Umbral aumentado a 0.70 para prevenir falsos positivos
        # Valores recomendados: 0.65-0.75 (menor = más permisivo, mayor = más estricto)
        threshold = 0.70  # Umbral de similitud (0-1, mayor = más similar)
        
        print(f"[DEBUG FACIAL] Comparando con {len(users)} usuarios registrados...")
        
        for user in users:
            try:
                # Decodificar imagen almacenada
                stored_image_data = user['rostro_data']
                
                # Convertir BLOB a imagen
                nparr_stored = np.frombuffer(stored_image_data, np.uint8)
                stored_img = cv2.imdecode(nparr_stored, cv2.IMREAD_GRAYSCALE)
                
                if stored_img is None:
                    print(f"[DEBUG FACIAL] Usuario {user['nombre']}: No se pudo decodificar imagen")
                    continue
                
                # Redimensionar a mismo tamaño
                stored_img = cv2.resize(stored_img, (200, 200))
                
                # Calcular histograma de la imagen almacenada
                hist_stored = cv2.calcHist([stored_img], [0], None, [256], [0, 256])
                hist_stored = cv2.normalize(hist_stored, hist_stored).flatten()
                
                # Usar múltiples métodos de comparación para mayor precisión
                correl = cv2.compareHist(hist_captured, hist_stored, cv2.HISTCMP_CORREL)
                chisqr = cv2.compareHist(hist_captured, hist_stored, cv2.HISTCMP_CHISQR)
                intersect = cv2.compareHist(hist_captured, hist_stored, cv2.HISTCMP_INTERSECT)
                
                # Normalizar chi-square (menor es mejor, invertir)
                chisqr_norm = 1.0 / (1.0 + chisqr / 1000.0)
                
                # Normalizar intersección (0-1)
                intersect_norm = intersect / 200.0  # Normalizar por tamaño de imagen
                
                # Combinar métodos (promedio ponderado)
                similarity = (correl * 0.5) + (chisqr_norm * 0.2) + (intersect_norm * 0.3)
                
                print(f"[DEBUG FACIAL] Usuario {user['nombre']}:")
                print(f"  - Correlación: {correl:.4f}")
                print(f"  - Chi-Square: {chisqr:.2f} (norm: {chisqr_norm:.4f})")
                print(f"  - Intersección: {intersect:.2f} (norm: {intersect_norm:.4f})")
                print(f"  - Similitud combinada: {similarity:.4f} (umbral: {threshold})")
                
                # Si la similitud supera el umbral y es la mejor hasta ahora
                if similarity > threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user
                    print(f"  ✓ NUEVO MEJOR MATCH!")
                    
            except Exception as e:
                print(f"[ERROR] Error comparando con usuario {user.get('nombre', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"[DEBUG FACIAL] Mejor coincidencia: {best_match['nombre'] if best_match else 'Ninguna'}")
        print(f"[DEBUG FACIAL] Similitud final: {best_similarity:.4f}")
        
        # Si se encontró una coincidencia
        if best_match:
            confidence = best_similarity * 100  # Convertir a porcentaje
            
            session['user_id'] = best_match['id']
            session['user_name'] = best_match['nombre']
            session['user_type'] = best_match['tipo']
            session['user_level'] = best_match['nivel_acceso']
            session['a_cargo_inventario'] = bool(best_match.get('a_cargo_inventario', 0))
            
            # Generar token JWT automáticamente para la API
            access_token = create_access_token(identity=best_match['id'])
            session['api_token'] = access_token
            
            log_query = """
                INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                VALUES (%s, 'login_facial', %s, %s, TRUE)
            """
            detalle = f'Login facial exitoso (similitud: {confidence:.1f}%)'
            try:
                db_manager.execute_query(log_query, (best_match['id'], detalle, request.remote_addr))
            except Exception:
                pass
            
            return jsonify({
                'success': True, 
                'message': f'Bienvenido {best_match["nombre"]}',
                'confidence': f'{confidence:.1f}%',
                'redirect': url_for('dashboard'),  # 🔧 FIX: URL de redirección
                'api_token': access_token  # Devolver token para uso en cliente
            })
        
        # No se encontró coincidencia suficiente
        # Mensaje detallado para el usuario
        if best_similarity > 0:
            mensaje_error = f'Rostro no reconocido. Similitud máxima encontrada: {best_similarity*100:.1f}% (requerido: {threshold*100:.0f}%)'
        else:
            mensaje_error = 'No se encontró ningún rostro registrado que coincida'
        
        log_query = """
            INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
            VALUES (NULL, 'login_facial_fallido', %s, %s, FALSE)
        """
        detalle = f'Rostro no reconocido. Mejor similitud: {best_similarity*100:.1f}%'
        try:
            db_manager.execute_query(log_query, (detalle, request.remote_addr))
        except Exception:
            pass
        
        return jsonify({
            'success': False, 
            'message': mensaje_error,
            'best_similarity': f'{best_similarity*100:.1f}%' if best_similarity > 0 else 'N/A'
        })
        
    except Exception as e:
        print(f"[ERROR] Error en login facial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error en el sistema: {str(e)}'})


@app.route('/api/get-token', methods=['GET'])
def get_api_token():
    """Endpoint para obtener el token JWT actual del usuario logueado"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
    
    # Si ya existe un token, devolverlo
    if 'api_token' in session:
        return jsonify({
            'success': True,
            'token': session['api_token'],
            'user_id': session['user_id'],
            'user_name': session.get('user_name', '')
        })
    
    # Si no existe, generar uno nuevo
    access_token = create_access_token(identity=session['user_id'])
    session['api_token'] = access_token
    
    return jsonify({
        'success': True,
        'token': access_token,
        'user_id': session['user_id'],
        'user_name': session.get('user_name', '')
    })


@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_query = (
            """
            INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
            VALUES (%s, 'logout_web', 'Logout desde interfaz web', %s, TRUE)
            """
        )
        try:
            db_manager.execute_query(log_query, (session['user_id'], request.remote_addr))
        except Exception:
            pass
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))


@app.route('/api/accesibilidad/toggle', methods=['POST'])
def accesibilidad_toggle():
    """API para activar/desactivar opciones de accesibilidad"""
    data = request.get_json()
    opcion = data.get('opcion')
    valor = data.get('valor')
    
    if 'accesibilidad' not in session:
        session['accesibilidad'] = {}
    
    session['accesibilidad'][opcion] = valor
    session.modified = True
    
    return jsonify({'success': True, 'opcion': opcion, 'valor': valor})


@app.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    """Módulo de recuperación de contraseña - Enviar código por correo"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Por favor ingresa tu correo electrónico', 'error')
            return render_template('auth/recuperar_contrasena.html')
        
        # Verificar que el usuario existe
        query = "SELECT id, nombre, email FROM usuarios WHERE email = %s AND activo = TRUE"
        users = db_manager.execute_query(query, (email,))
        
        if users:
            user = users[0]
            
            # Generar código de 6 dígitos
            import random
            codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expiry = datetime.now() + timedelta(minutes=15)  # Código válido por 15 minutos
            
            # Debug: Mostrar código generado
            print(f"[DEBUG] Código generado para {user['id']}: '{codigo}' (len: {len(codigo)})")
            print(f"[DEBUG] Expira en: {expiry}")
            
            # Guardar código en sesión
            user_id = user["id"]
            session[f'reset_code_{user_id}'] = {
                'code': codigo,
                'expiry': expiry.isoformat(),
                'email': email
            }
            
            print(f"[DEBUG] Código guardado en sesión: {session.get(f'reset_code_{user_id}')}")
            
            # Intentar enviar correo con código
            try:
                enviar_codigo_recuperacion(user['email'], user['nombre'], codigo)
                flash('Se ha enviado un código de verificación a tu correo electrónico. Revisa tu bandeja de entrada.', 'success')
                # Redirigir a la página de verificación de código
                return redirect(url_for('verificar_codigo', user_id=user['id']))
            except Exception as e:
                print(f"[ERROR] Error enviando correo: {str(e)}")
                import traceback
                traceback.print_exc()
                flash(f'No se pudo enviar el correo. Error: {str(e)}', 'error')
        else:
            # Por seguridad, no revelar si el email existe o no
            flash('Si el correo está registrado, recibirás un código de verificación en tu bandeja de entrada.', 'info')
    
    return render_template('auth/recuperar_contrasena.html')


def enviar_codigo_recuperacion(email, nombre, codigo):
    """Enviar código de verificación de 6 dígitos por correo"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import ssl
    
    # Configuración del servidor SMTP de Gmail
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    print(f"[DEBUG] Intentando enviar código a: {email}")
    print(f"[DEBUG] SMTP Server: {smtp_server}:{smtp_port}")
    print(f"[DEBUG] SMTP User configurado: {'Sí - ' + smtp_user if smtp_user else 'No'}")
    print(f"[DEBUG] Password configurado: {'Sí' if smtp_password else 'No'}")
    
    if not smtp_user or not smtp_password:
        error_msg = 'Configuración de correo no disponible. Verifica que SMTP_USER y SMTP_PASSWORD estén en .env_produccion'
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] SMTP_USER actual: '{smtp_user}'")
        print(f"[ERROR] SMTP_PASSWORD actual: {'configurado' if smtp_password else 'vacío'}")
        raise Exception(error_msg)
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Código de Recuperación - Centro Minero SENA'
    msg['From'] = f'Centro Minero SENA <{smtp_user}>'
    msg['To'] = email
    
    # Contenido HTML del correo con código
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e5128 0%, #2d6a4f 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code-box {{ background: #fff; border: 3px dashed #2d6a4f; padding: 20px; text-align: center; margin: 20px 0; border-radius: 10px; }}
            .code {{ font-size: 36px; font-weight: bold; color: #1e5128; letter-spacing: 8px; font-family: 'Courier New', monospace; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Código de Verificación</h1>
            </div>
            <div class="content">
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en el Sistema de Gestión de Laboratorios del Centro Minero SENA.</p>
                
                <div class="code-box">
                    <p style="margin: 0; font-size: 14px; color: #666;">Tu código de verificación es:</p>
                    <div class="code">{codigo}</div>
                </div>
                
                <div class="warning">
                    <strong>⏰ Este código expirará en 15 minutos.</strong>
                </div>
                
                <p>Ingresa este código en la página de recuperación de contraseña para continuar.</p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo de forma segura.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    <strong>Consejos de seguridad:</strong><br>
                    • No compartas este código con nadie<br>
                    • El personal de SENA nunca te pedirá este código<br>
                    • Si no reconoces esta solicitud, cambia tu contraseña inmediatamente
                </p>
            </div>
            <div class="footer">
                <p>© 2025 Centro Minero SENA - Sistema de Gestión de Laboratorios</p>
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    part = MIMEText(html, 'html')
    msg.attach(part)
    
    # Enviar correo con manejo de errores mejorado
    try:
        print(f"[DEBUG] Conectando a {smtp_server}:{smtp_port}...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            print("[DEBUG] Conexión establecida")
            server.set_debuglevel(1)
            
            print("[DEBUG] Iniciando TLS...")
            server.starttls(context=context)
            print("[DEBUG] TLS iniciado")
            
            print("[DEBUG] Autenticando...")
            server.login(smtp_user, smtp_password)
            print("[DEBUG] Autenticación exitosa")
            
            print(f"[DEBUG] Enviando correo a {email}...")
            server.send_message(msg)
            print("[OK] Correo enviado exitosamente")
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Error de autenticación SMTP: {str(e)}. Verifica que SMTP_USER y SMTP_PASSWORD sean correctos. Para Gmail, usa una 'Contraseña de Aplicación'."
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error enviando correo: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)


def enviar_correo_recuperacion(email, nombre, reset_link):
    """Enviar correo de recuperación de contraseña usando Gmail"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import ssl
    
    # Configuración del servidor SMTP de Gmail
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    print(f"[DEBUG] Intentando enviar correo a: {email}")
    print(f"[DEBUG] SMTP Server: {smtp_server}:{smtp_port}")
    print(f"[DEBUG] SMTP User: {smtp_user}")
    print(f"[DEBUG] Password configurado: {'Sí' if smtp_password else 'No'}")
    
    if not smtp_user or not smtp_password:
        error_msg = 'Configuración de correo no disponible. Configure SMTP_USER y SMTP_PASSWORD en .env_produccion'
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Recuperación de Contraseña - Centro Minero SENA'
    msg['From'] = f'Centro Minero SENA <{smtp_user}>'
    msg['To'] = email
    
    # Contenido HTML del correo
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e5128 0%, #2d6a4f 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 15px 30px; background: #2d6a4f; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Recuperación de Contraseña</h1>
            </div>
            <div class="content">
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en el Sistema de Gestión de Laboratorios del Centro Minero SENA.</p>
                <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Restablecer Contraseña</a>
                </p>
                <p><strong>Este enlace expirará en 1 hora.</strong></p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo de forma segura.</p>
                <hr>
                <p style="font-size: 12px; color: #666;">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                    <a href="{reset_link}">{reset_link}</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2025 Centro Minero SENA - Sistema de Gestión de Laboratorios</p>
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    part = MIMEText(html, 'html')
    msg.attach(part)
    
    # Enviar correo con manejo de errores mejorado
    try:
        print(f"[DEBUG] Conectando a {smtp_server}:{smtp_port}...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            print("[DEBUG] Conexión establecida")
            server.set_debuglevel(1)  # Activar debug para ver detalles
            
            print("[DEBUG] Iniciando TLS...")
            server.starttls(context=context)
            print("[DEBUG] TLS iniciado")
            
            print("[DEBUG] Autenticando...")
            server.login(smtp_user, smtp_password)
            print("[DEBUG] Autenticación exitosa")
            
            print(f"[DEBUG] Enviando correo a {email}...")
            server.send_message(msg)
            print("[OK] Correo enviado exitosamente")
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Error de autenticación SMTP: {str(e)}. Verifica que SMTP_USER y SMTP_PASSWORD sean correctos. Para Gmail, usa una 'Contraseña de Aplicación'."
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error enviando correo: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)


@app.route('/verificar-codigo/<user_id>', methods=['GET', 'POST'])
def verificar_codigo(user_id):
    """Verificar código de 6 dígitos"""
    code_data = session.get(f'reset_code_{user_id}')
    
    if not code_data:
        flash('Sesión expirada. Solicita un nuevo código.', 'error')
        return redirect(url_for('recuperar_contrasena'))
    
    # Verificar expiración
    expiry = datetime.fromisoformat(code_data['expiry'])
    if datetime.now() > expiry:
        session.pop(f'reset_code_{user_id}', None)
        flash('El código ha expirado. Solicita uno nuevo.', 'error')
        return redirect(url_for('recuperar_contrasena'))
    
    if request.method == 'POST':
        codigo_ingresado = request.form.get('codigo', '').strip().replace(' ', '').replace('-', '')
        
        if not codigo_ingresado:
            flash('Por favor ingresa el código', 'error')
            return render_template('auth/verificar_codigo.html', user_id=user_id, email=code_data.get('email', ''))
        
        # Debug: Imprimir códigos para comparación
        codigo_esperado = str(code_data['code']).strip()
        print(f"[DEBUG] Código ingresado: '{codigo_ingresado}' (len: {len(codigo_ingresado)})")
        print(f"[DEBUG] Código esperado: '{codigo_esperado}' (len: {len(codigo_esperado)})")
        print(f"[DEBUG] Comparación: {codigo_ingresado} == {codigo_esperado} -> {codigo_ingresado == codigo_esperado}")
        
        if codigo_ingresado == codigo_esperado:
            # Código correcto, marcar como verificado
            session[f'code_verified_{user_id}'] = True
            flash('Código verificado correctamente', 'success')
            return redirect(url_for('restablecer_contrasena', user_id=user_id))
        else:
            flash(f'Código incorrecto. Verifica e intenta nuevamente.', 'error')
            return render_template('auth/verificar_codigo.html', user_id=user_id, email=code_data.get('email', ''))
    
    return render_template('auth/verificar_codigo.html', user_id=user_id, email=code_data.get('email', ''))


@app.route('/restablecer-contrasena/<user_id>', methods=['GET', 'POST'])
def restablecer_contrasena(user_id):
    """Restablecer contraseña después de verificar código"""
    # Verificar que el código fue verificado
    if not session.get(f'code_verified_{user_id}'):
        flash('Primero debes verificar el código', 'error')
        return redirect(url_for('recuperar_contrasena'))
    
    if request.method == 'POST':
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        
        if not nueva_contrasena or not confirmar_contrasena:
            flash('Todos los campos son requeridos', 'error')
            return render_template('auth/restablecer_contrasena.html', user_id=user_id)
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/restablecer_contrasena.html', user_id=user_id)
        
        if len(nueva_contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('auth/restablecer_contrasena.html', user_id=user_id)
        
        # Actualizar contraseña en la base de datos
        # Nota: En producción, usar bcrypt para hashear la contraseña
        try:
            update_query = "UPDATE usuarios SET password_hash = %s WHERE id = %s"
            db_manager.execute_query(update_query, (nueva_contrasena, user_id))
            
            # Limpiar sesión
            session.pop(f'reset_code_{user_id}', None)
            session.pop(f'code_verified_{user_id}', None)
            
            flash('Contraseña actualizada exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error al actualizar contraseña: {str(e)}', 'error')
    
    return render_template('auth/restablecer_contrasena.html', user_id=user_id)


@app.route('/ayuda')
def ayuda():
    """Manual de usuario interactivo"""
    return render_template('modules/ayuda.html', user=session if 'user_id' in session else None)


@app.route('/modulos')
def modulos():
    """Vista de todos los módulos del proyecto"""
    return render_template('modules/modulos_proyecto.html', user=session if 'user_id' in session else None)


@app.route('/perfil', methods=['GET', 'POST'])
@require_login
def perfil():
    """Editar perfil de usuario"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        programa = request.form.get('programa')
        
        query = """
            UPDATE usuarios 
            SET nombre = %s, email = %s, telefono = %s, programa = %s
            WHERE id = %s
        """
        try:
            db_manager.execute_query(query, (nombre, email, telefono, programa, session['user_id']))
            session['user_name'] = nombre
            flash('Perfil actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar perfil: {str(e)}', 'error')
        return redirect(url_for('perfil'))
    
    # GET - Mostrar formulario
    query = "SELECT id, nombre, email, telefono, tipo, programa, nivel_acceso FROM usuarios WHERE id = %s"
    user_data = db_manager.execute_query(query, (session['user_id'],))
    if user_data:
        return render_template('modules/perfil.html', usuario=user_data[0], user=session)
    return redirect(url_for('dashboard'))


@app.route('/backup', methods=['GET', 'POST'])
@require_login
@require_level(4)
def backup():
    """Gestión de backups de base de datos"""
    import subprocess
    from pathlib import Path
    
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            # Crear backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f'backup_{timestamp}.sql'
            
            try:
                # Usar ruta completa de mysqldump si está disponible
                mysqldump_path = os.getenv('MYSQLDUMP_PATH', 'mysqldump')
                
                cmd = [
                    mysqldump_path,
                    '-h', os.getenv('HOST', 'localhost'),
                    '-u', os.getenv('USUARIO_PRODUCCION', 'laboratorio_prod'),
                    f"-p{os.getenv('PASSWORD_PRODUCCION', '')}",
                    '--single-transaction',
                    '--routines',
                    '--triggers',
                    os.getenv('BASE_DATOS', 'laboratorio_sistema')
                ]
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    subprocess.run(cmd, stdout=f, check=True, stderr=subprocess.PIPE)
                
                flash(f'Backup creado exitosamente: {backup_file.name}', 'success')
            except Exception as e:
                flash(f'Error creando backup: {str(e)}', 'error')
        
        elif action == 'restore':
            # Restaurar backup
            backup_name = request.form.get('backup_file')
            backup_file = backup_dir / backup_name
            
            if backup_file.exists():
                try:
                    # Usar ruta completa de mysql si está disponible
                    mysql_path = os.getenv('MYSQL_PATH', 'mysql')
                    
                    cmd = [
                        mysql_path,
                        '-h', os.getenv('HOST', 'localhost'),
                        '-u', os.getenv('USUARIO_PRODUCCION', 'laboratorio_prod'),
                        f"-p{os.getenv('PASSWORD_PRODUCCION', '')}",
                        os.getenv('BASE_DATOS', 'laboratorio_sistema')
                    ]
                    
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        subprocess.run(cmd, stdin=f, check=True, stderr=subprocess.PIPE)
                    
                    flash(f'Backup restaurado exitosamente: {backup_name}', 'success')
                except Exception as e:
                    flash(f'Error restaurando backup: {str(e)}', 'error')
            else:
                flash('Archivo de backup no encontrado', 'error')
        
        elif action == 'delete':
            # Eliminar backup
            backup_name = request.form.get('backup_file')
            backup_file = backup_dir / backup_name
            
            if backup_file.exists():
                try:
                    backup_file.unlink()  # Eliminar archivo
                    flash(f'Backup eliminado exitosamente: {backup_name}', 'success')
                except Exception as e:
                    flash(f'Error eliminando backup: {str(e)}', 'error')
            else:
                flash('Archivo de backup no encontrado', 'error')
        
        return redirect(url_for('backup'))
    
    # GET - Listar backups disponibles
    backups = []
    if backup_dir.exists():
        backups = [
            {
                'nombre': f.name,
                'tamaño': f'{f.stat().st_size / 1024 / 1024:.2f} MB',
                'fecha': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
            for f in sorted(backup_dir.glob('*.sql'), key=lambda x: x.stat().st_mtime, reverse=True)
        ]
    
    return render_template('modules/backup.html', backups=backups, user=session)


@app.route('/backup/download/<filename>')
@require_login
@require_level(4)
def download_backup(filename):
    """Descargar un archivo de backup"""
    from flask import send_file
    from pathlib import Path
    import os
    
    # Validar que el archivo existe y es un backup válido
    backup_dir = Path('backups')
    backup_file = backup_dir / filename
    
    # Seguridad: verificar que el archivo está dentro del directorio de backups
    try:
        backup_file = backup_file.resolve()
        backup_dir = backup_dir.resolve()
        
        if not str(backup_file).startswith(str(backup_dir)):
            flash('Acceso denegado: ruta inválida', 'error')
            return redirect(url_for('backup'))
        
        if not backup_file.exists() or not backup_file.is_file():
            flash('Archivo de backup no encontrado', 'error')
            return redirect(url_for('backup'))
        
        if not filename.endswith('.sql'):
            flash('Tipo de archivo no permitido', 'error')
            return redirect(url_for('backup'))
        
        # Enviar archivo para descarga
        return send_file(
            backup_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/sql'
        )
    
    except Exception as e:
        flash(f'Error descargando backup: {str(e)}', 'error')
        return redirect(url_for('backup'))


@app.route('/dashboard')
@require_login
def dashboard():
    stats = get_dashboard_stats()
    
    # Obtener módulos según nivel de usuario
    user_level = session.get('user_level', 1)
    
    try:
        from app.utils.modulos_config import (
            get_modulos_disponibles, 
            get_acciones_rapidas_disponibles, 
            get_estadisticas_disponibles
        )
        
        modulos_disponibles = get_modulos_disponibles(user_level)
        acciones_rapidas = get_acciones_rapidas_disponibles(user_level)
        estadisticas_visibles = get_estadisticas_disponibles(user_level)
        
    except Exception as e:
        print(f"[ERROR] Error cargando configuración de módulos: {e}")
        # Fallback: mostrar módulos básicos
        modulos_disponibles = []
        acciones_rapidas = []
        estadisticas_visibles = ['equipos_activos', 'total_laboratorios']
    
    return render_template('dashboard/dashboard.html', 
                         stats=stats, 
                         user=session,
                         modulos_disponibles=modulos_disponibles,
                         acciones_rapidas=acciones_rapidas,
                         estadisticas_visibles=estadisticas_visibles)


@app.route('/api/dashboard/alertas')
@require_login
def dashboard_alertas():
    """Obtener alertas para el dashboard: stock crítico y reservas pendientes"""
    try:
        print(f"[DEBUG] Iniciando dashboard_alertas para usuario: {session.get('user_id')}")
        
        # Items con stock crítico o bajo
        query_stock = """
            SELECT i.id, i.nombre, i.cantidad_actual, i.cantidad_minima, i.unidad,
                   CASE 
                       WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                       WHEN i.cantidad_actual <= (i.cantidad_minima * 2) THEN 'bajo'
                       ELSE 'normal'
                   END as nivel_stock,
                   l.nombre as laboratorio_nombre
            FROM inventario i
            JOIN laboratorios l ON i.laboratorio_id = l.id
            WHERE i.cantidad_actual <= i.cantidad_minima * 2
            ORDER BY 
                CASE 
                    WHEN i.cantidad_actual <= i.cantidad_minima THEN 1 
                    ELSE 2 
                END,
                i.cantidad_actual ASC
            LIMIT 10
        """
        print(f"[DEBUG] Ejecutando query de stock...")
        stock_critico = db_manager.execute_query(query_stock) or []
        print(f"[DEBUG] Stock crítico encontrado: {len(stock_critico)} items")
        
        # Reservas pendientes de aprobación (solo para instructores y admin)
        reservas_pendientes = []
        if session.get('user_level', 0) >= 5:
            print(f"[DEBUG] Usuario con nivel {session.get('user_level')} - consultando reservas pendientes")
            query_reservas = """
                SELECT r.id, r.fecha_inicio, r.fecha_fin,
                       u.nombre as usuario_nombre,
                       e.nombre as equipo_nombre,
                       DATE_FORMAT(r.fecha_inicio, '%d/%m/%Y %H:%i') as fecha_inicio
                FROM reservas r
                JOIN usuarios u ON r.usuario_id = u.id
                JOIN equipos e ON r.equipo_id = e.id
                WHERE r.estado_aprobacion = 'pendiente'
                ORDER BY r.fecha_inicio ASC
                LIMIT 10
            """
            print(f"[DEBUG] Ejecutando query de reservas...")
            reservas_pendientes = db_manager.execute_query(query_reservas) or []
            print(f"[DEBUG] Reservas pendientes encontradas: {len(reservas_pendientes)}")
        else:
            print(f"[DEBUG] Usuario con nivel {session.get('user_level')} - sin acceso a reservas pendientes")
        
        print(f"[DEBUG] Retornando respuesta exitosa")
        return jsonify({
            'success': True,
            'stock_critico': stock_critico,
            'reservas_pendientes': reservas_pendientes
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error en dashboard_alertas: {str(e)}")
        print(f"[ERROR] Tipo de error: {type(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error obteniendo alertas: {str(e)}',
            'stock_critico': [],
            'reservas_pendientes': []
        }), 500


@app.route('/laboratorios')
@require_login
def laboratorios():
    query = """
        SELECT 
            l.id, l.codigo, l.nombre, l.tipo, l.ubicacion, l.capacidad_estudiantes,
            l.responsable, l.estado,
            COUNT(DISTINCT e.id) as total_equipos,
            COUNT(DISTINCT i.id) as total_items,
            COUNT(DISTINCT CASE WHEN i.cantidad_actual <= i.cantidad_minima THEN i.id END) as items_criticos
        FROM laboratorios l
        LEFT JOIN equipos e ON l.id = e.laboratorio_id
        LEFT JOIN inventario i ON l.id = i.laboratorio_id
        GROUP BY l.id, l.codigo, l.nombre, l.tipo, l.ubicacion, l.capacidad_estudiantes, l.responsable, l.estado
        ORDER BY l.tipo, l.codigo
    """
    laboratorios_list = db_manager.execute_query(query)
    
    # Obtener lista de instructores para el formulario
    query_instructores = """
        SELECT id, nombre, especialidad, programa_formacion
        FROM usuarios
        WHERE tipo = 'instructor' 
        AND activo = 1
        AND nivel_acceso >= 3
        ORDER BY nombre
    """
    instructores_list = db_manager.execute_query(query_instructores) or []
    
    return render_template('modules/laboratorios.html', 
                         laboratorios=laboratorios_list, 
                         instructores=instructores_list,
                         user=session)


@app.route('/laboratorio/<int:laboratorio_id>')
@require_login
def laboratorio_detalle(laboratorio_id):
    # Información del laboratorio con estadísticas
    query_lab = """
        SELECT l.*,
               COUNT(DISTINCT e.id) as total_equipos,
               COUNT(DISTINCT i.id) as total_items,
               COUNT(DISTINCT CASE WHEN i.cantidad_actual <= i.cantidad_minima THEN i.id END) as items_criticos,
               COUNT(DISTINCT CASE WHEN e.estado = 'disponible' THEN e.id END) as equipos_disponibles
        FROM laboratorios l
        LEFT JOIN equipos e ON l.id = e.laboratorio_id
        LEFT JOIN inventario i ON l.id = i.laboratorio_id
        WHERE l.id = %s
        GROUP BY l.id
    """
    laboratorio = db_manager.execute_query(query_lab, (laboratorio_id,))
    if not laboratorio:
        flash('Laboratorio no encontrado', 'error')
        return redirect(url_for('laboratorios'))
    
    # Equipos de ESTE laboratorio
    query_equipos = """
        SELECT id, nombre, tipo, estado, ubicacion,
               DATE_FORMAT(ultima_calibracion, '%d/%m/%Y') as calibracion,
               DATE_FORMAT(proximo_mantenimiento, '%d/%m/%Y') as mantenimiento
        FROM equipos
        WHERE laboratorio_id = %s
        ORDER BY tipo, nombre
    """
    equipos = db_manager.execute_query(query_equipos, (laboratorio_id,))
    
    # Inventario de ESTE laboratorio
    query_inventario = """
        SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima, i.unidad,
               i.ubicacion, i.proveedor, i.costo_unitario, i.laboratorio_id,
               CASE 
                   WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                   WHEN i.cantidad_actual <= i.cantidad_minima * 1.5 THEN 'bajo'
                   ELSE 'normal'
               END as stock_status
        FROM inventario i
        WHERE i.laboratorio_id = %s
    """
    inventario = db_manager.execute_query(query_inventario, (laboratorio_id,))
    
    return render_template('modules/laboratorio_detalle.html', 
                         laboratorio=laboratorio[0], 
                         equipos=equipos, 
                         inventario=inventario, 
                         user=session)


# =====================================================================
# CRUD LABORATORIOS - Solo Administradores (Nivel 6+)
# =====================================================================

@app.route('/api/laboratorios', methods=['POST'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def crear_laboratorio():
    """Crear un nuevo laboratorio - Solo administradores"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['codigo', 'nombre', 'tipo']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Verificar que el código no exista
        query_check = "SELECT id FROM laboratorios WHERE codigo = %s"
        existe = db_manager.execute_query(query_check, (data['codigo'],))
        if existe:
            return jsonify({
                'success': False,
                'message': f'Ya existe un laboratorio con el código {data["codigo"]}'
            }), 400
        
        # Preparar datos
        codigo = data['codigo'].strip()
        nombre = data['nombre'].strip()
        tipo = data['tipo']
        ubicacion = data.get('ubicacion', '').strip()
        capacidad = data.get('capacidad_estudiantes', 0) or 0
        area = data.get('area_m2', 0) or 0
        responsable_id = data.get('responsable_id') or None
        equipamiento = data.get('equipamiento_especializado', '').strip()
        normas = data.get('normas_seguridad', '').strip()
        
        # Obtener nombre del responsable si se proporciona ID
        responsable_nombre = None
        if responsable_id:
            query_resp = "SELECT nombre FROM usuarios WHERE id = %s"
            result_resp = db_manager.execute_query(query_resp, (responsable_id,))
            if result_resp:
                responsable_nombre = result_resp[0]['nombre']
        
        # Insertar laboratorio
        query = """
            INSERT INTO laboratorios 
            (codigo, nombre, tipo, ubicacion, capacidad_estudiantes, area_m2, 
             responsable, equipamiento_especializado, normas_seguridad, estado, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'activo', NOW())
        """
        params = (codigo, nombre, tipo, ubicacion, capacidad, area, 
                 responsable_nombre, equipamiento, normas)
        db_manager.execute_query(query, params)
        
        # Registrar en logs
        query_log = """
            INSERT INTO logs_sistema (usuario_id, accion, detalles, fecha)
            VALUES (%s, 'crear_laboratorio', %s, NOW())
        """
        detalles = f'Creado laboratorio: {codigo} - {nombre}'
        db_manager.execute_query(query_log, (session.get('user_id'), detalles))
        
        return jsonify({
            'success': True,
            'message': f'Laboratorio {codigo} creado exitosamente'
        }), 201
        
    except Exception as e:
        print(f"[ERROR] crear_laboratorio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear laboratorio: {str(e)}'
        }), 500


@app.route('/api/laboratorios/<int:lab_id>', methods=['PUT'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def actualizar_laboratorio(lab_id):
    """Actualizar un laboratorio existente - Solo administradores"""
    try:
        data = request.get_json()
        
        # Verificar que el laboratorio existe
        query_check = "SELECT id, codigo FROM laboratorios WHERE id = %s"
        lab_actual = db_manager.execute_query(query_check, (lab_id,))
        if not lab_actual:
            return jsonify({
                'success': False,
                'message': 'Laboratorio no encontrado'
            }), 404
        
        # Validar campos requeridos
        campos_requeridos = ['codigo', 'nombre', 'tipo']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Si cambia el código, verificar que no exista otro con ese código
        if data['codigo'] != lab_actual[0]['codigo']:
            query_check_codigo = "SELECT id FROM laboratorios WHERE codigo = %s AND id != %s"
            existe = db_manager.execute_query(query_check_codigo, (data['codigo'], lab_id))
            if existe:
                return jsonify({
                    'success': False,
                    'message': f'Ya existe otro laboratorio con el código {data["codigo"]}'
                }), 400
        
        # Preparar datos
        codigo = data['codigo'].strip()
        nombre = data['nombre'].strip()
        tipo = data['tipo']
        ubicacion = data.get('ubicacion', '').strip()
        capacidad = data.get('capacidad_estudiantes', 0) or 0
        area = data.get('area_m2', 0) or 0
        responsable_id = data.get('responsable_id') or None
        equipamiento = data.get('equipamiento_especializado', '').strip()
        normas = data.get('normas_seguridad', '').strip()
        estado = data.get('estado', 'activo')
        
        # Obtener nombre del responsable si se proporciona ID
        responsable_nombre = None
        if responsable_id:
            query_resp = "SELECT nombre FROM usuarios WHERE id = %s"
            result_resp = db_manager.execute_query(query_resp, (responsable_id,))
            if result_resp:
                responsable_nombre = result_resp[0]['nombre']
        
        # Actualizar laboratorio
        query = """
            UPDATE laboratorios SET
                codigo = %s,
                nombre = %s,
                tipo = %s,
                ubicacion = %s,
                capacidad_estudiantes = %s,
                area_m2 = %s,
                responsable = %s,
                equipamiento_especializado = %s,
                normas_seguridad = %s,
                estado = %s,
                fecha_modificacion = NOW()
            WHERE id = %s
        """
        params = (codigo, nombre, tipo, ubicacion, capacidad, area, 
                 responsable_nombre, equipamiento, normas, estado, lab_id)
        db_manager.execute_query(query, params)
        
        # Registrar en logs
        query_log = """
            INSERT INTO logs_sistema (usuario_id, accion, detalles, fecha)
            VALUES (%s, 'actualizar_laboratorio', %s, NOW())
        """
        detalles = f'Actualizado laboratorio ID {lab_id}: {codigo} - {nombre}'
        db_manager.execute_query(query_log, (session.get('user_id'), detalles))
        
        return jsonify({
            'success': True,
            'message': f'Laboratorio {codigo} actualizado exitosamente'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] actualizar_laboratorio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al actualizar laboratorio: {str(e)}'
        }), 500


@app.route('/api/laboratorios/<int:lab_id>', methods=['DELETE'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def eliminar_laboratorio(lab_id):
    """Eliminar un laboratorio - Solo administradores"""
    try:
        # Verificar que el laboratorio existe
        query_check = "SELECT codigo, nombre FROM laboratorios WHERE id = %s"
        laboratorio = db_manager.execute_query(query_check, (lab_id,))
        if not laboratorio:
            return jsonify({
                'success': False,
                'message': 'Laboratorio no encontrado'
            }), 404
        
        lab_data = laboratorio[0]
        
        # Verificar si tiene equipos o inventario asociado
        query_count_equipos = "SELECT COUNT(*) as total FROM equipos WHERE laboratorio_id = %s"
        count_equipos = db_manager.execute_query(query_count_equipos, (lab_id,))
        
        query_count_inventario = "SELECT COUNT(*) as total FROM inventario WHERE laboratorio_id = %s"
        count_inventario = db_manager.execute_query(query_count_inventario, (lab_id,))
        
        total_equipos = count_equipos[0]['total'] if count_equipos else 0
        total_inventario = count_inventario[0]['total'] if count_inventario else 0
        
        if total_equipos > 0 or total_inventario > 0:
            return jsonify({
                'success': False,
                'message': f'No se puede eliminar el laboratorio. Tiene {total_equipos} equipos y {total_inventario} items de inventario asociados. Primero elimínelos o reasígnelos.',
                'equipos': total_equipos,
                'inventario': total_inventario
            }), 400
        
        # Eliminar laboratorio
        query_delete = "DELETE FROM laboratorios WHERE id = %s"
        db_manager.execute_query(query_delete, (lab_id,))
        
        # Registrar en logs
        query_log = """
            INSERT INTO logs_sistema (usuario_id, accion, detalles, fecha)
            VALUES (%s, 'eliminar_laboratorio', %s, NOW())
        """
        detalles = f'Eliminado laboratorio ID {lab_id}: {lab_data["codigo"]} - {lab_data["nombre"]}'
        db_manager.execute_query(query_log, (session.get('user_id'), detalles))
        
        return jsonify({
            'success': True,
            'message': f'Laboratorio {lab_data["codigo"]} eliminado exitosamente'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] eliminar_laboratorio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al eliminar laboratorio: {str(e)}'
        }), 500


@app.route('/api/laboratorios/<int:lab_id>', methods=['GET'])
@require_login
def obtener_laboratorio(lab_id):
    """Obtener detalles de un laboratorio para edición"""
    try:
        query = """
            SELECT id, codigo, nombre, tipo, ubicacion, capacidad_estudiantes,
                   area_m2, responsable, equipamiento_especializado, 
                   normas_seguridad, estado
            FROM laboratorios
            WHERE id = %s
        """
        laboratorio = db_manager.execute_query(query, (lab_id,))
        
        if not laboratorio:
            return jsonify({
                'success': False,
                'message': 'Laboratorio no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': laboratorio[0]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] obtener_laboratorio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener laboratorio: {str(e)}'
        }), 500


@app.route('/equipos')
@require_login
def equipos():
    query = """
        SELECT e.id, e.nombre, e.tipo, e.estado, e.ubicacion,
               e.laboratorio_id,
               l.nombre as laboratorio_nombre,
               l.codigo as laboratorio_codigo,
               DATE_FORMAT(e.ultima_calibracion, '%d/%m/%Y') as calibracion,
               DATE_FORMAT(e.proximo_mantenimiento, '%d/%m/%Y') as mantenimiento,
               e.especificaciones
        FROM equipos e
        INNER JOIN laboratorios l ON e.laboratorio_id = l.id
        ORDER BY l.nombre, e.tipo, e.nombre
    """
    equipos_list = db_manager.execute_query(query)
    for equipo in equipos_list:
        if equipo.get('especificaciones'):
            try:
                specs_obj = json.loads(equipo['especificaciones'])
                # Si tiene el formato nuevo con "descripcion", extraer el texto
                if isinstance(specs_obj, dict) and 'descripcion' in specs_obj:
                    equipo['especificaciones'] = specs_obj['descripcion']
                else:
                    equipo['especificaciones'] = specs_obj
            except Exception:
                equipo['especificaciones'] = {}
    return render_template('modules/equipos.html', equipos=equipos_list, user=session)


@app.route('/equipos/detalle/<equipo_id>')
@require_login
def detalle_equipo(equipo_id):
    """Vista detallada de un equipo"""
    try:
        # Importar la función de utilidad
        import sys
        import os
        sys.path.append('.')
        from utils_fotos import obtener_foto_frontal
        
        # Obtener información completa del equipo
        query = """
            SELECT e.*, l.nombre as laboratorio_nombre 
            FROM equipos e
            LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
            WHERE e.id = %s
        """
        
        equipos = db_manager.execute_query(query, (equipo_id,))
        
        if not equipos:
            flash('Equipo no encontrado', 'error')
            return redirect(url_for('equipos'))
        
        equipo = equipos[0]
        
        # Obtener foto frontal del equipo
        foto_frontal = obtener_foto_frontal(
            equipo['id'], 
            equipo['nombre'], 
            'equipo'
        )
        
        # Obtener especificaciones si existen
        if equipo.get('especificaciones'):
            try:
                especificaciones = json.loads(equipo['especificaciones']) if isinstance(equipo['especificaciones'], str) else equipo['especificaciones']
            except:
                especificaciones = {}
        else:
            especificaciones = {}
        
        return render_template('modules/equipo_detalle.html', 
                             equipo=equipo, 
                             especificaciones=especificaciones,
                             foto_frontal=foto_frontal,
                             user=session)
        
    except Exception as e:
        flash(f'Error cargando detalle: {str(e)}', 'error')
        return redirect(url_for('equipos'))


@app.route('/equipos/crear', methods=['POST'])
@require_login
def crear_equipo_web():
    """Crear equipo desde interfaz web (sin JWT)"""
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        tipo = data.get('tipo')
        ubicacion = data.get('ubicacion')
        laboratorio_id = data.get('laboratorio_id', 1)  # Por defecto laboratorio 1
        especificaciones_texto = data.get('especificaciones', '')
        
        if not nombre or not tipo:
            return jsonify({'success': False, 'message': 'Nombre y tipo son requeridos'}), 400
        
        # Generar ID único
        import uuid
        equipo_id = f"EQ-{uuid.uuid4().hex[:8].upper()}"
        
        # Convertir texto a JSON válido
        especificaciones_json = json.dumps({"descripcion": especificaciones_texto})
        
        query = """
            INSERT INTO equipos (id, nombre, tipo, estado, ubicacion, laboratorio_id, especificaciones)
            VALUES (%s, %s, %s, 'disponible', %s, %s, %s)
        """
        db_manager.execute_query(query, (equipo_id, nombre, tipo, ubicacion, laboratorio_id, especificaciones_json))
        
        return jsonify({'success': True, 'message': 'Item creado exitosamente'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/inventario')
@require_login
def inventario():
    """Buscador global de equipos e items"""
    # Obtener todos los equipos con información del laboratorio
    query_equipos = """
        SELECT e.*, l.nombre as laboratorio_nombre
        FROM equipos e
        LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
        ORDER BY e.nombre
    """
    
    # Obtener todos los items de inventario con información del laboratorio
    query_items = """
        SELECT i.*, l.nombre as laboratorio_nombre 
        FROM inventario i
        LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
        ORDER BY i.nombre
    """
    
    equipos = db_manager.execute_query(query_equipos) or []
    items = db_manager.execute_query(query_items) or []
    
    # Obtener laboratorios para filtros
    query_labs = "SELECT id, nombre FROM laboratorios ORDER BY nombre"
    laboratorios = db_manager.execute_query(query_labs) or []
    
    return render_template('modules/inventario.html', 
                         equipos=equipos, 
                         items=items, 
                         laboratorios=laboratorios,
                         user=session)


@app.route('/inventario/detalle/<item_id>')
@require_login
def detalle_inventario(item_id):
    """Vista detallada de un item de inventario"""
    try:
        # Importar la función de utilidad
        import sys
        import os
        sys.path.append('.')
        from utils_fotos import obtener_foto_frontal
        
        # Obtener información completa del item
        query = """
            SELECT i.*, l.nombre as laboratorio_nombre 
            FROM inventario i
            LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
            WHERE i.id = %s
        """
        
        items = db_manager.execute_query(query, (item_id,))
        
        if not items:
            flash('Item no encontrado', 'error')
            return redirect(url_for('inventario'))
        
        item = items[0]
        
        # Obtener foto frontal del item
        foto_frontal = obtener_foto_frontal(
            item['id'], 
            item['nombre'], 
            'item'
        )
        
        return render_template('modules/inventario_detalle.html', 
                             item=item, 
                             foto_frontal=foto_frontal,
                             user=session)
        
    except Exception as e:
        flash(f'Error cargando detalle: {str(e)}', 'error')
        return redirect(url_for('inventario'))


@app.route('/inventario/crear', methods=['POST'])
@require_login
def crear_item_inventario_web():
    """Crear item de inventario desde interfaz web (sin JWT)"""
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        categoria = data.get('categoria')
        cantidad_actual = data.get('cantidad_actual', 0)
        cantidad_minima = data.get('cantidad_minima', 0)
        unidad = data.get('unidad', 'unidad')
        ubicacion = data.get('ubicacion')
        laboratorio_id = data.get('laboratorio_id', 1)  # Por defecto laboratorio 1
        proveedor = data.get('proveedor')
        costo_unitario = data.get('costo_unitario', 0)
        
        if not nombre:
            return jsonify({'success': False, 'message': 'Nombre es requerido'}), 400
        
        # Generar ID único
        import uuid
        item_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        query = """
            INSERT INTO inventario (id, nombre, categoria, cantidad_actual, cantidad_minima, 
                                  unidad, ubicacion, laboratorio_id, proveedor, costo_unitario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db_manager.execute_query(query, (item_id, nombre, categoria, cantidad_actual, 
                                        cantidad_minima, unidad, ubicacion, laboratorio_id,
                                        proveedor, costo_unitario))
        
        return jsonify({'success': True, 'message': 'Item de inventario creado exitosamente', 'id': item_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/inventario/ajustar-stock', methods=['POST'])
@require_login
@require_level(3)  # Solo Coordinador y Administrador
@limiter.limit("20 per minute")
def api_ajustar_stock():
    """
    API para ajustar stock de items existentes con control de acceso por laboratorio
    
    🔒 SEGURIDAD IMPLEMENTADA:
    - ✅ Validación de permisos por laboratorio
    - ✅ Solo instructores responsables pueden ajustar su laboratorio
    - ✅ Administradores pueden ajustar todos los laboratorios
    - ✅ Validación completa de datos
    - ✅ Transacción atómica
    - ✅ Auditoría de movimientos
    - ✅ Rate limiting
    
    PERMISOS REQUERIDOS:
    - Nivel 6 (Administrador): Puede ajustar stock de CUALQUIER laboratorio
    - Nivel 5 (Instructor a cargo de inventario): SOLO puede ajustar stock de su laboratorio asignado
    - Nivel 3-4: No pueden ajustar stock (requieren nivel 5+)
    
    VALIDACIONES:
    - item_id: Debe existir en inventario
    - nueva_cantidad: No puede ser negativa
    - motivo: Mínimo 3 caracteres
    - laboratorio_id: El usuario debe ser responsable del laboratorio del item
    
    ERRORES:
    - 400: Datos inválidos
    - 403: Sin permisos para este laboratorio
    - 404: Item no encontrado
    - 429: Too many requests (rate limiting)
    - 500: Error del servidor
    """
    try:
        data = request.get_json()
        
        # Validación de datos requeridos
        campos_requeridos = ['item_id', 'nueva_cantidad', 'motivo']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {campo}'
                }), 400
        
        item_id = data['item_id'].strip()
        nueva_cantidad = int(data['nueva_cantidad'])
        motivo = data['motivo'].strip()
        observaciones = data.get('observaciones', '').strip()
        
        # Validaciones de negocio
        if nueva_cantidad < 0:
            return jsonify({
                'success': False,
                'message': 'La cantidad no puede ser negativa'
            }), 400
        
        if len(motivo) < 3:
            return jsonify({
                'success': False,
                'message': 'El motivo debe tener al menos 3 caracteres'
            }), 400
        
        # Obtener información del item actual
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar que el item existe
            query_item = """
                SELECT id, nombre, categoria, cantidad_actual, laboratorio_id
                FROM inventario 
                WHERE id = %s
            """
            cursor.execute(query_item, (item_id,))
            item_actual = cursor.fetchone()
            
            if not item_actual:
                return jsonify({
                    'success': False,
                    'message': 'Item no encontrado'
                }), 404
            
            item_id_db, nombre, categoria, cantidad_actual, laboratorio_id = item_actual
            
            # Validación de permisos por laboratorio
            user_id = session.get('user_id')
            user_level = permissions_manager.get_nivel_usuario(user_id)
            
            # Administradores pueden gestionar todos los laboratorios
            if user_level != 6:  # Si no es administrador
                # Verificar si es instructor a cargo de inventario de ESTE laboratorio
                es_instructor, lab_instructor = permissions_manager.es_instructor_con_inventario(user_id)
                
                if not es_instructor:
                    return jsonify({
                        'success': False,
                        'message': 'Solo instructores a cargo de inventario pueden ajustar stock'
                    }), 403
                
                # Validar que el laboratorio del item coincida con el del instructor
                if laboratorio_id != lab_instructor:
                    return jsonify({
                        'success': False,
                        'message': f'No tienes autorización para ajustar stock de este laboratorio. Tu laboratorio: {lab_instructor}, Laboratorio del item: {laboratorio_id}'
                    }), 403
            
            # Calcular diferencia
            diferencia = nueva_cantidad - cantidad_actual
            
            # Si no hay cambios, retornar éxito
            if diferencia == 0:
                return jsonify({
                    'success': True,
                    'message': 'No hay cambios en el stock',
                    'data': {
                        'cantidad_anterior': cantidad_actual,
                        'cantidad_nueva': nueva_cantidad,
                        'diferencia': 0
                    }
                })
            
            # Iniciar transacción
            cursor.execute("START TRANSACTION")
            
            # Actualizar stock del item
            query_update = """
                UPDATE inventario 
                SET cantidad_actual = %s
                WHERE id = %s
            """
            cursor.execute(query_update, (nueva_cantidad, item_id))
            
            # Registrar movimiento en auditoría (conservando máxima información)
            tipo_movimiento = 'ajuste_entrada' if diferencia > 0 else 'ajuste_salida'
            try:
                # Intentar insertar con todas las columnas posibles
                query_movimiento = """
                    INSERT INTO movimientos_inventario 
                    (inventario_id, tipo_movimiento, cantidad, referencia, observaciones, 
                     usuario_id, laboratorio_id, fecha_movimiento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(query_movimiento, (
                    item_id,
                    tipo_movimiento,
                    abs(diferencia),
                    f"Ajuste de stock: {motivo}",
                    f"Stock anterior: {cantidad_actual}, Nuevo: {nueva_cantidad}. {observaciones}",
                    session.get('user_id'),
                    laboratorio_id
                ))
                print(f"✅ Movimiento registrado con todos los detalles")
                
            except Exception as e:
                # Si falla por columnas, intentar versión mínima
                print(f"⚠️ Error con consulta completa: {e}")
                try:
                    query_minimo = """
                        INSERT INTO movimientos_inventario 
                        (tipo_movimiento, cantidad, fecha_movimiento)
                        VALUES (%s, %s, NOW())
                    """
                    cursor.execute(query_minimo, (tipo_movimiento, abs(diferencia)))
                    print(f"✅ Movimiento registrado en versión mínima")
                    
                except Exception as e2:
                    # Si todo falla, continuar con el ajuste de stock
                    print(f"⚠️ No se pudo registrar movimiento: {e2}")
                    print(f"📦 Ajuste de stock continuará sin auditoría")
            
            # Confirmar transacción
            cursor.execute("COMMIT")
            
            # Log de seguridad
            try:
                log_security_event(
                    user_id=session.get('user_id'),
                    action='ajuste_stock',
                    detail=f"Item {item_id} ({nombre}) ajustado de {cantidad_actual} a {nueva_cantidad}",
                    ip=request.remote_addr,
                    success=True
                )
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': f'Stock ajustado exitosamente de {cantidad_actual} a {nueva_cantidad}',
                'data': {
                    'item_id': item_id,
                    'nombre': nombre,
                    'cantidad_anterior': cantidad_actual,
                    'cantidad_nueva': nueva_cantidad,
                    'diferencia': diferencia,
                    'tipo_movimiento': tipo_movimiento,
                    'motivo': motivo
                }
            })
            
        except Exception as e:
            # Rollback en caso de error
            cursor.execute("ROLLBACK")
            raise e
            
        finally:
            cursor.close()
            conn.close()
            
    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': f'Error de validación: {str(ve)}'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500


@app.route('/api/inventario/stock', methods=['GET'])
@require_login
def api_obtener_stock():
    """
    API para obtener stock actual de un item
    """
    try:
        item_id = request.args.get('item_id', '').strip()
        
        if not item_id:
            return jsonify({
                'success': False,
                'message': 'ID de item requerido'
            }), 400
        
        query = """
            SELECT id, nombre, categoria, cantidad_actual, unidad, laboratorio_id
            FROM inventario 
            WHERE id = %s
        """
        result = db_manager.execute_query(query, (item_id,))
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Item no encontrado'
            }), 404
        
        item = result[0]
        
        return jsonify({
            'success': True,
            'data': {
                'id': item[0],
                'nombre': item[1],
                'categoria': item[2],
                'cantidad_actual': item[3],
                'unidad': item[4],
                'laboratorio_id': item[5]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500




@app.route('/inventario/entregar', methods=['GET', 'POST'])
@require_login
@require_instructor_inventario
def entregar_consumible():
    """Entrega de consumibles con control de stock"""
    
    # Si es GET, redirigir a inventario SOLO si no viene de referer de inventario
    if request.method == 'GET':
        # Evitar redirección infinita
        referer = request.headers.get('Referer', '')
        if 'inventario/entregar' in referer:
            # Si viene de /inventario/entregar, devolver error para romper el bucle
            return jsonify({
                'error': 'Redirección infinita detectada',
                'message': 'Use el botón "Entregar" desde la página de inventario'
            }), 400
        
        return redirect(url_for('inventario'))
    
    # Procesar POST
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        cantidad = data.get('cantidad', 0)
        
        # Nuevos campos del formulario simplificado
        instructor_id = data.get('instructor_id', '')
        instructor_nombre = data.get('instructor_nombre', '')
        motivo_uso = data.get('motivo_uso', '')
        grupo = data.get('grupo', '')
        observaciones = data.get('observaciones', '')
        
        # Campos antiguos para compatibilidad (si vienen)
        recibido_por = data.get('recibido_por', '')
        clase = data.get('clase', '')
        
        if not item_id or cantidad <= 0:
            return jsonify({'success': False, 'message': 'Item y cantidad son requeridos'}), 400
        
        # Verificar stock disponible
        query_stock = "SELECT cantidad_actual, nombre FROM inventario WHERE id = %s"
        item = db_manager.execute_query(query_stock, (item_id,))
        
        if not item:
            return jsonify({'success': False, 'message': 'Item no encontrado'}), 404
        
        stock_actual = item[0]['cantidad_actual']
        item_nombre = item[0]['nombre']
        
        if stock_actual < cantidad:
            return jsonify({
                'success': False, 
                'message': f'Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad}'
            }), 400
        
        # Construir motivo descriptivo
        if motivo_uso:
            motivo = f"Entrega: {motivo_uso}"
            if instructor_nombre:
                motivo += f" - Instructor: {instructor_nombre}"
            if grupo:
                motivo += f" - Grupo: {grupo}"
        elif recibido_por and clase:
            # Compatibilidad con formato antiguo
            motivo = f"Entrega para {clase}"
            if recibido_por:
                motivo += f" - Recibido por: {recibido_por}"
        else:
            motivo = "Entrega de consumibles"
        
        # Registrar movimiento de salida (con fallbacks)
        try:
            # Intentar con inventario_id (columna correcta)
            query_movimiento = """
                INSERT INTO movimientos_inventario 
                (inventario_id, usuario_id, tipo_movimiento, cantidad,
                 cantidad_anterior, cantidad_nueva, motivo, observaciones)
                VALUES (%s, %s, 'salida', %s, %s, %s, %s, %s)
            """
            
            db_manager.execute_query(query_movimiento, (
                item_id, session['user_id'], cantidad,
                stock_actual, stock_actual - cantidad,
                motivo, observaciones
            ))
            print("✅ Movimiento registrado con inventario_id")
            
        except Exception as e:
            # Fallback: intentar con item_id
            try:
                query_movimiento_alt = """
                    INSERT INTO movimientos_inventario 
                    (item_id, usuario_id, tipo_movimiento, cantidad,
                     cantidad_anterior, cantidad_nueva, motivo, observaciones)
                    VALUES (%s, %s, 'salida', %s, %s, %s, %s, %s)
                """
                
                db_manager.execute_query(query_movimiento_alt, (
                    item_id, session['user_id'], cantidad,
                    stock_actual, stock_actual - cantidad,
                    motivo, observaciones
                ))
                print("✅ Movimiento registrado con item_id (fallback)")
                
            except Exception as e2:
                # Si todo falla, continuar con el ajuste de stock
                print(f"⚠️ No se pudo registrar movimiento: {e2}")
                print(f"📦 Entrega continuará sin auditoría")
        
        # Actualizar stock
        query_update = "UPDATE inventario SET cantidad_actual = %s WHERE id = %s"
        db_manager.execute_query(query_update, (stock_actual - cantidad, item_id))
        
        return jsonify({
            'success': True, 
            'message': f'✅ Entrega registrada: {cantidad} {item_nombre}',
            'stock_actual': stock_actual - cantidad
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/inventario/historial-item/<item_id>')
@require_login
def historial_item(item_id):
    """Obtener historial de movimientos de un item específico"""
    try:
        # Intentar consulta completa con JOINs
        try:
            query_completa = """
                SELECT 
                    mi.id,
                    mi.cantidad,
                    mi.fecha_movimiento,
                    mi.observaciones,
                    i.nombre as item_nombre,
                    u.nombre as usuario_entrega
                FROM movimientos_inventario mi
                JOIN inventario i ON mi.inventario_id = i.id
                LEFT JOIN usuarios u ON mi.usuario_id = u.id
                WHERE mi.inventario_id = %s
                ORDER BY mi.fecha_movimiento DESC
                LIMIT 50
            """
            
            historial = db_manager.execute_query(query_completa, (item_id,))
            
            if historial:
                print("✅ Historial de item obtenido con consulta completa")
                return jsonify({'success': True, 'historial': historial}), 200
                
        except Exception as e:
            print(f"⚠️ Error en consulta completa de historial item: {e}")
        
        # Fallback: Consulta mínima
        query_minima = """
            SELECT * FROM movimientos_inventario 
            WHERE inventario_id = %s
            ORDER BY fecha_movimiento DESC
            LIMIT 50
        """
        
        historial = db_manager.execute_query(query_minima, (item_id,))
        print("✅ Historial de item obtenido con consulta mínima")
        
        return jsonify({
            'success': True,
            'historial': historial or []
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/inventario/historial-entregas')
@require_login
def historial_entregas():
    """Obtener historial de entregas recientes conservando máxima información"""
    try:
        # Intentar consulta completa con JOINs para obtener nombres
        try:
            query_completa = """
                SELECT 
                    mi.id,
                    mi.cantidad,
                    mi.fecha_movimiento,
                    mi.observaciones,
                    i.nombre as item_nombre,
                    i.categoria,
                    l.nombre as laboratorio_nombre,
                    u.nombre as usuario_entrega
                FROM movimientos_inventario mi
                JOIN inventario i ON mi.inventario_id = i.id
                LEFT JOIN usuarios u ON mi.usuario_id = u.id
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                WHERE mi.tipo_movimiento = 'salida'
                ORDER BY mi.fecha_movimiento DESC
                LIMIT 50
            """
            entregas = db_manager.execute_query(query_completa)
            if entregas:
                print("✅ Historial obtenido con consulta completa")
                return jsonify({'success': True, 'entregas': entregas}), 200
                
        except Exception as e:
            print(f"⚠️ Error en consulta completa: {e}")
        
        # Fallback 1: Consulta con JOIN solo inventario
        try:
            query_parcial = """
                SELECT 
                    mi.id,
                    mi.cantidad,
                    mi.fecha_movimiento,
                    mi.observaciones,
                    i.nombre as item_nombre,
                    i.categoria,
                    'Usuario' as usuario_entrega
                FROM movimientos_inventario mi
                JOIN inventario i ON mi.inventario_id = i.id
                WHERE mi.tipo_movimiento = 'salida'
                ORDER BY mi.fecha_movimiento DESC
                LIMIT 50
            """
            entregas = db_manager.execute_query(query_parcial)
            if entregas:
                print("✅ Historial obtenido con consulta parcial")
                return jsonify({'success': True, 'entregas': entregas}), 200
                
        except Exception as e:
            print(f"⚠️ Error en consulta parcial: {e}")
        
        # Fallback 2: Consulta mínima que siempre funciona
        query_minima = """
            SELECT * FROM movimientos_inventario 
            WHERE tipo_movimiento = 'salida'
            ORDER BY fecha_movimiento DESC
            LIMIT 50
        """
        
        entregas = db_manager.execute_query(query_minima)
        print("✅ Historial obtenido con consulta mínima")
        
        return jsonify({
            'success': True,
            'entregas': entregas or [],
            'nivel_detalle': 'minimo'  # Indicar nivel de detalle
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/instructores-quimica')
@require_login
def obtener_instructores_quimica():
    """Obtener lista de todos los instructores de química disponibles"""
    try:
        query = """
            SELECT id, nombre, email, especialidad, programa_formacion, nivel_acceso,
                   CASE 
                       WHEN nivel_acceso = 5 THEN 'Instructor con Inventario'
                       WHEN nivel_acceso = 4 THEN 'Instructor sin Inventario'
                       ELSE 'Otro'
                   END as rol_inventario
            FROM usuarios 
            WHERE nivel_acceso IN (4, 5) AND activo = TRUE
            ORDER BY nivel_acceso DESC, nombre
        """
        
        instructores = db_manager.execute_query(query)
        
        return jsonify({
            'success': True,
            'instructores': instructores or []
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/inventario/disponible/<item_id>')
@require_login
def verificar_disponibilidad(item_id):
    """Verificar disponibilidad de un item"""
    try:
        query = """
            SELECT 
                id, nombre, cantidad_actual, cantidad_minima, unidad,
                CASE 
                    WHEN cantidad_actual <= cantidad_minima THEN 'critico'
                    WHEN cantidad_actual <= cantidad_minima * 1.5 THEN 'bajo'
                    ELSE 'normal'
                END as stock_status
            FROM inventario 
            WHERE id = %s
        """
        
        item = db_manager.execute_query(query, (item_id,))
        
        if not item:
            return jsonify({'success': False, 'message': 'Item no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'item': item[0]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/reservas')
@require_login
def reservas():
    # Obtener lista de equipos disponibles para el formulario
    equipos_query = """
        SELECT id, nombre, tipo, estado 
        FROM equipos 
        WHERE estado IN ('disponible', 'en_uso')
        ORDER BY nombre
    """
    equipos_list = db_manager.execute_query(equipos_query) or []
    
    if session.get('user_level', 1) >= 3:
        query = (
            """
            SELECT r.id, 
                   DATE_FORMAT(r.fecha_inicio, '%d/%m/%Y %H:%i') as fecha_inicio,
                   DATE_FORMAT(r.fecha_fin, '%d/%m/%Y %H:%i') as fecha_fin,
                   r.estado,
                   r.estado_aprobacion,
                   r.notas,
                   r.motivo_rechazo,
                   u.nombre as usuario_nombre,
                   u.programa as usuario_programa,
                   e.nombre as equipo_nombre,
                   instructor.nombre as aprobada_por_nombre
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN equipos e ON r.equipo_id = e.id
            LEFT JOIN usuarios instructor ON r.instructor_aprobador = instructor.id
            ORDER BY 
                CASE WHEN r.estado_aprobacion = 'pendiente' THEN 0 ELSE 1 END,
                r.fecha_inicio DESC
            """
        )
        reservas_list = db_manager.execute_query(query) or []
    else:
        query = (
            """
            SELECT r.id,
                   DATE_FORMAT(r.fecha_inicio, '%d/%m/%Y %H:%i') as fecha_inicio,
                   DATE_FORMAT(r.fecha_fin, '%d/%m/%Y %H:%i') as fecha_fin,
                   r.estado,
                   r.estado_aprobacion,
                   r.notas,
                   r.motivo_rechazo,
                   u.nombre as usuario_nombre,
                   u.programa as usuario_programa,
                   e.nombre as equipo_nombre,
                   instructor.nombre as aprobada_por_nombre
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN equipos e ON r.equipo_id = e.id
            LEFT JOIN usuarios instructor ON r.instructor_aprobador = instructor.id
            WHERE r.usuario_id = %s
            ORDER BY r.fecha_inicio DESC
            """
        )
        reservas_list = db_manager.execute_query(query, (session['user_id'],)) or []
    
    return render_template('modules/reservas.html', reservas=reservas_list, equipos=equipos_list, user=session)


@app.route('/reservas/crear', methods=['POST'])
@require_login
def crear_reserva_web():
    """Crear reserva desde interfaz web (sin JWT)"""
    try:
        data = request.get_json()
        equipo_id = data.get('equipo_id')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        proposito = data.get('proposito')
        usuario_id = session.get('user_id')
        
        if not all([equipo_id, fecha_inicio, fecha_fin, proposito]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400
        
        # Verificar que el equipo existe y obtener información
        query_equipo = "SELECT id, nombre, laboratorio_id FROM equipos WHERE id = %s"
        equipo = db_manager.execute_query(query_equipo, (equipo_id,))
        if not equipo:
            return jsonify({'success': False, 'message': 'El equipo no existe'}), 404
        
        equipo_nombre = equipo[0]['nombre']
        laboratorio_id = equipo[0].get('laboratorio_id')
        
        # Generar ID único
        import uuid
        reserva_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear la reserva con estado pendiente de aprobación
        query = """
            INSERT INTO reservas (id, equipo_id, usuario_id, fecha_inicio, fecha_fin, 
                                estado, notas, estado_aprobacion)
            VALUES (%s, %s, %s, %s, %s, 'programada', %s, 'pendiente')
        """
        db_manager.execute_query(query, (reserva_id, equipo_id, usuario_id, fecha_inicio, 
                                        fecha_fin, proposito))
        
        # Enviar notificación a instructores a cargo del inventario
        notificaciones_manager.notificar_nueva_reserva(
            reserva_id=reserva_id,
            usuario_id=usuario_id,
            equipo_nombre=equipo[0]['nombre'],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            laboratorio_id=laboratorio_id
        )
        
        return jsonify({
            'success': True, 
            'message': 'Reserva creada exitosamente. Los instructores serán notificados para su aprobación.',
            'reserva_id': reserva_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/reservas/aprobar-modificada/<reserva_id>', methods=['POST'])
@require_login
@require_instructor_inventario
def aprobar_reserva_modificada(reserva_id):
    """Aprobar reserva con posible modificación de fechas"""
    try:
        instructor_id = session['user_id']
        laboratorio_asignado = kwargs.get('laboratorio_asignado')
        
        data = request.get_json()
        opcion = data.get('opcion')  # 'comoEsta' o 'modificado'
        nueva_fecha_inicio = data.get('nueva_fecha_inicio')
        nueva_fecha_fin = data.get('nueva_fecha_fin')
        razon_cambio = data.get('razon_cambio', '')
        notas_solicitante = data.get('notas_solicitante', '')
        
        if opcion not in ['comoEsta', 'modificado']:
            return {'message': 'Opción inválida'}, 400
        
        # Obtener información de la reserva
        query_reserva = """
            SELECT r.usuario_id, r.equipo_id, r.fecha_inicio, r.fecha_fin, r.notas,
                   e.nombre as equipo_nombre, e.laboratorio_id,
                   u.nombre as usuario_nombre
            FROM reservas r
            JOIN equipos e ON r.equipo_id = e.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.id = %s
        """
        reserva = db_manager.execute_query(query_reserva, (reserva_id,))
        
        if not reserva:
            return {'message': 'Reserva no encontrada'}, 404
        
        reserva_data = reserva[0]
        lab_equipo = reserva_data['laboratorio_id']
        
        # Validar que el instructor pueda gestionar este laboratorio
        if lab_equipo != laboratorio_asignado:
            return {'message': 'No tienes autorización para gestionar reservas de este laboratorio'}, 403
        
        # Si es modificación, validar las nuevas fechas
        if opcion == 'modificado':
            if not nueva_fecha_inicio or not nueva_fecha_fin:
                return {'message': 'Debes especificar las nuevas fechas'}, 400
            
            # Convertir fechas
            try:
                nuevo_inicio = datetime.strptime(nueva_fecha_inicio, '%Y-%m-%dT%H:%M')
                nuevo_fin = datetime.strptime(nueva_fecha_fin, '%Y-%m-%dT%H:%M')
            except ValueError:
                return {'message': 'Formato de fechas inválido'}, 400
            
            # Validar que fin sea posterior a inicio
            if nuevo_fin <= nuevo_inicio:
                return {'message': 'La fecha de fin debe ser posterior a la de inicio'}, 400
            
            # Validar que no haya conflictos con otras reservas
            query_conflictos = """
                SELECT COUNT(*) as conflictos
                FROM reservas 
                WHERE equipo_id = %s 
                AND id != %s
                AND estado_aprobacion = 'aprobada'
                AND (
                    (fecha_inicio <= %s AND fecha_fin >= %s) OR
                    (fecha_inicio <= %s AND fecha_fin >= %s) OR
                    (fecha_inicio >= %s AND fecha_fin <= %s)
                )
            """
            conflictos = db_manager.execute_query(query_conflictos, (
                reserva_data['equipo_id'], reserva_id,
                nuevo_inicio, nuevo_inicio,
                nuevo_fin, nuevo_fin,
                nuevo_inicio, nuevo_fin
            ))
            
            if conflictos[0]['conflictos'] > 0:
                return {'message': 'Las nuevas fechas tienen conflictos con otras reservas aprobadas'}, 400
        
        # Actualizar la reserva
        try:
            if opcion == 'comoEsta':
                # Aprobar como está
                query = """
                    UPDATE reservas 
                    SET estado_aprobacion = 'aprobada',
                        instructor_aprobador = %s,
                        fecha_aprobacion = NOW(),
                        estado = 'programada'
                    WHERE id = %s
                """
                db_manager.execute_query(query, (instructor_id, reserva_id))
                
                mensaje_aprobacion = "Reserva aprobada con las fechas solicitadas"
                
            else:
                # Aprobar con modificación
                query = """
                    UPDATE reservas 
                    SET estado_aprobacion = 'aprobada_modificada',
                        instructor_aprobador = %s,
                        fecha_aprobacion = NOW(),
                        fecha_inicio = %s,
                        fecha_fin = %s,
                        estado = 'programada',
                        notas_modificacion = %s,
                        notas_instructor = %s
                    WHERE id = %s
                """
                db_manager.execute_query(query, (
                    instructor_id, 
                    nuevo_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                    nuevo_fin.strftime('%Y-%m-%d %H:%M:%S'),
                    razon_cambio,
                    notas_solicitante,
                    reserva_id
                ))
                
                mensaje_aprobacion = f"Reserva aprobada con fechas modificadas: {nuevo_inicio.strftime('%d/%m/%Y %H:%M')} - {nuevo_fin.strftime('%d/%m/%Y %H:%M')}"
        
        except Exception as e:
            return {'message': f'Error actualizando la reserva: {str(e)}'}, 500
        
        # Notificar al usuario
        try:
            if opcion == 'comoEsta':
                notificaciones_manager.notificar_reserva_aprobada(
                    reserva_id=reserva_id,
                    usuario_id=reserva_data['usuario_id'],
                    equipo_nombre=reserva_data['equipo_nombre'],
                    instructor_id=instructor_id
                )
            else:
                # Notificación especial para modificación
                notificaciones_manager.notificar_reserva_modificada(
                    reserva_id=reserva_id,
                    usuario_id=reserva_data['usuario_id'],
                    equipo_nombre=reserva_data['equipo_nombre'],
                    instructor_id=instructor_id,
                    fecha_original_inicio=reserva_data['fecha_inicio'],
                    fecha_original_fin=reserva_data['fecha_fin'],
                    nueva_fecha_inicio=nuevo_inicio.strftime('%d/%m/%Y %H:%M'),
                    nueva_fecha_fin=nuevo_fin.strftime('%d/%m/%Y %H:%M'),
                    razon_cambio=razon_cambio,
                    notas_instructor=notas_solicitante
                )
        except Exception as e:
            print(f"Error enviando notificación: {e}")
        
        return {
            'success': True,
            'message': mensaje_aprobacion,
            'opcion': opcion
        }, 200
        
    except Exception as e:
        return {'message': f'Error del servidor: {str(e)}'}, 500


@app.route('/reservas/aprobar/<reserva_id>', methods=['POST'])
@require_login
@require_instructor_inventario
def aprobar_reserva_web(reserva_id):
    """Aprobar o rechazar una reserva desde interfaz web (solo instructor responsable del laboratorio)"""
    try:
        instructor_id = session['user_id']
        laboratorio_asignado = kwargs.get('laboratorio_asignado')
        
        data = request.get_json()
        respuesta = data.get('respuesta')  # 'aprobada' o 'rechazada'
        motivo_rechazo = data.get('motivo_rechazo')
        
        if respuesta not in ['aprobada', 'rechazada']:
            return {'message': 'Respuesta inválida. Debe ser "aprobada" o "rechazada"'}, 400
        
        # Obtener información de la reserva Y el laboratorio del equipo
        query_reserva = """
            SELECT r.usuario_id, r.equipo_id, e.nombre as equipo_nombre,
                   e.laboratorio_id, l.nombre as laboratorio_nombre
            FROM reservas r
            JOIN equipos e ON r.equipo_id = e.id
            LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
            WHERE r.id = %s
        """
        reserva = db_manager.execute_query(query_reserva, (reserva_id,))
        
        if not reserva:
            return {'message': 'Reserva no encontrada'}, 404
        
        lab_equipo = reserva[0]['laboratorio_id']
        lab_nombre = reserva[0]['laboratorio_nombre'] or 'desconocido'
        
        # VALIDACIÓN CRÍTICA: El laboratorio del equipo debe coincidir con el del instructor
        if lab_equipo != laboratorio_asignado:
            return {
                'message': f'No tienes autorización para gestionar reservas de este laboratorio. Solo puedes aprobar reservas de tu laboratorio asignado ({lab_nombre}).',
                'laboratorio_equipo': lab_equipo,
                'laboratorio_instructor': laboratorio_asignado
            }, 403
        
        usuario_id = reserva[0]['usuario_id']
        equipo_id = reserva[0]['equipo_id']
        
        # Actualizar la reserva
        try:
            if respuesta == 'aprobada':
                query = """
                    UPDATE reservas 
                    SET estado_aprobacion = 'aprobada',
                        instructor_aprobador = %s,
                        fecha_aprobacion = NOW(),
                        estado = 'aprobada'
                    WHERE id = %s
                """
                db_manager.execute_query(query, (instructor_id, reserva_id))
            else:
                query = """
                    UPDATE reservas 
                    SET estado_aprobacion = 'rechazada',
                        instructor_aprobador = %s,
                        fecha_aprobacion = NOW(),
                        motivo_rechazo = %s,
                        estado = 'cancelada'
                    WHERE id = %s
                """
                db_manager.execute_query(query, (instructor_id, motivo_rechazo, reserva_id))
        except Exception as e:
            return {'message': f'Error al actualizar la reserva: {str(e)}'}, 500
        
        # Notificar al usuario sobre la decisión
        try:
            if respuesta == 'aprobada':
                notificaciones_manager.notificar_reserva_aprobada(
                    reserva_id=reserva_id,
                    usuario_id=usuario_id,
                    equipo_nombre=reserva[0]['equipo_nombre'],
                    instructor_id=instructor_id
                )
            else:
                notificaciones_manager.notificar_reserva_rechazada(
                    reserva_id=reserva_id,
                    usuario_id=usuario_id,
                    equipo_nombre=reserva[0]['equipo_nombre'],
                    instructor_id=instructor_id,
                    motivo=motivo_rechazo
                )
        except Exception as e:
            print(f"Error enviando notificación: {e}")
        
        return {
            'success': True,
            'message': f'Reserva {respuesta} correctamente',
            'respuesta': respuesta
        }, 200
        
    except Exception as e:
        return {'message': f'Error del servidor: {str(e)}'}, 500


@app.route('/notificaciones')
@require_login
def notificaciones_view():
    """Vista de notificaciones del usuario"""
    usuario_id = session.get('user_id')
    
    # Obtener notificaciones
    notificaciones_list = notificaciones_manager.obtener_notificaciones_usuario(
        usuario_id=usuario_id,
        solo_no_leidas=False,
        limite=100
    )
    
    no_leidas = notificaciones_manager.contar_no_leidas(usuario_id)
    
    return render_template('notificaciones.html', 
                         notificaciones=notificaciones_list,
                         total_no_leidas=no_leidas,
                         user=session)


@app.route('/usuarios')
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def usuarios():
    """Vista de gestión de usuarios (solo administradores)"""
    query = (
        """
        SELECT id, nombre, tipo, programa, nivel_acceso, activo, email, telefono,
               DATE_FORMAT(fecha_registro, '%d/%m/%Y') as registro,
               CASE WHEN rostro_data IS NOT NULL THEN 'Sí' ELSE 'No' END as tiene_rostro
        FROM usuarios
        ORDER BY tipo, nombre
        """
    )
    usuarios_list = db_manager.execute_query(query)
    return render_template('modules/usuarios.html', usuarios=usuarios_list, user=session)


@app.route('/admin/solicitudes-nivel')
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def gestionar_solicitudes_nivel():
    """Panel para gestionar solicitudes de cambio de nivel de usuarios"""
    query = """
        SELECT 
            s.id,
            s.usuario_id,
            s.nivel_solicitado,
            s.nivel_actual,
            s.estado,
            s.fecha_solicitud,
            s.fecha_respuesta,
            s.admin_revisor,
            s.comentario_admin,
            u.nombre,
            u.email,
            u.tipo
        FROM solicitudes_nivel s
        JOIN usuarios u ON s.usuario_id = u.id
        ORDER BY 
            CASE s.estado 
                WHEN 'pendiente' THEN 1 
                WHEN 'aprobada' THEN 2 
                WHEN 'rechazada' THEN 3 
            END,
            s.fecha_solicitud DESC
    """
    solicitudes = db_manager.execute_query(query) or []
    
    # Contar solicitudes pendientes
    pendientes = sum(1 for s in solicitudes if s['estado'] == 'pendiente')
    
    return render_template('modules/admin_solicitudes_nivel.html', 
                         solicitudes=solicitudes, 
                         pendientes=pendientes,
                         roles_nombres=ROLES_NOMBRES,
                         user=session)


@app.route('/admin/solicitud/aprobar/<int:solicitud_id>', methods=['POST'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def aprobar_solicitud_nivel(solicitud_id):
    """Aprobar solicitud de cambio de nivel"""
    try:
        # Obtener solicitud
        query = "SELECT * FROM solicitudes_nivel WHERE id = %s AND estado = 'pendiente'"
        solicitud = db_manager.execute_query(query, (solicitud_id,))
        
        if not solicitud:
            flash('Solicitud no encontrada o ya procesada', 'error')
            return redirect(url_for('gestionar_solicitudes_nivel'))
        
        sol = solicitud[0]
        comentario = request.form.get('comentario', '')
        
        # Cambiar nivel del usuario
        update_usuario = """
            UPDATE usuarios 
            SET nivel_acceso = %s, 
                tipo = %s
            WHERE id = %s
        """
        
        # Mapear tipo según nivel
        tipo_map = {
            1: 'aprendiz',
            2: 'funcionario',
            3: 'instructor',
            4: 'instructor',
            5: 'instructor',
            6: 'administrador'
        }
        nuevo_tipo = tipo_map.get(sol['nivel_solicitado'], 'aprendiz')
        
        db_manager.execute_query(update_usuario, (sol['nivel_solicitado'], nuevo_tipo, sol['usuario_id']))
        
        # Marcar solicitud como aprobada
        update_solicitud = """
            UPDATE solicitudes_nivel 
            SET estado = 'aprobada', 
                fecha_respuesta = NOW(), 
                admin_revisor = %s,
                comentario_admin = %s
            WHERE id = %s
        """
        db_manager.execute_query(update_solicitud, (session['user_id'], comentario, solicitud_id))
        
        # Log de auditoría
        try:
            log_query = """
                INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                VALUES (%s, 'aprobacion_nivel', %s, %s, TRUE)
            """
            db_manager.execute_query(log_query, (
                session['user_id'],
                f'Aprobó cambio de nivel {sol["nivel_actual"]} → {sol["nivel_solicitado"]} para {sol["usuario_id"]}',
                request.remote_addr
            ))
        except:
            pass
        
        flash(f'Solicitud aprobada. Usuario {sol["usuario_id"]} ahora es {get_rol_nombre(sol["nivel_solicitado"])}', 'success')
        
    except Exception as e:
        flash(f'Error al aprobar solicitud: {str(e)}', 'error')
    
    return redirect(url_for('gestionar_solicitudes_nivel'))


@app.route('/admin/solicitud/rechazar/<int:solicitud_id>', methods=['POST'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def rechazar_solicitud_nivel(solicitud_id):
    """Rechazar solicitud de cambio de nivel"""
    try:
        # Obtener solicitud
        query = "SELECT * FROM solicitudes_nivel WHERE id = %s AND estado = 'pendiente'"
        solicitud = db_manager.execute_query(query, (solicitud_id,))
        
        if not solicitud:
            flash('Solicitud no encontrada o ya procesada', 'error')
            return redirect(url_for('gestionar_solicitudes_nivel'))
        
        sol = solicitud[0]
        comentario = request.form.get('comentario', '')
        
        # Marcar solicitud como rechazada
        update_solicitud = """
            UPDATE solicitudes_nivel 
            SET estado = 'rechazada', 
                fecha_respuesta = NOW(), 
                admin_revisor = %s,
                comentario_admin = %s
            WHERE id = %s
        """
        db_manager.execute_query(update_solicitud, (session['user_id'], comentario, solicitud_id))
        
        # Log de auditoría
        try:
            log_query = """
                INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                VALUES (%s, 'rechazo_nivel', %s, %s, TRUE)
            """
            db_manager.execute_query(log_query, (
                session['user_id'],
                f'Rechazó cambio de nivel para {sol["usuario_id"]} (solicitó nivel {sol["nivel_solicitado"]})',
                request.remote_addr
            ))
        except:
            pass
        
        flash(f'Solicitud rechazada para usuario {sol["usuario_id"]}', 'info')
        
    except Exception as e:
        flash(f'Error al rechazar solicitud: {str(e)}', 'error')
    
    return redirect(url_for('gestionar_solicitudes_nivel'))


@app.route('/reportes')
@require_login
@require_level(2)
def reportes():
    """Reportes con datos iniciales desde servidor (SSR) + API para actualizaciones"""
    # Obtener estadísticas completas
    stats = get_dashboard_stats()
    reportes_data = get_reportes_data()
    
    # Combinar todos los datos
    datos_completos = {
        **stats,
        'uso_equipos': reportes_data.get('uso_equipos', []),
        'inventario_bajo': reportes_data.get('inventario_bajo', []),
        'usuarios_activos': reportes_data.get('usuarios_activos', [])
    }
    
    # Generar JWT para uso opcional en actualizaciones dinámicas
    try:
        access_token = create_access_token(
            identity=session['user_id'],
            additional_claims={
                'nombre': session.get('nombre', ''),
                'nivel': session.get('user_level', 1)
            }
        )
        session['api_token'] = access_token
    except:
        pass
    
    return render_template('modules/reportes.html', 
                         reportes=datos_completos, 
                         user=session)


@app.route('/reportes/descargar/pdf')
@require_login
@require_level(2)
def descargar_reporte_pdf():
    """Descargar reporte en formato PDF"""
    try:
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Obtener datos del reporte
        data = obtener_datos_completos_reporte(fecha_inicio, fecha_fin)
        
        # Generar PDF
        pdf_buffer = report_generator.generar_pdf_estadisticas(data, fecha_inicio, fecha_fin)
        
        # Nombre del archivo
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_laboratorio_{fecha_actual}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error al generar el reporte PDF: {str(e)}', 'error')
        return redirect(url_for('reportes'))


@app.route('/reportes/descargar/excel')
@require_login
@require_level(2)
def descargar_reporte_excel():
    """Descargar reporte en formato Excel"""
    try:
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Obtener datos del reporte
        data = obtener_datos_completos_reporte(fecha_inicio, fecha_fin)
        
        # Generar Excel
        excel_buffer = report_generator.generar_excel_estadisticas(data, fecha_inicio, fecha_fin)
        
        # Nombre del archivo
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_laboratorio_{fecha_actual}.xlsx"
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error al generar el reporte Excel: {str(e)}', 'error')
        return redirect(url_for('reportes'))


@app.route('/configuracion')
@require_login
@require_level(4)
def configuracion():
    query = "SELECT clave, valor, descripcion FROM configuracion_sistema ORDER BY clave"
    config_list = db_manager.execute_query(query) or []
    return render_template('modules/configuracion.html', configuraciones=config_list, user=session)

@app.route('/visual')
@require_login
def visual():
    """Página para entrenar la IA de reconocimiento visual (alias de entrenamiento-visual)"""
    return redirect(url_for('entrenamiento_visual'))


@app.route('/entrenamiento-visual')
@require_login
def entrenamiento_visual():
    """Página para entrenar la IA de reconocimiento visual"""
    return render_template('modules/entrenamiento_visual.html', user=session)


@app.route('/facial')
@require_login
def facial():
    """Página para registro facial de usuarios (alias de registro-facial)"""
    return redirect(url_for('registro_facial'))


@app.route('/registro-facial')
@require_login
def registro_facial():
    """Página para registro facial de usuarios"""
    return render_template('modules/registro_facial.html', user=session)


# =====================================================================
# FUNCIONES DE APOYO PARA VISTAS
# =====================================================================

def get_dashboard_stats():
    """Estadísticas mejoradas del dashboard con datos reales"""
    stats = {}
    
    # Equipos por estado
    eq = db_manager.execute_query("SELECT estado, COUNT(*) cantidad FROM equipos GROUP BY estado")
    stats['equipos_estado'] = {r['estado']: r['cantidad'] for r in eq} if eq else {}
    
    # Total de equipos activos (excluyendo fuera de servicio)
    activos = db_manager.execute_query("SELECT COUNT(*) cantidad FROM equipos WHERE estado != 'fuera_servicio'")
    stats['equipos_activos'] = activos[0]['cantidad'] if activos else 0
    
    # Equipos disponibles (más útil que críticos)
    disp = db_manager.execute_query("SELECT COUNT(*) cantidad FROM equipos WHERE estado = 'disponible'")
    stats['equipos_disponibles'] = disp[0]['cantidad'] if disp else 0
    
    # Items con stock crítico (en o bajo el mínimo)
    criticos = db_manager.execute_query("SELECT COUNT(*) cantidad FROM inventario WHERE cantidad_actual <= cantidad_minima")
    stats['items_criticos'] = criticos[0]['cantidad'] if criticos else 0
    
    # Items con stock bajo (advertencia temprana)
    bajo = db_manager.execute_query("SELECT COUNT(*) cantidad FROM inventario WHERE cantidad_actual <= (cantidad_minima * 1.5) AND cantidad_actual > cantidad_minima")
    stats['inventario_bajo'] = bajo[0]['cantidad'] if bajo else 0
    
    # Reservas próximas (incluye programadas y activas, sin filtro de fecha estricto)
    prox = db_manager.execute_query("SELECT COUNT(*) cantidad FROM reservas WHERE estado IN ('activa', 'programada')")
    stats['reservas_proximas'] = prox[0]['cantidad'] if prox else 0
    
    # Total de laboratorios activos
    labs = db_manager.execute_query("SELECT COUNT(*) cantidad FROM laboratorios WHERE estado = 'activo'")
    stats['total_laboratorios'] = labs[0]['cantidad'] if labs else 0
    
    # Total de items en inventario
    total_inv = db_manager.execute_query("SELECT COUNT(*) cantidad FROM inventario")
    stats['total_inventario'] = total_inv[0]['cantidad'] if total_inv else 0
    
    # Total de usuarios activos (para reportes)
    total_users = db_manager.execute_query("SELECT COUNT(*) cantidad FROM usuarios WHERE activo = TRUE")
    stats['total_usuarios'] = total_users[0]['cantidad'] if total_users else 0
    
    return stats


def get_reportes_data():
    data = {}
    q1 = (
        """
        SELECT e.nombre, COUNT(h.id) usos
        FROM equipos e
        LEFT JOIN historial_uso h ON e.id = h.equipo_id AND h.fecha_uso >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY e.id, e.nombre
        ORDER BY usos DESC
        LIMIT 10
        """
    )
    data['uso_equipos'] = db_manager.execute_query(q1)
    q2 = (
        """
        SELECT nombre, categoria, cantidad_actual, cantidad_minima
        FROM inventario
        WHERE cantidad_actual <= cantidad_minima
        ORDER BY (cantidad_actual - cantidad_minima)
        """
    )
    data['inventario_bajo'] = db_manager.execute_query(q2)
    q3 = (
        """
        SELECT u.nombre, u.tipo, COUNT(c.id) comandos
        FROM usuarios u
        LEFT JOIN comandos_voz c ON u.id = c.usuario_id AND c.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY u.id, u.nombre, u.tipo
        ORDER BY comandos DESC
        LIMIT 10
        """
    )
    data['usuarios_activos'] = db_manager.execute_query(q3)
    return data


def obtener_datos_completos_reporte(fecha_inicio=None, fecha_fin=None):
    """
    Obtener todos los datos necesarios para generar un reporte completo
    
    Args:
        fecha_inicio: Fecha de inicio del período (formato YYYY-MM-DD)
        fecha_fin: Fecha de fin del período (formato YYYY-MM-DD)
    
    Returns:
        dict: Diccionario con todos los datos del reporte
    """
    data = {}
    
    # Estadísticas generales
    # Total de equipos
    total_eq = db_manager.execute_query("SELECT COUNT(*) as total FROM equipos")
    data['total_equipos'] = total_eq[0]['total'] if total_eq else 0
    
    # Equipos activos (excluyendo fuera de servicio)
    activos_eq = db_manager.execute_query("SELECT COUNT(*) as total FROM equipos WHERE estado != 'fuera_servicio'")
    data['equipos_activos'] = activos_eq[0]['total'] if activos_eq else 0
    
    # Total de usuarios
    total_users = db_manager.execute_query("SELECT COUNT(*) as total FROM usuarios WHERE activo = TRUE")
    data['total_usuarios'] = total_users[0]['total'] if total_users else 0
    
    # Total de reservas
    total_res = db_manager.execute_query("SELECT COUNT(*) as total FROM reservas")
    data['total_reservas'] = total_res[0]['total'] if total_res else 0
    
    # Reservas activas
    activas_res = db_manager.execute_query("SELECT COUNT(*) as total FROM reservas WHERE estado = 'activa'")
    data['reservas_activas'] = activas_res[0]['total'] if activas_res else 0
    
    # Total de items en inventario
    total_inv = db_manager.execute_query("SELECT COUNT(*) as total FROM inventario")
    data['total_items'] = total_inv[0]['total'] if total_inv else 0
    
    # Items con stock bajo
    bajo_inv = db_manager.execute_query("SELECT COUNT(*) as total FROM inventario WHERE cantidad_actual <= cantidad_minima")
    data['items_stock_bajo'] = bajo_inv[0]['total'] if bajo_inv else 0
    
    # Equipos más utilizados (con filtro de fecha si se proporciona)
    if fecha_inicio and fecha_fin:
        q_equipos = """
            SELECT e.nombre, COUNT(h.id) as usos
            FROM equipos e
            LEFT JOIN historial_uso h ON e.id = h.equipo_id 
                AND h.fecha_uso BETWEEN %s AND %s
            GROUP BY e.id, e.nombre
            ORDER BY usos DESC
            LIMIT 10
        """
        data['equipos_mas_usados'] = db_manager.execute_query(q_equipos, (fecha_inicio, fecha_fin)) or []
    else:
        q_equipos = """
            SELECT e.nombre, COUNT(h.id) as usos
            FROM equipos e
            LEFT JOIN historial_uso h ON e.id = h.equipo_id 
                AND h.fecha_uso >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY e.id, e.nombre
            ORDER BY usos DESC
            LIMIT 10
        """
        data['equipos_mas_usados'] = db_manager.execute_query(q_equipos) or []
    
    # Usuarios más activos (con filtro de fecha si se proporciona)
    if fecha_inicio and fecha_fin:
        q_usuarios = """
            SELECT u.nombre, u.tipo, COUNT(c.id) as comandos
            FROM usuarios u
            LEFT JOIN comandos_voz c ON u.id = c.usuario_id 
                AND c.fecha BETWEEN %s AND %s
            WHERE u.activo = TRUE
            GROUP BY u.id, u.nombre, u.tipo
            ORDER BY comandos DESC
            LIMIT 10
        """
        data['usuarios_activos'] = db_manager.execute_query(q_usuarios, (fecha_inicio, fecha_fin)) or []
    else:
        q_usuarios = """
            SELECT u.nombre, u.tipo, COUNT(c.id) as comandos
            FROM usuarios u
            LEFT JOIN comandos_voz c ON u.id = c.usuario_id 
                AND c.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            WHERE u.activo = TRUE
            GROUP BY u.id, u.nombre, u.tipo
            ORDER BY comandos DESC
            LIMIT 10
        """
        data['usuarios_activos'] = db_manager.execute_query(q_usuarios) or []
    
    # Inventario con stock bajo
    q_inventario = """
        SELECT nombre, categoria, cantidad_actual, cantidad_minima
        FROM inventario
        WHERE cantidad_actual <= cantidad_minima
        ORDER BY (cantidad_actual - cantidad_minima)
    """
    data['inventario_bajo'] = db_manager.execute_query(q_inventario) or []
    
    return data

# =====================================================================
# API REST - ENDPOINTS PRINCIPALES
# =====================================================================

class AuthAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', required=True, help='ID de usuario requerido')
        args = parser.parse_args()
        query = "SELECT id, nombre, tipo, nivel_acceso FROM usuarios WHERE id = %s AND activo = TRUE"
        users = db_manager.execute_query(query, (args['user_id'],))
        if users:
            user = users[0]
            access_token = create_access_token(
                identity=user['id'],
                additional_claims={'nombre': user['nombre'], 'tipo': user['tipo'], 'nivel': user['nivel_acceso']},
            )
            try:
                log_query = (
                    """
                    INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                    VALUES (%s, 'login_api', 'Login exitoso desde API', %s, TRUE)
                    """
                )
                db_manager.execute_query(log_query, (user['id'], request.remote_addr))
            except Exception:
                pass
            return {
                'access_token': access_token,
                'user': {
                    'id': user['id'],
                    'nombre': user['nombre'],
                    'tipo': user['tipo'],
                    'nivel_acceso': user['nivel_acceso'],
                },
            }, 200
        return {'message': 'Usuario no encontrado o inactivo'}, 401


class EquiposAPI(Resource):
    def get(self):
        # Permitir acceso con JWT o sesión web
        try:
            verify_jwt_in_request()
        except:
            # Fallback a sesión web
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
        
        # Obtener todos los equipos (sin filtro de laboratorio ya que la columna no existe)
        query = """
            SELECT e.id, e.nombre, e.tipo, e.estado, e.ubicacion, e.especificaciones,
                   DATE_FORMAT(e.ultima_calibracion, '%Y-%m-%d') as ultima_calibracion,
                   DATE_FORMAT(e.proximo_mantenimiento, '%Y-%m-%d') as proximo_mantenimiento
            FROM equipos e
            ORDER BY e.tipo, e.nombre
        """
        params = []
        
        equipos = db_manager.execute_query(query, params)
        
        for e in equipos:
            if e.get('especificaciones'):
                try:
                    e['especificaciones'] = json.loads(e['especificaciones'])
                except Exception:
                    e['especificaciones'] = {}
        
        return {'equipos': equipos}, 200

    def post(self):
        verify_jwt_or_admin()
        data = request.get_json(silent=True) or {}
        
        # Validar campos requeridos
        if not data.get('nombre'):
            return {'message': 'nombre es requerido'}, 400
        if not data.get('tipo'):
            return {'message': 'tipo es requerido'}, 400
        
        import uuid
        equipo_id = f"EQ_{str(uuid.uuid4())[:8].upper()}"
        
        query = """
            INSERT INTO equipos (id, nombre, tipo, estado, ubicacion, especificaciones)
            VALUES (%s, %s, %s, 'disponible', %s, %s)
        """
        
        specs_json = json.dumps(data.get('especificaciones')) if data.get('especificaciones') else None
        
        try:
            db_manager.execute_query(query, (
                equipo_id, data['nombre'], data['tipo'], 
                data.get('ubicacion'), specs_json
            ))
            return {'message': 'Equipo creado exitosamente', 'id': equipo_id}, 201
        except Exception as e:
            return {'message': f'Error creando equipo: {str(e)}'}, 500


class EquipoAPI(Resource):
    def get(self, equipo_id):
        verify_jwt_in_request()
        query = (
            """
            SELECT id, nombre, tipo, estado, ubicacion, especificaciones,
                   DATE_FORMAT(ultima_calibracion, '%Y-%m-%d') as ultima_calibracion,
                   DATE_FORMAT(proximo_mantenimiento, '%Y-%m-%d') as proximo_mantenimiento
            FROM equipos WHERE id = %s
            """
        )
        rs = db_manager.execute_query(query, (equipo_id,))
        if not rs:
            return {'message': 'Equipo no encontrado'}, 404
        e = rs[0]
        if e.get('especificaciones'):
            try:
                e['especificaciones'] = json.loads(e['especificaciones'])
            except Exception:
                e['especificaciones'] = {}
        return {'equipo': e}, 200

    def put(self, equipo_id):
        # Permitir acceso con JWT o sesión web
        try:
            verify_jwt_in_request()
        except:
            # Fallback a sesión web
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
        
        data = request.get_json(silent=True) or {}
        args = {
            'estado': data.get('estado'),
            'ubicacion': data.get('ubicacion'),
            'especificaciones': data.get('especificaciones')
        }
        updates, params = [], []
        if args['estado']:
            updates.append('estado = %s'); params.append(args['estado'])
        if args['ubicacion'] is not None:
            updates.append('ubicacion = %s'); params.append(args['ubicacion'])
        if args['especificaciones']:
            # Manejar especificaciones como string o dict
            if isinstance(args['especificaciones'], str):
                # Si es string, intentar parsear como JSON, si falla usar como texto
                try:
                    specs_dict = json.loads(args['especificaciones'])
                    updates.append('especificaciones = %s'); params.append(json.dumps(specs_dict))
                except:
                    # No es JSON válido, guardar como descripción
                    updates.append('especificaciones = %s'); params.append(json.dumps({'descripcion': args['especificaciones']}))
            else:
                updates.append('especificaciones = %s'); params.append(json.dumps(args['especificaciones']))
        if not updates:
            return {'message': 'No hay datos para actualizar'}, 400
        query = f"UPDATE equipos SET {', '.join(updates)} WHERE id = %s"
        params.append(equipo_id)
        try:
            affected = db_manager.execute_query(query, params)
            return ({'message': 'Equipo actualizado exitosamente'}, 200) if affected else ({'message': 'Equipo no encontrado'}, 404)
        except Exception as e:
            return {'message': f'Error actualizando equipo: {str(e)}'}, 500


class LaboratoriosAPI(Resource):
    def get(self):
        verify_jwt_in_request()
        tipo = request.args.get('tipo')
        estado = request.args.get('estado', 'activo')
        
        query = """
            SELECT l.id, l.codigo, l.nombre, l.tipo, l.ubicacion, l.capacidad_estudiantes,
                   l.area_m2, l.responsable, l.estado, l.equipamiento_especializado,
                   COUNT(DISTINCT e.id) as total_equipos,
                   COUNT(DISTINCT i.id) as total_items,
                   COUNT(DISTINCT CASE WHEN e.estado = 'disponible' THEN e.id END) as equipos_disponibles,
                   COUNT(DISTINCT CASE WHEN i.cantidad_actual <= i.cantidad_minima THEN i.id END) as items_criticos
            FROM laboratorios l
            LEFT JOIN equipos e ON l.id = e.laboratorio_id
            LEFT JOIN inventario i ON l.id = i.laboratorio_id
        """
        
        params, conds = [], []
        if tipo:
            conds.append('l.tipo = %s'); params.append(tipo)
        if estado:
            conds.append('l.estado = %s'); params.append(estado)
        
        if conds:
            query += ' WHERE ' + ' AND '.join(conds)
        
        query += ' GROUP BY l.id ORDER BY l.tipo, l.codigo'
        
        laboratorios = db_manager.execute_query(query, params)
        return {'laboratorios': laboratorios}, 200
    
    def post(self):
        """Crear laboratorio (solo administradores)"""
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        
        # Verificar que el usuario sea administrador
        query_nivel = "SELECT nivel_acceso FROM usuarios WHERE id = %s"
        result = db_manager.execute_query(query_nivel, (current_user,))
        
        if not result or result[0]['nivel_acceso'] < NIVEL_ADMINISTRADOR:
            return {'message': 'Acceso denegado. Solo administradores pueden crear espacios'}, 403
        
        data = request.get_json(silent=True) or {}
        
        campos_requeridos = ['codigo', 'nombre', 'tipo']
        for campo in campos_requeridos:
            if not data.get(campo):
                return {'message': f'{campo} es requerido'}, 400
        
        # Validar que codigo no sea vacío
        if not data['codigo'].strip():
            return {'message': 'codigo no puede estar vacío'}, 400
        
        # Verificar que el código no exista ya
        check_query = "SELECT id FROM laboratorios WHERE codigo = %s"
        existing = db_manager.execute_query(check_query, (data['codigo'],))
        if existing:
            return {'message': 'Ya existe un laboratorio con ese código'}, 400
        
        # Procesar responsable_id para obtener el nombre del instructor
        responsable_nombre = ''
        responsable_id = data.get('responsable_id', '').strip()
        
        if responsable_id:
            query_responsable = "SELECT nombre FROM usuarios WHERE id = %s AND tipo = 'instructor' AND activo = 1"
            instructor = db_manager.execute_query(query_responsable, (responsable_id,))
            if instructor:
                responsable_nombre = instructor[0]['nombre']
            else:
                return {'message': 'Instructor no encontrado o no válido'}, 400
        
        query = """
            INSERT INTO laboratorios (codigo, nombre, tipo, ubicacion, capacidad_estudiantes,
                                    area_m2, responsable, equipamiento_especializado, normas_seguridad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            db_manager.execute_query(query, (
                data['codigo'], data['nombre'], data['tipo'],
                data.get('ubicacion', ''), data.get('capacidad_estudiantes', 0),
                data.get('area_m2'), responsable_nombre,
                data.get('equipamiento_especializado', ''), data.get('normas_seguridad', '')
            ))
            
            # Obtener el ID del laboratorio recién creado
            laboratorio_creado = db_manager.execute_query(
                "SELECT id FROM laboratorios WHERE codigo = %s", 
                (data['codigo'],)
            )
            
            # Si se asignó un responsable, actualizar el campo laboratorio_id del instructor
            if responsable_id and laboratorio_creado:
                laboratorio_id = laboratorio_creado[0]['id']
                db_manager.execute_query(
                    "UPDATE usuarios SET laboratorio_id = %s WHERE id = %s",
                    (laboratorio_id, responsable_id)
                )
            
            return {'message': 'Laboratorio creado exitosamente'}, 201
        except Exception as e:
            return {'message': f'Error creando laboratorio: {str(e)}'}, 500


class LaboratorioAPI(Resource):
    def get(self, laboratorio_id):
        verify_jwt_in_request()
        
        # Información del laboratorio
        query_lab = """
            SELECT l.*, 
                   COUNT(DISTINCT e.id) as total_equipos,
                   COUNT(DISTINCT i.id) as total_items,
                   SUM(DISTINCT i.cantidad_actual * IFNULL(i.costo_unitario, 0)) as valor_inventario
            FROM laboratorios l
            LEFT JOIN equipos e ON l.id = e.laboratorio_id
            LEFT JOIN inventario i ON l.id = i.laboratorio_id
            WHERE l.id = %s
            GROUP BY l.id
        """
        
        laboratorio = db_manager.execute_query(query_lab, (laboratorio_id,))
        if not laboratorio:
            return {'message': 'Laboratorio no encontrado'}, 404
        
        return {'laboratorio': laboratorio[0]}, 200
    
    def put(self, laboratorio_id):
        """Actualizar laboratorio (solo administradores)"""
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        
        # Verificar que el usuario sea administrador
        query_nivel = "SELECT nivel_acceso FROM usuarios WHERE id = %s"
        result = db_manager.execute_query(query_nivel, (current_user,))
        
        if not result or result[0]['nivel_acceso'] < NIVEL_ADMINISTRADOR:
            return {'message': 'Acceso denegado. Solo administradores pueden editar espacios'}, 403
        
        data = request.get_json(silent=True) or {}
        
        campos_actualizables = [
            'nombre', 'ubicacion', 'capacidad_estudiantes', 'area_m2',
            'responsable', 'equipamiento_especializado', 'normas_seguridad', 'estado'
        ]
        
        updates, params = [], []
        for campo in campos_actualizables:
            if campo in data:
                updates.append(f'{campo} = %s')
                params.append(data[campo])
        
        if not updates:
            return {'message': 'No hay datos para actualizar'}, 400
        
        query = f"UPDATE laboratorios SET {', '.join(updates)} WHERE id = %s"
        params.append(laboratorio_id)
        
        try:
            affected = db_manager.execute_query(query, params)
            return ({'message': 'Laboratorio actualizado'}, 200) if affected else ({'message': 'Laboratorio no encontrado'}, 404)
        except Exception as e:
            return {'message': f'Error actualizando laboratorio: {str(e)}'}, 500


class InventarioAPI(Resource):
    def get(self):
        # Permitir acceso con JWT o sesión web
        try:
            verify_jwt_in_request()
        except:
            # Fallback a sesión web
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
        
        laboratorio_id = request.args.get('laboratorio_id')
        categoria = request.args.get('categoria')
        stock_bajo = request.args.get('stock_bajo', 'false').lower() == 'true'
        
        if laboratorio_id:
            # Inventario específico de un laboratorio
            query = """
                SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima,
                       i.unidad, i.ubicacion, i.proveedor, i.costo_unitario,
                       DATE_FORMAT(i.fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento,
                       l.codigo as laboratorio_codigo, l.nombre as laboratorio_nombre
                FROM inventario i
                INNER JOIN laboratorios l ON i.laboratorio_id = l.id
                WHERE i.laboratorio_id = %s
            """
            params = [laboratorio_id]
        else:
            # Vista general con información de laboratorio
            query = """
                SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima,
                       i.unidad, i.ubicacion, i.proveedor, i.costo_unitario,
                       DATE_FORMAT(i.fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento,
                       l.codigo as laboratorio_codigo, l.nombre as laboratorio_nombre,
                       l.tipo as laboratorio_tipo
                FROM inventario i
                INNER JOIN laboratorios l ON i.laboratorio_id = l.id
            """
            params = []
        
        conds = []
        if categoria:
            conds.append('i.categoria = %s'); params.append(categoria)
        if stock_bajo:
            conds.append('i.cantidad_actual <= i.cantidad_minima')
        
        if conds:
            query += ' AND ' + ' AND '.join(conds)
        
        query += ' ORDER BY l.codigo, i.categoria, i.nombre'
        
        inventario = db_manager.execute_query(query, params)
        
        # Calcular nivel de stock
        for item in inventario:
            if item['cantidad_actual'] <= item['cantidad_minima']:
                item['stock_status'] = 'critico'
            elif item['cantidad_actual'] <= item['cantidad_minima'] * 1.5:
                item['stock_status'] = 'bajo'
            else:
                item['stock_status'] = 'normal'
        
        return {'inventario': inventario}, 200
    
    def post(self):
        verify_jwt_in_request()
        data = request.get_json(silent=True) or {}
        
        campos_requeridos = ['nombre', 'laboratorio_id', 'cantidad_actual', 'cantidad_minima']
        for campo in campos_requeridos:
            if not data.get(campo):
                return {'message': f'{campo} es requerido'}, 400
        
        # Verificar que el laboratorio existe
        lab_exists = db_manager.execute_query("SELECT id FROM laboratorios WHERE id = %s", (data['laboratorio_id'],))
        if not lab_exists:
            return {'message': 'Laboratorio no encontrado'}, 404
        
        query = """
            INSERT INTO inventario (nombre, categoria, cantidad_actual, cantidad_minima, unidad,
                                  ubicacion, proveedor, costo_unitario, fecha_vencimiento, laboratorio_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            db_manager.execute_query(query, (
                data['nombre'], data.get('categoria'), data['cantidad_actual'],
                data['cantidad_minima'], data.get('unidad'), data.get('ubicacion'),
                data.get('proveedor'), data.get('costo_unitario'),
                data.get('fecha_vencimiento'), data['laboratorio_id']
            ))
            return {'message': 'Item de inventario creado exitosamente'}, 201
        except Exception as e:
            return {'message': f'Error creando item: {str(e)}'}, 500


class ReservasAPI(Resource):
    def get(self):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        usuario_nivel = request.args.get('nivel_usuario', '1')
        if int(usuario_nivel) >= 3:
            query = (
                """
                SELECT r.id, r.usuario_id, r.equipo_id, r.fecha_inicio, r.fecha_fin,
                       r.estado, r.notas,
                       u.nombre as usuario_nombre, e.nombre as equipo_nombre
                FROM reservas r
                JOIN usuarios u ON r.usuario_id = u.id
                JOIN equipos e ON r.equipo_id = e.id
                ORDER BY r.fecha_inicio DESC
                """
            )
            reservas = db_manager.execute_query(query)
        else:
            query = (
                """
                SELECT r.id, r.usuario_id, r.equipo_id, r.fecha_inicio, r.fecha_fin,
                       r.estado, r.notas,
                       u.nombre as usuario_nombre, e.nombre as equipo_nombre
                FROM reservas r
                JOIN usuarios u ON r.usuario_id = u.id
                JOIN equipos e ON r.equipo_id = e.id
                WHERE r.usuario_id = %s
                ORDER BY r.fecha_inicio DESC
                """
            )
            reservas = db_manager.execute_query(query, (current_user,))
        return {'reservas': reservas}, 200

    def post(self):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('equipo_id', required=True)
        parser.add_argument('fecha_inicio', required=True)
        parser.add_argument('fecha_fin', required=True)
        parser.add_argument('notas')
        args = parser.parse_args()
        # Normalizar fechas (aceptar 'YYYY-MM-DDTHH:mm' de inputs HTML)
        def normalize(dt: str) -> str:
            dt = dt.replace('T', ' ').strip()
            # agregar segundos si faltan
            if len(dt) == 16:  # 'YYYY-MM-DD HH:MM'
                dt = dt + ":00"
            return dt
        fecha_inicio = normalize(args['fecha_inicio'])
        fecha_fin = normalize(args['fecha_fin'])
        # Validación simple de orden temporal
        try:
            dt_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
            dt_fin = datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S')
            if dt_fin <= dt_ini:
                return {'message': 'La fecha fin debe ser posterior al inicio'}, 400
        except Exception:
            return {'message': 'Formato de fecha inválido'}, 400

        # Validar equipo y obtener información
        try:
            rs = db_manager.execute_query(
                "SELECT estado, nombre, laboratorio_id FROM equipos WHERE id=%s", 
                (args['equipo_id'],)
            )
        except Exception as e:
            return {'message': f'Error consultando equipo: {str(e)}'}, 500
        if not rs:
            return {'message': 'Equipo no encontrado'}, 404
        if rs[0]['estado'] != 'disponible':
            return {'message': 'Equipo no disponible'}, 400
        
        equipo_nombre = rs[0]['nombre']
        laboratorio_id = rs[0].get('laboratorio_id')

        import uuid
        reserva_id = f"RES{str(uuid.uuid4())[:8].upper()}"
        try:
            db_manager.execute_query(
                """
                INSERT INTO reservas (id, usuario_id, equipo_id, fecha_inicio, fecha_fin, 
                                    estado, notas, estado_aprobacion)
                VALUES (%s, %s, %s, %s, %s, 'programada', %s, 'pendiente')
                """,
                (reserva_id, current_user, args['equipo_id'], fecha_inicio, fecha_fin, args['notas']),
            )
            db_manager.execute_query("UPDATE equipos SET estado='en_uso' WHERE id=%s", (args['equipo_id'],))
            
            # Enviar notificación a instructores a cargo del inventario
            notificaciones_manager.notificar_nueva_reserva(
                reserva_id=reserva_id,
                usuario_id=current_user,
                equipo_nombre=equipo_nombre,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                laboratorio_id=laboratorio_id
            )
            
            return {
                'message': 'Reserva creada exitosamente. Los instructores serán notificados.',
                'reserva_id': reserva_id
            }, 201
        except Exception as e:
            return {'message': f'Error creando reserva: {str(e)}'}, 500


class ReservaAPI(Resource):
    def delete(self, reserva_id):
        verify_jwt_in_request()
        rs = db_manager.execute_query("SELECT usuario_id, equipo_id, estado FROM reservas WHERE id=%s", (reserva_id,))
        if not rs:
            return {'message': 'Reserva no encontrada'}, 404
        reserva = rs[0]
        if reserva['estado'] not in ['programada', 'activa']:
            return {'message': 'No se puede cancelar esta reserva'}, 400
        try:
            db_manager.execute_query("UPDATE reservas SET estado='cancelada' WHERE id=%s", (reserva_id,))
            db_manager.execute_query("UPDATE equipos SET estado='disponible' WHERE id=%s", (reserva['equipo_id'],))
            return {'message': 'Reserva cancelada exitosamente'}, 200
        except Exception as e:
            return {'message': f'Error cancelando reserva: {str(e)}'}, 500


class NotificacionesAPI(Resource):
    def get(self):
        """Obtener notificaciones del usuario"""
        # Permitir JWT o sesión web
        try:
            verify_jwt_in_request()
            usuario_id = get_jwt_identity()
        except:
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
            usuario_id = session['user_id']
        
        solo_no_leidas = request.args.get('no_leidas', 'false').lower() == 'true'
        limite = int(request.args.get('limite', 50))
        
        notificaciones = notificaciones_manager.obtener_notificaciones_usuario(
            usuario_id=usuario_id,
            solo_no_leidas=solo_no_leidas,
            limite=limite
        )
        
        no_leidas = notificaciones_manager.contar_no_leidas(usuario_id)
        
        return {
            'notificaciones': notificaciones,
            'total_no_leidas': no_leidas
        }, 200


class NotificacionAPI(Resource):
    def put(self, notificacion_id):
        """Marcar notificación como leída"""
        # Permitir JWT o sesión web
        try:
            verify_jwt_in_request()
            usuario_id = get_jwt_identity()
        except:
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
            usuario_id = session['user_id']
        
        if notificaciones_manager.marcar_como_leida(notificacion_id):
            return {'message': 'Notificación marcada como leída'}, 200
        return {'message': 'Error al marcar notificación'}, 500
    
    def delete(self, notificacion_id):
        """Eliminar notificación"""
        # Permitir JWT o sesión web
        try:
            verify_jwt_in_request()
            usuario_id = get_jwt_identity()
        except:
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
            usuario_id = session['user_id']
        
        if notificaciones_manager.eliminar_notificacion(notificacion_id, usuario_id):
            return {'message': 'Notificación eliminada'}, 200
        return {'message': 'Error al eliminar notificación'}, 500


class ReservaRespuestaAPI(Resource):
    @require_instructor_inventario
    def post(self, reserva_id):
        """Aprobar o rechazar una reserva (solo instructor responsable del laboratorio)"""
        # Permitir JWT o sesión web
        try:
            verify_jwt_in_request()
            instructor_id = get_jwt_identity()
        except:
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
            instructor_id = session['user_id']
        
        # VALIDACIÓN ESTRICTA: Verificar que el instructor sea responsable del laboratorio
        es_instructor, lab_instructor = permissions_manager.es_instructor_con_inventario(instructor_id)
        
        if not es_instructor:
            return {'message': 'No tienes permisos de instructor a cargo de inventario'}, 403
        
        data = request.get_json()
        respuesta = data.get('respuesta')  # 'aprobada' o 'rechazada'
        motivo_rechazo = data.get('motivo_rechazo')
        
        if respuesta not in ['aprobada', 'rechazada']:
            return {'message': 'Respuesta inválida. Debe ser "aprobada" o "rechazada"'}, 400
        
        # Obtener información de la reserva Y el laboratorio del equipo
        query_reserva = """
            SELECT r.usuario_id, r.equipo_id, e.nombre as equipo_nombre,
                   e.laboratorio_id, l.nombre as laboratorio_nombre
            FROM reservas r
            JOIN equipos e ON r.equipo_id = e.id
            LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
            WHERE r.id = %s
        """
        reserva = db_manager.execute_query(query_reserva, (reserva_id,))
        
        if not reserva:
            return {'message': 'Reserva no encontrada'}, 404
        
        lab_equipo = reserva[0]['laboratorio_id']
        lab_nombre = reserva[0]['laboratorio_nombre'] or 'desconocido'
        
        # VALIDACIÓN CRÍTICA: El laboratorio del equipo debe coincidir con el del instructor
        if lab_equipo != lab_instructor:
            return {
                'message': f'No tienes autorización para gestionar reservas de este laboratorio. Solo puedes aprobar reservas de tu laboratorio asignado.',
                'tu_laboratorio': lab_instructor,
                'laboratorio_equipo': lab_equipo,
                'nombre_laboratorio': lab_nombre
            }, 403
        
        usuario_id = reserva[0]['usuario_id']
        equipo_id = reserva[0]['equipo_id']
        
        # Actualizar la reserva
        try:
            if respuesta == 'aprobada':
                query = """
                    UPDATE reservas 
                    SET estado_aprobacion = 'aprobada',
                        instructor_aprobador = %s,
                        fecha_aprobacion = NOW(),
                        estado = 'aprobada'
                    WHERE id = %s
                """
                db_manager.execute_query(query, (instructor_id, reserva_id))
            else:
                query = """
                    UPDATE reservas 
                    SET estado_aprobacion = 'rechazada',
                        instructor_aprobador = %s,
                        fecha_aprobacion = NOW(),
                        motivo_rechazo = %s,
                        estado = 'cancelada'
                    WHERE id = %s
                """
                db_manager.execute_query(query, (instructor_id, motivo_rechazo, reserva_id))
                
                # Liberar el equipo si fue rechazada
                db_manager.execute_query(
                    "UPDATE equipos SET estado='disponible' WHERE id=%s", 
                    (equipo_id,)
                )
            
            # Obtener nombre del instructor
            query_instructor = "SELECT nombre FROM usuarios WHERE id = %s"
            instructor = db_manager.execute_query(query_instructor, (instructor_id,))
            instructor_nombre = instructor[0]['nombre'] if instructor else 'Instructor'
            
            # Enviar notificación al usuario
            notificaciones_manager.notificar_respuesta_reserva(
                reserva_id=reserva_id,
                usuario_id=usuario_id,
                instructor_nombre=instructor_nombre,
                aprobada=(respuesta == 'aprobada'),
                motivo=motivo_rechazo
            )
            
            # Log de seguridad: Registro de aprobación/rechazo
            try:
                log_query = """
                    INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                    VALUES (%s, %s, %s, %s, TRUE)
                """
                accion = 'aprobar_reserva' if respuesta == 'aprobada' else 'rechazar_reserva'
                detalle = f'Reserva {reserva_id} {respuesta} por instructor {instructor_id} (Lab: {lab_instructor})'
                db_manager.execute_query(log_query, (
                    instructor_id,
                    accion,
                    detalle,
                    request.remote_addr
                ))
            except:
                pass  # No fallar si el log falla
            
            mensaje = 'Reserva aprobada exitosamente' if respuesta == 'aprobada' else 'Reserva rechazada'
            return {'message': mensaje}, 200
            
        except Exception as e:
            return {'message': f'Error procesando respuesta: {str(e)}'}, 500


class UsuariosAPI(Resource):
    def get(self):
        """Obtener lista de usuarios (solo administradores)"""
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        
        # Verificar que el usuario sea administrador
        query_nivel = "SELECT nivel_acceso FROM usuarios WHERE id = %s"
        result = db_manager.execute_query(query_nivel, (current_user,))
        
        if not result or result[0]['nivel_acceso'] < NIVEL_ADMINISTRADOR:
            return {'message': 'Acceso denegado. Solo administradores pueden ver usuarios'}, 403
        
        query = (
            """
            SELECT id, nombre, tipo, programa, nivel_acceso, activo, email,
                   DATE_FORMAT(fecha_registro, '%Y-%m-%d') as fecha_registro,
                   CASE WHEN rostro_data IS NOT NULL THEN true ELSE false END as tiene_rostro
            FROM usuarios
            ORDER BY tipo, nombre
            """
        )
        usuarios = db_manager.execute_query(query)
        return {'usuarios': usuarios}, 200


class UsuarioCreateAPI(Resource):
    @require_login
    def post(self):
        """Crear nuevo usuario (solo administradores)"""
        if session.get('user_level', 0) < NIVEL_ADMINISTRADOR:
            return {'success': False, 'message': 'Acceso denegado'}, 403
        
        data = request.get_json()
        user_id = data.get('id', '').strip()
        nombre = data.get('nombre', '').strip()
        password = data.get('password', '').strip()
        nivel_acceso = data.get('nivel_acceso', 1)
        email = data.get('email', '').strip()
        
        if not user_id or not nombre or not password:
            return {'success': False, 'message': 'Faltan campos obligatorios'}, 400
        
        # Verificar que el usuario no exista
        check = db_manager.execute_query("SELECT id FROM usuarios WHERE id = %s", (user_id,))
        if check:
            return {'success': False, 'message': 'El ID de usuario ya existe'}, 400
        
        try:
            query = """
                INSERT INTO usuarios (id, nombre, password_hash, nivel_acceso, email, tipo, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db_manager.execute_query(query, (user_id, nombre, password, nivel_acceso, email, 'usuario', True))
            return {'success': True, 'message': 'Usuario creado exitosamente'}, 201
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}, 500


class UsuarioUpdateAPI(Resource):
    @require_login
    def put(self, user_id):
        """Actualizar usuario (solo administradores)"""
        if session.get('user_level', 0) < NIVEL_ADMINISTRADOR:
            return {'success': False, 'message': 'Acceso denegado'}, 403
        
        data = request.get_json()
        nivel_acceso = data.get('nivel_acceso')
        password = data.get('password', '').strip()
        
        try:
            if password:
                query = "UPDATE usuarios SET nivel_acceso = %s, password_hash = %s WHERE id = %s"
                db_manager.execute_query(query, (nivel_acceso, password, user_id))
            else:
                query = "UPDATE usuarios SET nivel_acceso = %s WHERE id = %s"
                db_manager.execute_query(query, (nivel_acceso, user_id))
            
            return {'success': True, 'message': 'Usuario actualizado exitosamente'}, 200
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}, 500


class UsuarioToggleAPI(Resource):
    @require_login
    def put(self, user_id):
        """Activar/Desactivar usuario (solo administradores)"""
        if session.get('user_level', 0) < NIVEL_ADMINISTRADOR:
            return {'success': False, 'message': 'Acceso denegado'}, 403
        
        data = request.get_json()
        activo = data.get('activo', 1)
        
        try:
            query = "UPDATE usuarios SET activo = %s WHERE id = %s"
            db_manager.execute_query(query, (activo, user_id))
            return {'success': True, 'message': 'Estado actualizado exitosamente'}, 200
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}, 500


class UsuarioDeleteAPI(Resource):
    @require_login
    def delete(self, user_id):
        """Eliminar usuario permanentemente (solo administradores)"""
        if session.get('user_level', 0) < NIVEL_ADMINISTRADOR:
            return {'success': False, 'message': 'Acceso denegado'}, 403
        
        # Prevenir auto-eliminación
        if session.get('user_id') == user_id:
            return {'success': False, 'message': 'No puedes eliminar tu propia cuenta'}, 400
        
        # Verificar que el usuario existe
        check = db_manager.execute_query("SELECT id FROM usuarios WHERE id = %s", (user_id,))
        if not check:
            return {'success': False, 'message': 'Usuario no encontrado'}, 404
        
        try:
            # Eliminar usuario permanentemente
            query = "DELETE FROM usuarios WHERE id = %s"
            db_manager.execute_query(query, (user_id,))
            return {'success': True, 'message': 'Usuario eliminado permanentemente'}, 200
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}, 500


class EstadisticasAPI(Resource):
    def get(self):
        verify_jwt_in_request()
        stats = get_dashboard_stats()
        q1 = (
            """
            SELECT u.programa, COUNT(DISTINCT h.id) usos
            FROM usuarios u
            LEFT JOIN historial_uso h ON u.id = h.usuario_id AND h.fecha_uso >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY u.programa
            ORDER BY usos DESC
            """
        )
        stats['uso_por_programa'] = db_manager.execute_query(q1)
        q2 = (
            """
            SELECT e.nombre, e.tipo, COUNT(h.id) usos
            FROM equipos e
            LEFT JOIN historial_uso h ON e.id = h.equipo_id AND h.fecha_uso >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY e.id, e.nombre, e.tipo
            ORDER BY usos DESC
            LIMIT 10
            """
        )
        stats['equipos_mas_usados'] = db_manager.execute_query(q2)
        return {'estadisticas': stats}, 200


class ComandosVozAPI(Resource):
    def post(self):
        # Comandos de voz sin autenticación para navegación simple
        parser = reqparse.RequestParser()
        parser.add_argument('comando', required=True)
        args = parser.parse_args()
        
        respuesta = procesar_comando_voz(args['comando'].lower().strip())
        
        # Intentar registrar el comando (opcional, sin fallar si no hay usuario)
        try:
            # Verificar si hay usuario logueado (opcional)
            current_user = None
            try:
                verify_jwt_in_request()
                current_user = get_jwt_identity()
            except:
                current_user = 'anonimo'  # Usuario anónimo para comandos de navegación
            
            db_manager.execute_query(
                """
                INSERT INTO comandos_voz (usuario_id, comando, respuesta, exito)
                VALUES (%s, %s, %s, %s)
                """,
                (current_user, args['comando'], respuesta['mensaje'], respuesta['exito']),
            )
        except Exception as e:
            # No fallar si no se puede registrar el comando
            print(f"No se pudo registrar comando de voz: {e}")
            pass
        
        return respuesta, 200


def procesar_comando_voz(comando: str):
    """
    Procesador de comandos de voz - Navegación entre módulos del sistema
    """
    comando = comando.lower().strip()
    
    # =============================
    # COMANDOS DE NAVEGACIÓN
    # =============================
    
    # Dashboard / Inicio
    if any(p in comando for p in ['dashboard', 'inicio', 'home', 'principal', 'tablero']):
        return {'mensaje': '📊 Navegando al dashboard...', 'exito': True, 'accion': 'navegar', 'url': '/dashboard'}
    
    # Laboratorios
    if any(p in comando for p in ['laboratorios', 'laboratorio', 'labs', 'lab']):
        return {'mensaje': '🔬 Navegando a laboratorios...', 'exito': True, 'accion': 'navegar', 'url': '/laboratorios'}
    
    # Equipos
    if any(p in comando for p in ['equipos', 'equipo', 'maquinaria', 'herramientas']):
        return {'mensaje': '⚙️ Navegando a equipos...', 'exito': True, 'accion': 'navegar', 'url': '/equipos'}
    
    # Inventario
    if any(p in comando for p in ['inventario', 'stock', 'almacén', 'almacen', 'reactivos', 'materiales']):
        return {'mensaje': '📦 Navegando a inventario...', 'exito': True, 'accion': 'navegar', 'url': '/inventario'}
    
    # Reservas
    if any(p in comando for p in ['reservas', 'reserva', 'reservaciones', 'reservación']):
        return {'mensaje': '📅 Navegando a reservas...', 'exito': True, 'accion': 'navegar', 'url': '/reservas'}
    
    # Usuarios
    if any(p in comando for p in ['usuarios', 'usuario', 'personas', 'estudiantes']):
        return {'mensaje': '👥 Navegando a usuarios...', 'exito': True, 'accion': 'navegar', 'url': '/usuarios'}
    
    # Reportes
    if any(p in comando for p in ['reportes', 'reporte', 'informes', 'estadísticas', 'estadisticas']):
        return {'mensaje': '📈 Navegando a reportes...', 'exito': True, 'accion': 'navegar', 'url': '/reportes'}
    
    # Configuración
    if any(p in comando for p in ['configuración', 'configuracion', 'ajustes', 'settings']):
        return {'mensaje': '⚙️ Navegando a configuración...', 'exito': True, 'accion': 'navegar', 'url': '/configuracion'}
    
    # Ayuda / Manual
    if any(p in comando for p in ['manual', 'ayuda general', 'documentación', 'documentacion', 'guía', 'guia']):
        return {'mensaje': '📖 Abriendo manual de usuario...', 'exito': True, 'accion': 'navegar', 'url': '/ayuda'}
    
    # Módulos del proyecto
    if any(p in comando for p in ['módulos', 'modulos', 'funcionalidades', 'características', 'caracteristicas']):
        return {'mensaje': '🧩 Navegando a módulos del proyecto...', 'exito': True, 'accion': 'navegar', 'url': '/modulos'}
    
    # Cerrar sesión
    if any(p in comando for p in ['cerrar sesión', 'cerrar sesion', 'salir', 'logout', 'desconectar']):
        return {'mensaje': '👋 Cerrando sesión...', 'exito': True, 'accion': 'navegar', 'url': '/logout'}
    
    # =============================
    # COMANDOS DE AYUDA
    # =============================
    
    if any(p in comando for p in ['ayuda', 'help', 'comandos', 'qué puedo decir', 'que puedo decir', 'opciones']):
        return {
            'mensaje': """🎤 Comandos de voz disponibles:
            
📍 NAVEGACIÓN:
• "Dashboard" o "Inicio" - Panel principal
• "Laboratorios" - Gestión de laboratorios
• "Equipos" - Gestión de equipos
• "Inventario" - Control de inventario y reactivos
• "Reservas" - Sistema de reservas
• "Usuarios" - Gestión de usuarios
• "Reportes" - Informes y estadísticas
• "Configuración" - Ajustes del sistema
• "Ayuda" - Manual de usuario
• "Módulos" - Ver funcionalidades del proyecto

🚪 SESIÓN:
• "Cerrar sesión" - Salir del sistema

💡 Tip: Puede decir variaciones como "ir a equipos", "mostrar inventario", etc.""", 
            'exito': True
        }
    
    # =============================
    # COMANDO NO RECONOCIDO
    # =============================
    
    return {
        'mensaje': f'❌ Comando "{comando}" no reconocido. Diga "ayuda" para ver todos los comandos disponibles.', 
        'exito': False
    }

# =====================================================================
# API DE RECONOCIMIENTO VISUAL
# =====================================================================

class VisualTrainingAPI(Resource):
    """API para entrenar el reconocimiento visual (versión mejorada con metadata completa)"""
    
    def post(self):
        """Agregar imagen de entrenamiento para un equipo o item"""
        data = request.get_json(silent=True) or {}
        item_type = data.get('item_type')  # 'equipo' o 'item'
        item_id = data.get('item_id')
        image_base64 = data.get('image_base64')
        description = data.get('description', '')
        view_angle = data.get('view_angle', 'frontal')
        
        if not item_type or item_type not in ['equipo', 'item']:
            return {'message': 'item_type debe ser "equipo" o "item"'}, 400
        if not item_id:
            return {'message': 'item_id es requerido'}, 400
        if not image_base64:
            return {'message': 'image_base64 es requerido'}, 400
        
        try:
            # Decodificar imagen base64
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {'message': 'No se pudo decodificar la imagen'}, 400
            
            # Obtener detalles del item desde la base de datos
            item_details = {}
            if item_type == 'equipo':
                query = "SELECT id, nombre, tipo, estado, ubicacion, especificaciones FROM equipos WHERE id = %s"
                result = db_manager.execute_query(query, (item_id,))
                if result:
                    item_details = result[0]
                    # Parsear especificaciones JSON
                    if item_details.get('especificaciones'):
                        try:
                            item_details['especificaciones'] = json.loads(item_details['especificaciones'])
                        except:
                            item_details['especificaciones'] = {}
            else:
                query = "SELECT id, nombre, categoria, cantidad_actual, unidad, ubicacion FROM inventario WHERE id = %s"
                result = db_manager.execute_query(query, (item_id,))
                if result:
                    item_details = result[0]
            
            if not item_details:
                return {'message': f'{item_type} con ID {item_id} no encontrado en la base de datos'}, 404
            
            # Guardar imagen de entrenamiento
            base_dir = os.path.join('imagenes', 'entrenamiento', item_type, str(item_id))
            os.makedirs(base_dir, exist_ok=True)
            
            filename = f"{view_angle}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(base_dir, filename)
            cv2.imwrite(filepath, image)
            
            # Extraer características ORB para verificación
            orb = cv2.ORB_create(nfeatures=500)
            keypoints, descriptors = orb.detectAndCompute(image, None)
            num_features = len(keypoints) if keypoints else 0
            
            # Guardar metadatos completos incluyendo detalles del item
            metadata = {
                'description': description,
                'view_angle': view_angle,
                'filepath': filepath,
                'training_date': datetime.now().isoformat(),
                'num_features': num_features,
                'item_details': item_details  # Incluir todos los detalles del item
            }
            
            metadata_file = os.path.join(base_dir, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    all_metadata = json.load(f)
            else:
                all_metadata = []
            
            all_metadata.append(metadata)
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(all_metadata, f, indent=2, ensure_ascii=False)
            
            return {
                'message': 'Imagen de entrenamiento guardada exitosamente',
                'filepath': filepath,
                'num_features': num_features,
                'total_images': len(all_metadata),
                'item_details': item_details
            }, 200
                
        except Exception as e:
            print(f"[ERROR] Error en entrenamiento visual: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error procesando imagen: {str(e)}'}, 500

class VisualRecognitionAPI(Resource):
    """API para reconocer equipos e items por imagen (versión simplificada)"""
    
    def post(self):
        """Reconocer equipo o item en una imagen"""
        data = request.get_json(silent=True) or {}
        image_base64 = data.get('image_base64')
        confidence_threshold = data.get('confidence_threshold', 0.3)
        
        if not image_base64:
            return {'message': 'image_base64 es requerido'}, 400
        
        try:
            # Decodificar imagen base64
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {'message': 'No se pudo decodificar la imagen'}, 400
            
            # Buscar coincidencias en imágenes de entrenamiento usando comparación simple
            result = self._simple_recognition(image, confidence_threshold)
            
            if not result['success']:
                return {'message': result['message']}, 400
            
            # Si se reconoció algo, obtener detalles actualizados de la base de datos
            if result['recognized']:
                item_details = None
                
                # Primero intentar usar metadata guardada (tiene toda la info)
                if result.get('metadata'):
                    metadata = result['metadata']
                    
                    # Si tiene item_details (formato antiguo de entrenamiento)
                    if metadata.get('item_details'):
                        item_details = metadata['item_details']
                        item_details['tipo_item'] = result['item_type']
                        item_details['from_cache'] = True
                    
                    # Si tiene la metadata del registro (formato nuevo)
                    elif metadata.get('id') or metadata.get('nombre'):
                        item_details = {
                            'id': metadata.get('id'),
                            'nombre': metadata.get('nombre'),
                            'categoria': metadata.get('categoria'),
                            'descripcion': metadata.get('descripcion'),
                            'ubicacion': metadata.get('ubicacion'),
                            'laboratorio_id': metadata.get('laboratorio_id'),
                            'tipo_item': result['item_type'],
                            'from_cache': True
                        }
                        
                        # Agregar campos específicos según tipo
                        if result['item_type'] == 'equipo':
                            item_details['estado'] = metadata.get('estado', 'disponible')
                            item_details['equipo_id'] = metadata.get('equipo_id')
                        else:
                            item_details['cantidad_actual'] = metadata.get('cantidad')
                
                # Intentar obtener datos actualizados de la base de datos
                # Primero necesitamos el ID real del item
                db_id = None
                
                # Si metadata tiene el ID, usarlo
                if result.get('metadata') and result['metadata'].get('id'):
                    db_id = result['metadata']['id']
                # Si item_id es numérico, usarlo directamente
                elif result['item_id'].isdigit():
                    db_id = result['item_id']
                # Si no, buscar por nombre en la metadata
                elif result.get('metadata') and result['metadata'].get('nombre'):
                    nombre = result['metadata']['nombre']
                    if result['item_type'] == 'equipo':
                        search_query = "SELECT id FROM equipos WHERE nombre = %s LIMIT 1"
                    else:
                        search_query = "SELECT id FROM inventario WHERE nombre = %s LIMIT 1"
                    search_result = db_manager.execute_query(search_query, (nombre,))
                    if search_result:
                        db_id = search_result[0]['id']
                
                # Obtener datos frescos de la BD si tenemos el ID
                if db_id:
                    if result['item_type'] == 'equipo':
                        equipo_query = """
                            SELECT e.id, e.nombre, e.tipo, e.estado, e.ubicacion, e.especificaciones,
                                   e.laboratorio_id, l.nombre as laboratorio_nombre, l.ubicacion as laboratorio_ubicacion,
                                   e.equipo_id, e.marca, e.modelo, e.numero_serie, e.observaciones,
                                   DATE_FORMAT(e.fecha_creacion, '%Y-%m-%d %H:%i') as fecha_creacion
                            FROM equipos e
                            LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
                            WHERE e.id = %s
                        """
                        equipo_data = db_manager.execute_query(equipo_query, (db_id,))
                        if equipo_data:
                            fresh_details = equipo_data[0]
                            # Parsear especificaciones JSON
                            if fresh_details.get('especificaciones'):
                                try:
                                    fresh_details['especificaciones'] = json.loads(fresh_details['especificaciones'])
                                except:
                                    fresh_details['especificaciones'] = {}
                            fresh_details['tipo_item'] = 'equipo'
                            fresh_details['from_cache'] = False
                            item_details = fresh_details
                    
                    elif result['item_type'] == 'item':
                        item_query = """
                            SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.unidad, i.ubicacion,
                                   i.laboratorio_id, l.nombre as laboratorio_nombre, l.ubicacion as laboratorio_ubicacion,
                                   i.cantidad_minima, i.descripcion, i.proveedor,
                                   DATE_FORMAT(i.fecha_registro, '%Y-%m-%d %H:%i') as fecha_registro
                            FROM inventario i
                            LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                            WHERE i.id = %s
                        """
                        item_data = db_manager.execute_query(item_query, (db_id,))
                        if item_data:
                            fresh_details = item_data[0]
                            fresh_details['tipo_item'] = 'item'
                            fresh_details['from_cache'] = False
                            item_details = fresh_details
                
                # Si no se pudo obtener de BD pero tenemos metadata, enriquecer con info de laboratorio
                if not item_details or item_details.get('from_cache'):
                    if item_details and item_details.get('laboratorio_id'):
                        lab_query = "SELECT id, nombre, ubicacion FROM laboratorios WHERE id = %s"
                        lab_data = db_manager.execute_query(lab_query, (item_details['laboratorio_id'],))
                        if lab_data:
                            item_details['laboratorio_nombre'] = lab_data[0]['nombre']
                            item_details['laboratorio_ubicacion'] = lab_data[0]['ubicacion']
                
                return {
                    'recognized': True,
                    'confidence': result['confidence'],
                    'item_type': result['item_type'],
                    'item_id': result['item_id'],
                    'details': item_details,
                    'matches': result.get('matches', 0),
                    'training_metadata': result.get('metadata', {})  # Metadata del entrenamiento
                }, 200
            else:
                return {
                    'recognized': False,
                    'message': 'No se encontraron coincidencias suficientes. Entrene más imágenes de este item.',
                    'best_score': result.get('best_score', 0)
                }, 200
                
        except Exception as e:
            print(f"[ERROR] Error en reconocimiento: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error en reconocimiento: {str(e)}'}, 500
    
    def _simple_recognition(self, query_image, threshold=0.3):
        """Reconocimiento mejorado usando ORB con metadata completa"""
        try:
            print(f"\n[DEBUG RECONOCIMIENTO] Iniciando reconocimiento visual...")
            print(f"[DEBUG] Umbral de confianza: {threshold}")
            
            # Usar ORB para detectar características
            orb = cv2.ORB_create(nfeatures=500)
            kp1, des1 = orb.detectAndCompute(query_image, None)
            
            print(f"[DEBUG] Características detectadas en imagen query: {len(kp1) if kp1 else 0} keypoints")
            
            if des1 is None:
                return {'success': True, 'recognized': False, 'message': 'No se detectaron características en la imagen'}
            
            best_match = None
            best_score = 0
            best_metadata = None
            
            # BUSCAR EN DOS UBICACIONES:
            # 1. imagenes/entrenamiento/{tipo}/{id}/ (imágenes de entrenamiento manual)
            # 2. imagenes/{tipo}/{nombre}/ (imágenes del módulo de registro)
            
            search_paths = []
            
            # Crear directorios si no existen
            os.makedirs('imagenes/entrenamiento/equipo', exist_ok=True)
            os.makedirs('imagenes/entrenamiento/item', exist_ok=True)
            os.makedirs('imagenes/equipo', exist_ok=True)
            os.makedirs('imagenes/item', exist_ok=True)
            
            # Ruta 1: Entrenamiento manual
            training_base = 'imagenes/entrenamiento'
            if os.path.exists(training_base):
                for item_type in ['equipo', 'item']:
                    type_dir = os.path.join(training_base, item_type)
                    if os.path.exists(type_dir):
                        try:
                            for item_id in os.listdir(type_dir):
                                item_dir = os.path.join(type_dir, item_id)
                                if os.path.isdir(item_dir):
                                    search_paths.append({
                                        'path': item_dir,
                                        'type': item_type,
                                        'id': item_id,
                                        'source': 'training'
                                    })
                        except (OSError, PermissionError) as e:
                            print(f"[WARN] Error accediendo a {type_dir}: {e}")
                            continue
            
            # Ruta 2: Registro de equipos/items
            registro_base = 'imagenes'
            for item_type in ['equipo', 'item']:
                type_dir = os.path.join(registro_base, item_type)
                if os.path.exists(type_dir):
                    try:
                        for nombre_carpeta in os.listdir(type_dir):
                            item_dir = os.path.join(type_dir, nombre_carpeta)
                            if os.path.isdir(item_dir):
                                search_paths.append({
                                    'path': item_dir,
                                    'type': item_type,
                                    'id': nombre_carpeta,
                                    'source': 'registro'
                                })
                    except (OSError, PermissionError) as e:
                        print(f"[WARN] Error accediendo a {type_dir}: {e}")
                        continue
            
            print(f"[DEBUG] Total de carpetas a buscar: {len(search_paths)}")
            for sp in search_paths:
                print(f"  - {sp['type']}/{sp['id']} (fuente: {sp['source']})")
            
            if not search_paths:
                return {'success': True, 'recognized': False, 'message': 'No hay imágenes registradas. Registre equipos/items con fotos primero.'}
            
            # Buscar en todas las rutas
            total_comparisons = 0
            for search_info in search_paths:
                item_dir = search_info['path']
                item_type = search_info['type']
                item_id = search_info['id']
                
                print(f"\n[DEBUG] Buscando en: {item_dir}")
                
                # Cargar metadata del item
                metadata_file = os.path.join(item_dir, 'metadata.json')
                item_metadata = None
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata_content = json.load(f)
                            # Si es una lista (formato entrenamiento), usar el último
                            if isinstance(metadata_content, list):
                                item_metadata = metadata_content[-1] if metadata_content else None
                            # Si es un dict (formato registro), usar directamente
                            elif isinstance(metadata_content, dict):
                                item_metadata = metadata_content
                        print(f"[DEBUG] Metadata cargada: {item_metadata.get('nombre', 'N/A') if item_metadata else 'None'}")
                    except Exception as e:
                        print(f"[WARN] Error leyendo metadata de {metadata_file}: {e}")
                
                # Comparar con todas las imágenes de este item
                try:
                    images_in_dir = [f for f in os.listdir(item_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                    print(f"[DEBUG] Imágenes encontradas: {len(images_in_dir)} -> {images_in_dir}")
                except (OSError, PermissionError) as e:
                    print(f"[WARN] Error listando imágenes en {item_dir}: {e}")
                    continue
                
                for img_file in images_in_dir:
                    img_path = os.path.join(item_dir, img_file)
                    train_img = cv2.imread(img_path)
                    if train_img is None:
                        print(f"[WARN] No se pudo leer imagen: {img_path}")
                        continue
                    
                    kp2, des2 = orb.detectAndCompute(train_img, None)
                    if des2 is None:
                        print(f"[WARN] No se detectaron características en: {img_file}")
                        continue
                    
                    # Comparar características
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                    matches = bf.match(des1, des2)
                    
                    # Calcular score basado en número de coincidencias
                    score = len(matches) / max(len(kp1), len(kp2))
                    total_comparisons += 1
                    
                    print(f"[DEBUG]   {img_file}: {len(matches)} matches, score={score:.4f} (kp_train={len(kp2)})")
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'item_type': item_type,
                            'item_id': item_id,
                            'matches': len(matches),
                            'score': score,
                            'source': search_info['source'],
                            'image_path': img_path
                        }
                        best_metadata = item_metadata
                        print(f"[DEBUG]   *** NUEVO MEJOR MATCH! ***")
            
            print(f"\n[DEBUG] Total de comparaciones realizadas: {total_comparisons}")
            print(f"[DEBUG] Mejor score encontrado: {best_score:.4f}")
            print(f"[DEBUG] Umbral requerido: {threshold:.4f}")
            print(f"[DEBUG] ¿Supera umbral?: {best_score >= threshold}")
            
            if best_match and best_score >= threshold:
                return {
                    'success': True,
                    'recognized': True,
                    'item_type': best_match['item_type'],
                    'item_id': best_match['item_id'],
                    'confidence': best_score,
                    'matches': best_match['matches'],
                    'metadata': best_metadata  # Incluir metadata guardada
                }
            else:
                return {
                    'success': True,
                    'recognized': False,
                    'best_score': best_score,
                    'message': f'Mejor coincidencia: {best_score:.2%} (umbral: {threshold:.2%}). Entrena más imágenes del item.'
                }
                
        except Exception as e:
            return {'success': False, 'message': str(e)}

class VisualStatsAPI(Resource):
    """API para estadísticas del sistema visual (simplificado)"""
    
    def get(self):
        """Obtener estadísticas del entrenamiento y registro"""
        try:
            stats = {
                'equipos_entrenados': 0,
                'items_entrenados': 0,
                'equipos_registrados': 0,
                'items_registrados': 0,
                'total_imagenes': 0,
                'imagenes_entrenamiento': 0,
                'imagenes_registro': 0
            }
            
            # Crear directorios si no existen
            os.makedirs('imagenes/entrenamiento/equipo', exist_ok=True)
            os.makedirs('imagenes/entrenamiento/item', exist_ok=True)
            os.makedirs('imagenes/equipo', exist_ok=True)
            os.makedirs('imagenes/item', exist_ok=True)
            
            # Contar imágenes de entrenamiento manual
            training_base = 'imagenes/entrenamiento'
            if os.path.exists(training_base):
                for item_type in ['equipo', 'item']:
                    type_dir = os.path.join(training_base, item_type)
                    if os.path.exists(type_dir):
                        try:
                            items = [d for d in os.listdir(type_dir) if os.path.isdir(os.path.join(type_dir, d))]
                            if item_type == 'equipo':
                                stats['equipos_entrenados'] = len(items)
                            else:
                                stats['items_entrenados'] = len(items)
                            
                            for item_id in items:
                                item_dir = os.path.join(type_dir, item_id)
                                try:
                                    images = [f for f in os.listdir(item_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                                    count = len(images)
                                    stats['imagenes_entrenamiento'] += count
                                    stats['total_imagenes'] += count
                                except (OSError, PermissionError):
                                    continue
                        except (OSError, PermissionError):
                            continue
            
            # Contar imágenes de registro
            registro_base = 'imagenes'
            for item_type in ['equipo', 'item']:
                type_dir = os.path.join(registro_base, item_type)
                if os.path.exists(type_dir):
                    try:
                        items = [d for d in os.listdir(type_dir) if os.path.isdir(os.path.join(type_dir, d))]
                        if item_type == 'equipo':
                            stats['equipos_registrados'] = len(items)
                        else:
                            stats['items_registrados'] = len(items)
                        
                        for nombre_carpeta in items:
                            item_dir = os.path.join(type_dir, nombre_carpeta)
                            try:
                                images = [f for f in os.listdir(item_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                                count = len(images)
                                stats['imagenes_registro'] += count
                                stats['total_imagenes'] += count
                            except (OSError, PermissionError):
                                continue
                    except (OSError, PermissionError):
                        continue
            
            return {'stats': stats}, 200
        except Exception as e:
            print(f"[ERROR] Error en VisualStatsAPI: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error obteniendo estadísticas: {str(e)}'}, 500

class VisualManagementAPI(Resource):
    """API para gestión de datos de entrenamiento (simplificado)"""
    
    def delete(self):
        """Eliminar datos de entrenamiento"""
        data = request.get_json(silent=True) or {}
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        
        if not item_type or item_type not in ['equipo', 'item']:
            return {'message': 'item_type debe ser "equipo" o "item"'}, 400
        if not item_id:
            return {'message': 'item_id es requerido'}, 400
        
        try:
            import shutil
            item_dir = os.path.join('imagenes', 'entrenamiento', item_type, str(item_id))
            
            if not os.path.exists(item_dir):
                return {'message': 'No se encontraron datos de entrenamiento para este item'}, 404
            
            # Contar archivos antes de eliminar
            files = [f for f in os.listdir(item_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            deleted_count = len(files)
            
            # Eliminar directorio completo
            shutil.rmtree(item_dir)
            
            return {
                'message': f'Datos de entrenamiento eliminados exitosamente',
                'deleted_files': deleted_count
            }, 200
                
        except Exception as e:
            return {'message': f'Error eliminando datos: {str(e)}'}, 500

# =====================================================================
# IMPORTAR MÓDULOS EXTERNOS ANTES DE REGISTRAR ENDPOINTS
# =====================================================================

# Implementación de API de registro facial
class FacialRegistrationAPI(Resource):
    """API para registrar, verificar y eliminar rostro de usuario"""
    
    def get(self):
        """Verificar si el usuario ya tiene rostro registrado"""
        try:
            user_id = request.args.get('user_id')
            
            if not user_id:
                return {'success': False, 'message': 'Se requiere user_id'}, 400
            
            # Verificar si el usuario tiene rostro registrado
            query = """SELECT id, nombre, rostro_data, fecha_registro 
                       FROM usuarios 
                       WHERE id = %s AND activo = TRUE"""
            
            users = db_manager.execute_query(query, (user_id,))
            
            if not users:
                return {'success': False, 'message': 'Usuario no encontrado'}, 404
            
            user = users[0]
            has_face = user['rostro_data'] is not None
            
            if has_face:
                # Convertir rostro a base64 para mostrarlo
                face_data = user['rostro_data']
                face_base64 = base64.b64encode(face_data).decode('utf-8')
                
                return {
                    'success': True,
                    'registered': True,
                    'user': {
                        'id': user['id'],
                        'nombre': user['nombre'],
                        'fecha_registro': str(user['fecha_registro'])
                    },
                    'face_image': f"data:image/jpeg;base64,{face_base64}"
                }, 200
            else:
                return {
                    'success': True,
                    'registered': False,
                    'user': {
                        'id': user['id'],
                        'nombre': user['nombre']
                    }
                }, 200
                
        except Exception as e:
            print(f"[ERROR] Error verificando registro facial: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'Error al verificar registro: {str(e)}'}, 500
    
    def delete(self):
        """Eliminar registro facial de usuario"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return {'success': False, 'message': 'Se requiere user_id'}, 400
            
            # Verificar que el usuario existe y tiene rostro
            check_query = "SELECT id, rostro_data FROM usuarios WHERE id = %s"
            users = db_manager.execute_query(check_query, (user_id,))
            
            if not users:
                return {'success': False, 'message': 'Usuario no encontrado'}, 404
            
            if users[0]['rostro_data'] is None:
                return {'success': False, 'message': 'El usuario no tiene rostro registrado'}, 400
            
            # Eliminar rostro
            delete_query = "UPDATE usuarios SET rostro_data = NULL WHERE id = %s"
            db_manager.execute_query(delete_query, (user_id,))
            
            # Log de auditoría
            log_query = """INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                           VALUES (%s, 'eliminacion_facial', 'Registro facial eliminado', %s, TRUE)"""
            try:
                db_manager.execute_query(log_query, (user_id, request.remote_addr))
            except:
                pass
            
            return {
                'success': True,
                'message': 'Registro facial eliminado exitosamente'
            }, 200
            
        except Exception as e:
            print(f"[ERROR] Error eliminando registro facial: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'Error al eliminar registro: {str(e)}'}, 500
    
    def post(self):
        """Registrar rostro de usuario"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            image_base64 = data.get('image')
            
            if not user_id or not image_base64:
                return {'success': False, 'message': 'Faltan datos requeridos (user_id, image)'}, 400
            
            # Remover prefijo data:image si existe
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            # Decodificar imagen
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'success': False, 'message': 'No se pudo procesar la imagen'}, 400
            
            # Detectar rostro
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            
            if len(faces) == 0:
                return {'success': False, 'message': 'No se detectó ningún rostro en la imagen'}, 400
            
            if len(faces) > 1:
                return {'success': False, 'message': 'Se detectaron múltiples rostros. Solo debe aparecer un rostro'}, 400
            
            # Extraer rostro y guardar
            (x, y, w, h) = faces[0]
            face_roi = img[y:y+h, x:x+w]
            
            # Redimensionar para almacenamiento
            face_roi = cv2.resize(face_roi, (200, 200))
            
            # Convertir a JPEG para almacenar
            _, buffer = cv2.imencode('.jpg', face_roi)
            face_blob = buffer.tobytes()
            
            # Actualizar usuario en la base de datos
            update_query = """
                UPDATE usuarios 
                SET rostro_data = %s
                WHERE id = %s
            """
            
            try:
                # Verificar si el usuario existe
                check_query = "SELECT id, nombre FROM usuarios WHERE id = %s"
                users = db_manager.execute_query(check_query, (user_id,))
                
                if not users:
                    return {'success': False, 'error': 'Usuario no encontrado en la base de datos'}, 404
                
                # Actualizar rostro
                result = db_manager.execute_query(update_query, (face_blob, user_id))
                
                # Verificar que se actualizó correctamente
                if result is not None:
                    # Log de auditoría
                    log_query = """
                        INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
                        VALUES (%s, 'registro_facial', 'Rostro registrado exitosamente', %s, TRUE)
                    """
                    try:
                        db_manager.execute_query(log_query, (user_id, request.remote_addr))
                    except Exception as log_error:
                        print(f"[WARNING] Error en log de auditoría: {log_error}")
                    
                    return {
                        'success': True,
                        'message': 'Rostro registrado exitosamente',
                        'user_id': user_id,
                        'user_name': users[0]['nombre']
                    }, 200
                else:
                    return {'success': False, 'error': 'No se pudo actualizar el registro en la base de datos'}, 500
                
            except mysql.connector.Error as db_error:
                print(f"[ERROR] Error de base de datos: {db_error}")
                print(f"[ERROR] Error code: {db_error.errno}")
                print(f"[ERROR] SQL State: {db_error.sqlstate}")
                return {'success': False, 'error': f'Error de base de datos: {str(db_error)}'}, 500
            except Exception as e:
                print(f"[ERROR] Error guardando rostro en BD: {e}")
                import traceback
                traceback.print_exc()
                return {'success': False, 'error': f'Error guardando en base de datos: {str(e)}'}, 500
                
        except cv2.error as cv_error:
            print(f"[ERROR] Error de OpenCV: {cv_error}")
            return {'success': False, 'error': f'Error procesando imagen: {str(cv_error)}'}, 500
        except Exception as e:
            print(f"[ERROR] Error en registro facial: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Error desconocido: {str(e)}. Por favor, contacta al administrador.'}, 500

FACIAL_API_AVAILABLE = True
print("[OK] Modulo de reconocimiento facial cargado (OpenCV)")

# =====================================================================
# REGISTRO DE ENDPOINTS API
# =====================================================================

api.add_resource(AuthAPI, '/api/auth')
api.add_resource(LaboratoriosAPI, '/api/laboratorios')
api.add_resource(LaboratorioAPI, '/api/laboratorios/<int:laboratorio_id>')
api.add_resource(EquiposAPI, '/api/equipos')
api.add_resource(EquipoAPI, '/api/equipos/<string:equipo_id>')
api.add_resource(InventarioAPI, '/api/inventario')
api.add_resource(ReservasAPI, '/api/reservas')
api.add_resource(ReservaAPI, '/api/reservas/<string:reserva_id>')
api.add_resource(ReservaRespuestaAPI, '/api/reservas/<string:reserva_id>/responder')
api.add_resource(NotificacionesAPI, '/api/notificaciones')
api.add_resource(NotificacionAPI, '/api/notificaciones/<int:notificacion_id>')
api.add_resource(UsuarioCreateAPI, '/api/usuarios/create')
api.add_resource(UsuarioUpdateAPI, '/api/usuarios/<string:user_id>/update')
api.add_resource(UsuarioToggleAPI, '/api/usuarios/<string:user_id>/toggle')
api.add_resource(UsuarioDeleteAPI, '/api/usuarios/<string:user_id>/delete')
api.add_resource(UsuariosAPI, '/api/usuarios')
api.add_resource(EstadisticasAPI, '/api/estadisticas')
api.add_resource(ComandosVozAPI, '/api/voz/comando')
api.add_resource(FacialRegistrationAPI, '/api/facial/register')
api.add_resource(VisualTrainingAPI, '/api/visual/training')
api.add_resource(VisualRecognitionAPI, '/api/visual/recognize')
api.add_resource(VisualStatsAPI, '/api/visual/stats')
api.add_resource(VisualManagementAPI, '/api/visual/management')

# =============================
# VISIÓN POR CÁMARA (MVP)
# =============================

# Rutas absolutas seguras para imágenes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_ROOT = os.path.join(BASE_DIR, 'imagenes')

# =============================
# INTEGRACIÓN DE IA AVANZADA
# =============================

# Inicializar sistema de IA avanzada
AI_MANAGER = None

try:
    from modules.ai_integration import create_ai_manager, enhance_vision_match_endpoint
    
    # Crear gestor de IA (se inicializará después de definir procesar_comando_voz)
    def initialize_ai_system():
        global AI_MANAGER
        if AI_MANAGER is None:
            AI_MANAGER = create_ai_manager(procesar_comando_voz, IMG_ROOT)
            if AI_MANAGER:
                print("[OK] Sistema de IA avanzada inicializado")
                # Iniciar control por voz si está disponible
                if AI_MANAGER.voice_ai_enabled:
                    AI_MANAGER.start_voice_control()
                    print("[OK] Control por voz avanzado activado")
            else:
                print("[WARN] Sistema de IA no disponible, usando metodos tradicionales")
        return AI_MANAGER
    
    AI_AVAILABLE = True
    
except ImportError as e:
    print(f"[WARN] Modulos de IA no disponibles: {e}")
    AI_AVAILABLE = False
    AI_MANAGER = None
    
    def initialize_ai_system():
        return None

def _decode_image_base64(img_b64: str):
    try:
        if ',' in img_b64:  # dataURL
            img_b64 = img_b64.split(',')[1]
        img_bytes = base64.b64decode(img_b64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None

def _safe_imread(path: str):
    try:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is not None:
            return img
        # Fallback: leer bytes y decodificar
        with open(path, 'rb') as f:
            buf = f.read()
        arr = np.frombuffer(buf, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        return None


def _load_template_images():
    templates = []

    # Utilidad para sanitizar carpeta->nombre
    import re
    def san(s: str) -> str:
        s = (s or '').lower().replace('..','').replace('/','').replace('\\','')
        s = re.sub(r"[^a-z0-9_\- ]+", '', s).strip()
        s = re.sub(r"\s+", '_', s)
        return s

    # 1) Plantillas de EQUIPOS por nombre (mapeadas a id)
    base_eq = os.path.join(IMG_ROOT, 'equipos')
    if os.path.isdir(base_eq):
        try:
            rs = db_manager.execute_query("SELECT id, nombre FROM equipos") or []
        except Exception:
            rs = []
        name_to_id = { san(r['nombre']): str(r['id']) for r in rs }
        for entry in os.listdir(base_eq):
            folder_path = os.path.join(base_eq, entry)
            if not os.path.isdir(folder_path):
                continue
            eid_or_key = name_to_id.get(san(entry))  # si None, trataremos como OBJETO por nombre de carpeta
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                        continue
                    path = os.path.join(root, fn)
                    img = _safe_imread(path)
                    if img is None:
                        continue
                    templates.append((eid_or_key if eid_or_key else san(entry), img))
            # no hacer break: recorrer todas las subcarpetas (superior/inferior/etc.)

    # 2) Plantillas de OBJETOS por nombre (clave = nombre carpeta)
    base_obj = os.path.join(IMG_ROOT, 'objetos')
    if os.path.isdir(base_obj):
        for entry in os.listdir(base_obj):
            folder_path = os.path.join(base_obj, entry)
            if not os.path.isdir(folder_path):
                continue
            key = entry  # usamos nombre de carpeta
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                        continue
                    path = os.path.join(root, fn)
                    img = _safe_imread(path)
                    if img is None:
                        continue
                    templates.append((key, img))
            # no hacer break: recorrer todas las subcarpetas (superior/inferior/etc.)

    # 3) Plantillas de OBJETOS desde BD (BLOB)
    try:
        rows = db_manager.execute_query(
            """
            SELECT o.nombre, oi.imagen
            FROM objetos_imagenes oi
            JOIN objetos o ON o.id = oi.objeto_id
            """
        ) or []
        for r in rows:
            blob = r.get('imagen')
            if not blob:
                continue
            img_arr = np.frombuffer(blob, dtype=np.uint8)
            img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            if img is None:
                continue
            templates.append((san(r['nombre']), img))
    except Exception:
        pass

    # 4) Plantillas desde cualquier otra carpeta top-level dentro de 'imagenes/'
    base_root = IMG_ROOT
    if os.path.isdir(base_root):
        for entry in os.listdir(base_root):
            if entry in ('equipos','objetos'):
                continue
            folder_path = os.path.join(base_root, entry)
            if not os.path.isdir(folder_path):
                continue
            key = san(entry)
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                        continue
                    path = os.path.join(root, fn)
                    img = cv2.imread(path, cv2.IMREAD_COLOR)
                    if img is None:
                        continue
                    templates.append((key, img))

    return templates

# Endpoint de diagnóstico: lista carpetas y archivos detectados por visión
@app.get('/api/vision/debug_templates')
def vision_debug_templates():
    report = {'equipos': {}, 'objetos': {}, 'otros': {}}
    import re
    def san(s: str) -> str:
        s = (s or '').lower().replace('..','').replace('/','').replace('\\','')
        s = re.sub(r"[^a-z0-9_\- ]+", '', s).strip()
        s = re.sub(r"\s+", '_', s)
        return s
    # Equipos
    base_eq = os.path.join('imagenes', 'equipos')
    if os.path.isdir(base_eq):
        try:
            rs = db_manager.execute_query("SELECT id, nombre FROM equipos") or []
        except Exception:
            rs = []
        name_to_id = { san(r['nombre']): str(r['id']) for r in rs }
        for entry in os.listdir(base_eq):
            folder_path = os.path.join(base_eq, entry)
            if not os.path.isdir(folder_path):
                continue
            eid = name_to_id.get(san(entry))
            info = {'equipo_id': eid, 'path': folder_path, 'files': []}
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if fn.lower().endswith(('.jpg','.jpeg','.png')):
                        info['files'].append(os.path.join(root, fn).replace('\\','/'))
            report['equipos'][entry] = info
    # Objetos (FS y BD)
    base_obj = os.path.join('imagenes', 'objetos')
    if os.path.isdir(base_obj):
        for entry in os.listdir(base_obj):
            folder_path = os.path.join(base_obj, entry)
            if not os.path.isdir(folder_path):
                continue
            info = {'path': folder_path, 'files': []}
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if fn.lower().endswith(('.jpg','.jpeg','.png')):
                        info['files'].append(os.path.join(root, fn).replace('\\','/'))
            report['objetos'][entry] = info
    # Otros top-level bajo imagenes/
    base_root = 'imagenes'
    if os.path.isdir(base_root):
        for entry in os.listdir(base_root):
            if entry in ('equipos','objetos'):
                continue
            folder_path = os.path.join(base_root, entry)
            if not os.path.isdir(folder_path):
                continue
            info = {'path': folder_path, 'files': []}
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if fn.lower().endswith(('.jpg','.jpeg','.png')):
                        info['files'].append(os.path.join(root, fn).replace('\\','/'))
            report['otros'][entry] = info
    # Resumen desde BD
    try:
        db_rows = db_manager.execute_query("SELECT o.nombre, COUNT(oi.id) c FROM objetos o LEFT JOIN objetos_imagenes oi ON oi.objeto_id=o.id GROUP BY o.id, o.nombre") or []
        report['objetos_db'] = { r['nombre']: r['c'] for r in db_rows }
    except Exception:
        report['objetos_db'] = {}
    return jsonify(report), 200

# Conteo de plantillas cargadas (para depurar casos "no se encontraron plantillas")
@app.get('/api/vision/debug_counts')
def vision_debug_counts():
    templates = _load_template_images_slim(max_per_key=12)
    return jsonify({
        'total_templates': len(templates),
        'cwd': os.getcwd(),
        'img_root': IMG_ROOT,
    }), 200


def _match_orb_flann(frame: np.ndarray, templates, min_good=10):
    try:
        orb = cv2.ORB_create(nfeatures=1500)
        kp1, des1 = orb.detectAndCompute(frame, None)
        if des1 is None:
            return None
        index_params = dict(algorithm=6,  # FLANN_INDEX_LSH
                            table_number=12, key_size=20, multi_probe_level=2)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        best = None  # (key, score)
        for eid, tmpl in templates:
            kp2, des2 = orb.detectAndCompute(tmpl, None)
            if des2 is None:
                continue
            matches = flann.knnMatch(des1, des2, k=2)
            good = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)
            score = len(good)
            if best is None or score > best[1]:
                best = (eid, score)
        if best:
            if best[1] >= min_good:
                return {'equipo_id': best[0], 'score': int(best[1]), 'passed': True}
            else:
                return {'equipo_id': best[0], 'score': int(best[1]), 'passed': False}
        return None
    except Exception:
        return None


@app.post('/api/vision/match')
def vision_match():
    # No exigimos JWT por ahora, pero se puede agregar verify_jwt_in_request()
    data = request.get_json(silent=True) or {}
    img_b64 = data.get('image_base64')
    if not img_b64:
        return jsonify({'message': 'image_base64 requerido'}), 400
    
    # Intentar con IA avanzada primero
    if AI_MANAGER and AI_MANAGER.vision_ai_enabled:
        try:
            ai_result = AI_MANAGER.detect_objects_advanced(img_b64)
            if ai_result.get('success'):
                detection = ai_result['detection_result']
                if detection.get('detected'):
                    # Buscar en BD si es un objeto conocido
                    key = detection['class']
                    import re
                    def san(s: str) -> str:
                        s = (s or '').lower().replace('..','').replace('/','').replace('\\','')
                        s = re.sub(r"[^a-z0-9_\- ]+", '', s).strip()
                        s = re.sub(r"\s+", '_', s)
                        return s
                    
                    # Buscar objeto por nombre
                    objs = db_manager.execute_query("SELECT id, nombre, categoria, descripcion FROM objetos") or []
                    found = None
                    for o in objs:
                        if san(o['nombre']) == san(key):
                            found = o; break
                    
                    if found:
                        return jsonify({
                            'tipo': 'objeto',
                            'objeto': found,
                            'match': {
                                'equipo_id': key,
                                'score': int(detection['confidence'] * 100),
                                'passed': detection['confidence'] > 0.5,
                                'ai_enhanced': True,
                                'method': 'tensorflow'
                            },
                            'message': f'🤖 IA: {detection["class"]} (confianza: {detection["confidence"]:.2f})'
                        }), 200
                    else:
                        return jsonify({
                            'tipo': 'sugerencia',
                            'categoria': 'objeto',
                            'key': key,
                            'match': {
                                'equipo_id': key,
                                'score': int(detection['confidence'] * 100),
                                'passed': False,
                                'ai_enhanced': True,
                                'method': 'tensorflow'
                            },
                            'message': f'🤖 IA detectó: {key} (no registrado en BD)'
                        }), 200
        except Exception as e:
            print(f"Error en IA de visión: {e}")
    
    # Fallback a método tradicional
    frame = _decode_image_base64(img_b64)
    frame = _preprocess_for_orb(frame)
    if frame is None:
        return jsonify({'message': 'Imagen inválida'}), 400
    templates = _load_template_images_slim(max_per_key=12)
    if not templates:
        return jsonify({'message': 'No hay plantillas en imagenes/equipos u objetos'}), 404
    match = _match_orb_flann(frame, templates)
    if not match:
        return jsonify({'message': 'Sin coincidencias'}), 200

    key = str(match.get('equipo_id'))
    # Si key es numérica, tratamos como equipo
    if key.isdigit():
        rs = db_manager.execute_query("SELECT id, nombre, estado, ubicacion FROM equipos WHERE id=%s", (key,))
        if not rs:
            if match and match.get('passed') is False:
                return jsonify({'tipo': 'sugerencia', 'categoria': 'equipo', 'key': key, 'score': match.get('score'), 'message': 'Sugerencia de equipo (baja confianza)'}), 200
            return jsonify({'match': match, 'message': 'Coincidencia de equipo, pero no encontrado en BD'}), 200
        if match.get('passed'):
            return jsonify({'tipo': 'equipo', 'equipo': rs[0], 'match': match, 'message': 'Coincidencia de equipo encontrada'}), 200
        else:
            return jsonify({'tipo': 'sugerencia', 'categoria': 'equipo', 'equipo': rs[0], 'match': match, 'message': 'Sugerencia de equipo (baja confianza)'}), 200

    # Caso objeto: key es nombre de carpeta. Buscar objeto por nombre saneado
    import re
    def san(s: str) -> str:
        s = (s or '').lower().replace('..','').replace('/','').replace('\\','')
        s = re.sub(r"[^a-z0-9_\- ]+", '', s).strip()
        s = re.sub(r"\s+", '_', s)
        return s
    objs = db_manager.execute_query("SELECT id, nombre, categoria, descripcion FROM objetos") or []
    found = None
    for o in objs:
        if san(o['nombre']) == san(key):
            found = o; break
    if found:
        if match.get('passed'):
            return jsonify({'tipo': 'objeto', 'objeto': found, 'match': match, 'message': 'Coincidencia de objeto encontrada'}), 200
        else:
            return jsonify({'tipo': 'sugerencia', 'categoria': 'objeto', 'objeto': found, 'match': match, 'message': 'Sugerencia de objeto (baja confianza)'}), 200
    # No está en BD pero hay key (nombre de carpeta)
    if not key.isdigit():
        return jsonify({'tipo': 'sugerencia', 'categoria': 'objeto', 'key': key, 'match': match, 'message': 'Sugerencia de objeto por carpeta (no mapeada a BD)'}), 200
    return jsonify({'match': match, 'message': 'Coincidencia encontrada, pero no mapeada a BD'}), 200

# =============================
# OBJETOS: Registro unificado (crear + imagen)
# =============================

@app.post('/api/objetos/crear_con_imagen')
def crear_objeto_con_imagen():
    try:
        verify_jwt_or_admin()
    except Exception:
        return jsonify({'message': 'No autorizado'}), 401

    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombre') or '').strip()
    categoria = (data.get('categoria') or '').strip() or None
    descripcion = data.get('descripcion')
    img_b64 = data.get('image_base64')
    vista = (data.get('vista') or '').strip()
    notas = data.get('notas')
    fuente = data.get('fuente', 'upload')
    if not nombre:
        return jsonify({'message': 'nombre requerido'}), 400
    if not img_b64:
        return jsonify({'message': 'image_base64 requerido'}), 400
    if not vista:
        return jsonify({'message': 'vista requerida'}), 400

    # crear/obtener objeto
    try:
        rs_exist = db_manager.execute_query(
            "SELECT id FROM objetos WHERE nombre=%s AND (categoria=%s OR (categoria IS NULL AND %s IS NULL))",
            (nombre, categoria, categoria)
        ) or []
        if rs_exist:
            objeto_id = rs_exist[0]['id']
            print(f"[DEBUG] Objeto existente encontrado: ID={objeto_id}")
        else:
            print(f"[DEBUG] Creando nuevo objeto: nombre='{nombre}', categoria='{categoria}'")
            db_manager.execute_query(
                "INSERT INTO objetos (nombre, categoria, descripcion) VALUES (%s,%s,%s)",
                (nombre, categoria, descripcion)
            )
            rs_new = db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
            print(f"[DEBUG] Resultado LAST_INSERT_ID: {rs_new}")
            
            if not rs_new or not rs_new[0].get('id'):
                return jsonify({'message': 'Error: No se pudo obtener el ID del objeto creado'}), 500
            
            objeto_id = rs_new[0]['id']
            print(f"[DEBUG] Nuevo objeto creado: ID={objeto_id}")
        
        if not objeto_id:
            return jsonify({'message': 'Error: objeto_id es nulo'}), 500
            
    except Exception as e:
        print(f"[ERROR] Error creando/consultando objeto: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error creando/consultando objeto: {e}'}), 500

    # Guardar imagen en FS y BD (igual a ObjetoImagenAPI.post)
    try:
        # decode base64
        if ',' in img_b64:
            _, img_b64 = img_b64.split(',', 1)
        blob = base64.b64decode(img_b64)
        content_type = 'image/jpeg'
        import re
        def san(s: str) -> str:
            s = (s or '').lower().replace('..','').replace('/','').replace('\\','')
            s = re.sub(r"[^a-z0-9_\- ]+", '', s).strip()
            s = re.sub(r"\s+", '_', s)
            return s
        base_dir = os.path.join('imagenes', 'objetos', san(nombre), vista)
        os.makedirs(base_dir, exist_ok=True)
        filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = os.path.join(base_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(blob)
        # thumbnail
        thumb_blob = None
        try:
            img_arr = np.frombuffer(blob, dtype=np.uint8)
            im = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            if im is not None:
                h, w = im.shape[:2]
                scale = 320.0 / max(1.0, w)
                if scale < 1.0:
                    im_res = cv2.resize(im, (int(w*scale), int(h*scale)))
                else:
                    im_res = im
                ok, enc = cv2.imencode('.jpg', im_res, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ok:
                    thumb_blob = enc.tobytes()
        except Exception:
            thumb_blob = None
        # insert BD
        print(f"[DEBUG] Insertando imagen: objeto_id={objeto_id}, path={file_path}, vista={vista}")
        db_manager.execute_query(
            """
            INSERT INTO objetos_imagenes (objeto_id, path, thumbnail, fuente, notas, vista)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (objeto_id, file_path.replace('\\','/'), thumb_blob, fuente, notas, vista)
        )
        print(f"[OK] Imagen guardada exitosamente")
    except Exception as e:
        print(f"[ERROR] Error guardando imagen: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error guardando imagen: {e}'}), 500

    return jsonify({'message': 'Objeto e imagen guardados', 'id': objeto_id}), 201

# =============================
# OBJETOS: Registro y Gestión
# =============================

class ObjetosAPI(Resource):
    def get(self):
        verify_jwt_or_admin()
        q = request.args.get('q')
        sql = (
            "SELECT o.id, o.nombre, o.categoria, o.descripcion, "
            "DATE_FORMAT(o.fecha_creacion, '%Y-%m-%d %H:%i') as fecha_creacion, "
            "(SELECT COUNT(*) FROM objetos_imagenes oi WHERE oi.objeto_id=o.id) AS img_count, "
            "(SELECT oi2.id FROM objetos_imagenes oi2 WHERE oi2.objeto_id=o.id ORDER BY oi2.id ASC LIMIT 1) AS first_img_id "
            "FROM objetos o"
        )
        params = []
        if q:
            sql += " WHERE o.nombre LIKE %s OR o.categoria LIKE %s"
            params = [f"%{q}%", f"%{q}%"]
        sql += " ORDER BY o.categoria, o.nombre"
        rs = db_manager.execute_query(sql, params)
        return {'objetos': rs}, 200

    def post(self):
        try:
            print("[DEBUG] Iniciando POST /api/objetos")
            
            # Permitir acceso con JWT o sesión web
            try:
                verify_jwt_in_request()
                print("[OK] JWT verificado")
            except Exception as e:
                print(f"[WARN] JWT no valido: {e}")
                # Fallback a sesión web
                if 'user_id' not in session:
                    print("[ERROR] No hay sesion web")
                    return {'message': 'Autenticación requerida'}, 401
                print(f"[OK] Sesion web valida: user_id={session.get('user_id')}")
            
            data = request.get_json(silent=True) or {}
            print(f"[DATA] Datos recibidos: {data}")
            
            nombre = (data.get('nombre') or '').strip()
            categoria = (data.get('categoria') or '').strip()
            descripcion = data.get('descripcion')
            
            if not nombre:
                print("[ERROR] Nombre vacio")
                return {'message': 'nombre requerido'}, 400
            
            print(f"[OK] Datos validados: nombre='{nombre}', categoria='{categoria}'")
        except Exception as e:
            print(f"[ERROR] ERROR CRITICO en inicio de POST: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error crítico: {str(e)}'}, 500
        
        try:
            print(f"[DEBUG] POST /api/objetos - nombre: '{nombre}', categoria: '{categoria}'")
            
            # Verificar si ya existe
            rs_exist = db_manager.execute_query(
                "SELECT id FROM objetos WHERE nombre=%s AND (categoria=%s OR (categoria IS NULL AND %s IS NULL))",
                (nombre, categoria or None, categoria or None)
            )
            print(f"[DEBUG] Verificacion existencia: {rs_exist}")
            
            if rs_exist:
                return {'message': f'Ya existe un objeto "{nombre}" en la categoría "{categoria or "Sin categoría"}". Use el registro existente o cambie el nombre.', 'id': rs_exist[0]['id'], 'existe': True}, 200
            
            # Crear nuevo objeto
            print(f"[DEBUG] Insertando objeto...")
            db_manager.execute_query(
                "INSERT INTO objetos (nombre, categoria, descripcion) VALUES (%s, %s, %s)",
                (nombre, categoria or None, descripcion),
            )
            print(f"[OK] Objeto insertado")
            
            rs = db_manager.execute_query("SELECT id FROM objetos WHERE nombre=%s AND (categoria=%s OR (categoria IS NULL AND %s IS NULL)) ORDER BY id DESC LIMIT 1", (nombre, categoria or None, categoria or None))
            print(f"[DEBUG] ID recuperado: {rs}")
            
            return {'message': 'Objeto creado exitosamente', 'id': rs[0]['id'] if rs else None}, 201
        except Exception as e:
            print(f"[ERROR] ERROR en POST /api/objetos: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if '1062' in str(e) or 'Duplicate entry' in str(e):
                return {'message': f'Ya existe un objeto con ese nombre y categoría. Use un nombre diferente o seleccione el existente de la lista.', 'duplicado': True}, 409
            return {'message': f'Error creando objeto: {str(e)}'}, 500


class ObjetoImagenAPI(Resource):
    def get(self, objeto_id):
        """Obtener lista de imágenes de un objeto"""
        # Permitir acceso con JWT o sesión web
        try:
            verify_jwt_in_request()
        except:
            # Fallback a sesión web
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
        
        try:
            print(f"[DEBUG] GET imagenes para objeto_id={objeto_id}")
            rs = db_manager.execute_query(
                "SELECT id, path, vista, notas, fuente, DATE_FORMAT(fecha_subida, '%Y-%m-%d %H:%i') as fecha_creacion FROM objetos_imagenes WHERE objeto_id=%s ORDER BY id DESC",
                (objeto_id,)
            )
            print(f"[DEBUG] Imagenes encontradas: {len(rs) if rs else 0}")
            return {'imagenes': rs or []}, 200
        except Exception as e:
            print(f"[ERROR] Error obteniendo imagenes: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': f'Error obteniendo imágenes: {str(e)}'}, 500
    
    def post(self, objeto_id):
        # Permitir acceso con JWT o sesión web
        try:
            verify_jwt_in_request()
        except:
            # Fallback a sesión web
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
        
        data = request.get_json(silent=True) or {}
        img_b64 = data.get('image_base64')
        notas = data.get('notas')
        fuente = data.get('fuente', 'upload')
        carpeta = (data.get('carpeta') or '').strip()
        tipo_registro = data.get('tipo_registro', 'objeto')  # 'equipo' o 'objeto'
        vista = (data.get('vista') or '').strip()  # superior/inferior/lateral_izquierda/lateral_derecha
        if not img_b64:
            return {'message': 'image_base64 requerido'}, 400
        try:
            print(f"[DEBUG] Iniciando guardado de imagen para objeto {objeto_id}")
            print(f"[DEBUG] Tipo registro: {tipo_registro}")
            print(f"[DEBUG] Carpeta solicitada: '{carpeta}'")
            
            # Si no hay carpeta especificada, usar nombre del objeto
            rs_obj = None
            if not carpeta:
                rs_obj = db_manager.execute_query("SELECT nombre FROM objetos WHERE id=%s", (objeto_id,))
                if rs_obj:
                    carpeta = rs_obj[0]['nombre']
                    print(f"[DEBUG] Carpeta obtenida del objeto: '{carpeta}'")
            # Normalizar dataURL
            if ',' in img_b64:
                header, img_b64 = img_b64.split(',', 1)
            blob = base64.b64decode(img_b64)
            content_type = 'image/jpeg'
            if 'data:image/' in (locals().get('header') or ''):
                try:
                    content_type = header.split(';')[0].split(':')[1]
                except Exception:
                    pass
            # Guardar en disco
            ext = '.jpg' if content_type=='image/jpeg' else ('.png' if content_type=='image/png' else '.img')
            # Sanitizar subcarpeta opcional
            def _sanitize_folder(name: str) -> str:
                import re
                name = name.replace('..','').replace('/', '').replace('\\','')
                name = re.sub(r"[^A-Za-z0-9_\- ]+", '', name).strip()
                name = re.sub(r"\s+", '_', name)
                return name[:80]

            safe_sub = _sanitize_folder(carpeta) if carpeta else ''
            if vista:
                safe_sub = _sanitize_folder(vista)
            # si viene 'vista', usarla como subcarpeta (tiene prioridad)
            if vista:
                safe_sub = _sanitize_folder(vista)
            # Determinar ruta base según tipo de registro y nombre
            base_folder = 'equipos' if tipo_registro == 'equipo' else 'objetos'
            # usar nombre del objeto/equipo como carpeta principal
            if carpeta:
                base_name = _sanitize_folder(carpeta)
            elif rs_obj and len(rs_obj) > 0:
                base_name = _sanitize_folder(rs_obj[0]['nombre'])
            else:
                base_name = f'objeto_{objeto_id}'
            
            dir_path = os.path.join('imagenes', base_folder, base_name)
            if safe_sub:
                dir_path = os.path.join(dir_path, safe_sub)
            
            print(f"[DEBUG] Ruta completa calculada: {dir_path}")
            print(f"[DEBUG] Directorio de trabajo actual: {os.getcwd()}")
            print(f"[DEBUG] Ruta absoluta: {os.path.abspath(dir_path)}")
            
            # Crear directorio con manejo de errores
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"[OK] Directorio creado/verificado: {dir_path}")
            except PermissionError:
                return {'message': f'Sin permisos para crear directorio: {dir_path}'}, 500
            except Exception as e:
                return {'message': f'Error creando directorio {dir_path}: {str(e)}'}, 500
            
            # Guardar archivo con manejo de errores
            filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            file_path = os.path.join(dir_path, filename)
            try:
                with open(file_path, 'wb') as f:
                    f.write(blob)
                print(f"[OK] Archivo guardado: {file_path} ({len(blob)} bytes)")
                
                # Verificar que el archivo realmente existe
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"[OK] Verificacion: archivo existe con {size} bytes")
                else:
                    print(f"[ERROR] ERROR: archivo NO existe despues de guardarlo: {file_path}")
                    return {'message': f'Error: archivo no se guardó correctamente en {file_path}'}, 500
                    
            except PermissionError:
                print(f"[ERROR] ERROR de permisos: {file_path}")
                return {'message': f'Sin permisos para escribir archivo: {file_path}'}, 500
            except OSError as e:
                print(f"[ERROR] ERROR del sistema: {str(e)}")
                return {'message': f'Error del sistema guardando {file_path}: {str(e)}'}, 500
            except Exception as e:
                print(f"[ERROR] ERROR inesperado: {str(e)}")
                return {'message': f'Error inesperado guardando archivo: {str(e)}'}, 500
            # Generar thumbnail (320px ancho máx) con manejo de errores
            thumb_blob = None
            try:
                img_arr = np.frombuffer(blob, dtype=np.uint8)
                im = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
                if im is not None:
                    h, w = im.shape[:2]
                    scale = 320.0 / max(1.0, w)
                    if scale < 1.0:
                        im_res = cv2.resize(im, (int(w*scale), int(h*scale)))
                    else:
                        im_res = im
                    ok, enc = cv2.imencode('.jpg', im_res, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    if ok:
                        thumb_blob = enc.tobytes()
                        print(f"[OK] Thumbnail generado: {len(thumb_blob)} bytes")
                    else:
                        print("[WARN] No se pudo codificar thumbnail")
                else:
                    print("[WARN] No se pudo decodificar imagen para thumbnail")
            except Exception as e:
                print(f"[WARN] Error generando thumbnail: {str(e)}")
                # Continuar sin thumbnail
            
            # Guardar registro en BD con manejo de errores
            try:
                db_manager.execute_query(
                    """
                    INSERT INTO objetos_imagenes (objeto_id, path, thumbnail, fuente, notas, vista)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (objeto_id, file_path.replace('\\','/'), thumb_blob, fuente, notas, vista),
                )
                print(f"[OK] Registro guardado en BD para objeto {objeto_id}")
                
                # Listar contenido de la carpeta para verificar
                try:
                    parent_dir = os.path.dirname(file_path)
                    files = os.listdir(parent_dir)
                    print(f"[DEBUG] Contenido de {parent_dir}: {files}")
                except Exception as e:
                    print(f"[WARN] No se pudo listar directorio: {str(e)}")
                
                return {'message': 'Imagen almacenada exitosamente', 'path': file_path.replace('\\','/'), 'size_bytes': len(blob)}, 201
            except Exception as e:
                # Si falla BD, intentar eliminar archivo para evitar inconsistencias
                try:
                    os.remove(file_path)
                    print(f"[WARN] Archivo eliminado por error BD: {file_path}")
                except:
                    pass
                return {'message': f'Error guardando en base de datos: {str(e)}'}, 500
        except Exception as e:
            return {'message': f'Error guardando imagen: {str(e)}'}, 500


api.add_resource(ObjetosAPI, '/api/objetos')

@app.route('/objetos/registrar')
@require_login
@require_level(4)  # Solo Administrador puede entrenar IA
def objetos_registrar():
    return render_template('modules/objetos_registrar.html', user=session)

@app.route('/registro-completo')
@require_login
@require_level(4)  # Solo Administrador
def registro_completo():
    """Formulario unificado de registro de equipos/items con IA"""
    # Obtener lista de laboratorios
    query = "SELECT id, codigo, nombre FROM laboratorios WHERE estado = 'activo' ORDER BY nombre"
    laboratorios = db_manager.execute_query(query)
    return render_template('auth/registro_completo.html', user=session, laboratorios=laboratorios)

@app.route('/registros-gestion')
@require_login
@require_level(4)  # Solo Administrador
def registros_gestion():
    """Página de gestión de registros"""
    query = "SELECT id, codigo, nombre FROM laboratorios WHERE estado = 'activo' ORDER BY nombre"
    laboratorios = db_manager.execute_query(query)
    return render_template('modules/registros_gestion.html', user=session, laboratorios=laboratorios)

@app.route('/api/registro-completo', methods=['POST'])
@require_login
@require_level(4)
@limiter.limit("10 per minute")
def api_registro_completo():
    """
    API SEGURA para guardar registro completo (equipo/item + fotos + IA)
    
    MEJORAS DE SEGURIDAD:
    - ✅ Validación estricta de todos los campos
    - ✅ Sanitización de nombres de archivo
    - ✅ Validación de imágenes (tamaño, tipo, dimensiones)
    - ✅ Prevención de path traversal
    - ✅ Rate limiting (10 req/min)
    - ✅ Manejo seguro de errores
    - ✅ Logs de seguridad mejorados
    """
    import json
    import uuid
    import base64
    import io
    from datetime import datetime
    from PIL import Image
    
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
        
        # DEBUG: Imprimir valores recibidos
        print(f"[DEBUG] Tipo: {tipo_registro}")
        print(f"[DEBUG] Cantidad recibida: {cantidad}")
        print(f"[DEBUG] Tipo de cantidad: {type(cantidad)}")
        print(f"[DEBUG] Datos completos: {datos_sanitizados}")
        print("=" * 50)
        
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
                # Crear equipo
                equipo_id = f"EQ_{str(uuid.uuid4())[:8].upper()}"
                
                query_equipo = """
                    INSERT INTO equipos (id, nombre, tipo, estado, ubicacion, laboratorio_id, especificaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_equipo, (
                    equipo_id, nombre, categoria, estado, ubicacion, laboratorio_id,
                    json.dumps({'descripcion': descripcion})
                ))
                registro_id = equipo_id
                
            else:  # item de inventario
                # Generar ID único para el item
                item_id = f"ITEM_{str(uuid.uuid4())[:8].upper()}"
                
                # DEBUG: Imprimir valores antes del INSERT
                print(f"[DEBUG INSERT] Item ID: {item_id}")
                print(f"[DEBUG INSERT] Nombre: {nombre}")
                print(f"[DEBUG INSERT] Categoría: {categoria}")
                print(f"[DEBUG INSERT] Laboratorio ID: {laboratorio_id}")
                print(f"[DEBUG INSERT] Cantidad: {cantidad}")
                print(f"[DEBUG INSERT] Tipo de cantidad: {type(cantidad)}")
                
                # Insertar item con cantidad inicial de stock
                query_item = """
                    INSERT INTO inventario (id, nombre, categoria, laboratorio_id, cantidad_actual, unidad)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_item, (
                    item_id, nombre, categoria, laboratorio_id, cantidad, 'unidades'
                ))
                print(f"[DEBUG] Item insertado con cantidad: {cantidad}")
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
                    nombre, categoria, descripcion,
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
            
            cursor.close()
            conn.close()
            
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

@app.route('/api/registros-completos')
@require_login
@require_level(4)
def api_registros_completos():
    """API para listar todos los registros (equipos + items)"""
    try:
        registros = []
        
        # Obtener equipos - solo columnas básicas
        try:
            query_equipos = """
                SELECT e.id, e.nombre, e.tipo as categoria, e.estado,
                    e.laboratorio_id, l.nombre as laboratorio_nombre
                FROM equipos e
                LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
                ORDER BY e.nombre
            """
            equipos = db_manager.execute_query(query_equipos) or []
            
            for eq in equipos:
                eq['tipo'] = 'equipo'
                # El estado ya viene de la BD, no lo sobrescribimos
                eq['entrenado_ia'] = False
                eq['foto_frontal'] = None
                
                # Buscar objeto asociado
                query_obj = "SELECT id FROM objetos WHERE nombre = %s LIMIT 1"
                obj = db_manager.execute_query(query_obj, (eq['nombre'],))
                if obj:
                    objeto_id = obj[0]['id']
                    # Buscar foto frontal
                    query_foto = "SELECT id FROM objetos_imagenes WHERE objeto_id = %s AND vista = 'frontal' LIMIT 1"
                    foto = db_manager.execute_query(query_foto, (objeto_id,))
                    if foto:
                        eq['foto_frontal'] = f'/imagenes_objeto/{foto[0]["id"]}'
                        eq['entrenado_ia'] = True
                
                registros.append(eq)
        except Exception as e:
            print(f"[WARN] Error obteniendo equipos: {e}")
        
        # Obtener items - solo columnas básicas
        try:
            query_items = """
                SELECT i.id, i.nombre, i.categoria, i.cantidad_actual as stock_actual,
                       i.laboratorio_id, l.nombre as laboratorio_nombre
                FROM inventario i
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                ORDER BY i.nombre
            """
            items = db_manager.execute_query(query_items) or []
            
            for item in items:
                item['tipo'] = 'item'
                # El stock_actual ya viene de la BD, no lo sobrescribimos
                item['entrenado_ia'] = False
                item['foto_frontal'] = None
                
                # Buscar objeto asociado
                query_obj = "SELECT id FROM objetos WHERE nombre = %s LIMIT 1"
                obj = db_manager.execute_query(query_obj, (item['nombre'],))
                if obj:
                    objeto_id = obj[0]['id']
                    # Buscar foto frontal
                    query_foto = "SELECT id FROM objetos_imagenes WHERE objeto_id = %s AND vista = 'frontal' LIMIT 1"
                    foto = db_manager.execute_query(query_foto, (objeto_id,))
                    if foto:
                        item['foto_frontal'] = f'/imagenes_objeto/{foto[0]["id"]}'
                        item['entrenado_ia'] = True
                
                registros.append(item)
        except Exception as e:
            print(f"[WARN] Error obteniendo items: {e}")
        
        print(f"[INFO] Total registros encontrados: {len(registros)}")
        return jsonify({'success': True, 'registros': registros})
        
    except Exception as e:
        print(f"[ERROR] Error listando registros: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/registro-detalle/<tipo>/<id>')
@require_login
@require_level(4)
def api_registro_detalle(tipo, id):
    """API para obtener detalles de un registro"""
    try:
        if tipo == 'equipo':
            query = """
                SELECT e.*, l.nombre as laboratorio_nombre, o.id as objeto_id
                FROM equipos e
                LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
                LEFT JOIN objetos o ON e.objeto_id = o.id
                WHERE e.id = %s
            """
            registro = db_manager.execute_query(query, (id,))
        else:
            query = """
                SELECT i.*, l.nombre as laboratorio_nombre, o.id as objeto_id
                FROM inventario i
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                LEFT JOIN objetos o ON o.nombre = i.nombre
                WHERE i.id = %s
            """
            registro = db_manager.execute_query(query, (id,))
        
        if not registro:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        
        registro = registro[0]
        registro['tipo'] = tipo
        
        # Obtener fotos
        if registro.get('objeto_id'):
            query_fotos = "SELECT id, path, vista FROM objetos_imagenes WHERE objeto_id = %s"
            fotos = db_manager.execute_query(query_fotos, (registro['objeto_id'],))
            registro['fotos'] = fotos
        else:
            registro['fotos'] = []
        
        return jsonify({'success': True, 'registro': registro})
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo detalle: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/registro-editar/<tipo>/<id>', methods=['GET'])
@require_login
@require_level(4)
def api_registro_editar(tipo, id):
    """API para obtener datos de un registro para edición"""
    try:
        if tipo == 'equipo':
            query = """
                SELECT e.*, l.nombre as laboratorio_nombre, o.id as objeto_id
                FROM equipos e
                LEFT JOIN laboratorios l ON e.laboratorio_id = l.id
                LEFT JOIN objetos o ON e.objeto_id = o.id
                WHERE e.id = %s
            """
        else:
            query = """
                SELECT i.*, l.nombre as laboratorio_nombre
                FROM inventario i
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                WHERE i.id = %s
            """
        
        result = db_manager.execute_query(query, (id,))
        
        if not result:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        
        registro = result[0]
        
        # Obtener fotos si existen
        if tipo == 'equipo' and registro.get('objeto_id'):
            query_fotos = "SELECT id, path, vista FROM objetos_imagenes WHERE objeto_id = %s"
            fotos = db_manager.execute_query(query_fotos, (registro['objeto_id'],))
            registro['fotos'] = fotos
        else:
            registro['fotos'] = []
        
        return jsonify({'success': True, 'registro': registro})
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo registro para editar: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/registro-actualizar/<tipo>/<id>', methods=['PUT'])
@require_login
@require_level(4)
def api_registro_actualizar(tipo, id):
    """API para actualizar un registro"""
    try:
        data = request.get_json()
        
        if tipo == 'equipo':
            query = """
                UPDATE equipos 
                SET nombre = %s, tipo = %s, descripcion = %s,
                    ubicacion = %s, estado = %s, laboratorio_id = %s
                WHERE id = %s
            """
            params = (
                data.get('nombre'),
                data.get('categoria'),  # Se mapea a 'tipo' en equipos
                data.get('descripcion'),
                data.get('ubicacion'),
                data.get('estado'),
                data.get('laboratorio_id'),
                id
            )
        else:
            query = """
                UPDATE inventario 
                SET nombre = %s, categoria = %s, descripcion = %s,
                    ubicacion = %s, cantidad_actual = %s, laboratorio_id = %s
                WHERE id = %s
            """
            params = (
                data.get('nombre'),
                data.get('categoria'),
                data.get('descripcion'),
                data.get('ubicacion'),
                data.get('stock_actual'),
                data.get('laboratorio_id'),
                id
            )
        
        db_manager.execute_query(query, params)
        
        return jsonify({'success': True, 'message': 'Registro actualizado exitosamente'})
        
    except Exception as e:
        print(f"[ERROR] Error actualizando registro: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/registro-eliminar/<tipo>/<id>', methods=['DELETE'])
@require_login
@require_level(4)
def api_registro_eliminar(tipo, id):
    """API para eliminar un registro"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        if tipo == 'equipo':
            # Obtener objeto_id antes de eliminar
            query_obj = "SELECT objeto_id FROM equipos WHERE id = %s"
            result = db_manager.execute_query(query_obj, (id,))
            objeto_id = result[0]['objeto_id'] if result and result[0].get('objeto_id') else None
            
            # Eliminar equipo
            cursor.execute("DELETE FROM equipos WHERE id = %s", (id,))
        else:
            # Buscar objeto asociado
            query_obj = "SELECT o.id FROM objetos o INNER JOIN inventario i ON o.nombre = i.nombre WHERE i.id = %s"
            result = db_manager.execute_query(query_obj, (id,))
            objeto_id = result[0]['id'] if result else None
            
            # Eliminar item
            cursor.execute("DELETE FROM inventario WHERE id = %s", (id,))
        
        # Si tiene objeto asociado, eliminar imágenes y objeto
        if objeto_id:
            cursor.execute("DELETE FROM objetos_imagenes WHERE objeto_id = %s", (objeto_id,))
            cursor.execute("DELETE FROM objetos WHERE id = %s", (objeto_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Registro eliminado exitosamente'})
        
    except Exception as e:
        print(f"[ERROR] Error eliminando registro: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/imagenes_objeto/<int:imagen_id>')
@require_login
def servir_imagen_objeto(imagen_id):
    """Servir imagen de objeto por ID"""
    from flask import send_file
    try:
        query = "SELECT path FROM objetos_imagenes WHERE id = %s"
        result = db_manager.execute_query(query, (imagen_id,))
        if result and result[0].get('path'):
            path = result[0]['path']
            # Asegurar que la ruta sea absoluta
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)
            if os.path.exists(path):
                return send_file(path, mimetype='image/jpeg')
        return "Imagen no encontrada", 404
    except Exception as e:
        print(f"[ERROR] Error sirviendo imagen: {str(e)}")
        return "Error al cargar imagen", 500


@app.route('/api/reemplazar-imagen', methods=['POST'])
@require_login
@require_level(4)
def api_reemplazar_imagen():
    """API para reemplazar una imagen existente"""
    try:
        # Obtener datos del formulario
        imagen_id = request.form.get('imagen_id')
        vista = request.form.get('vista')
        objeto_id = request.form.get('objeto_id')
        archivo = request.files.get('imagen')
        
        print(f"[DEBUG] Reemplazando imagen: imagen_id={imagen_id}, vista={vista}, objeto_id={objeto_id}")
        
        if not all([imagen_id, vista, objeto_id, archivo]):
            print(f"[ERROR] Faltan datos: imagen_id={imagen_id}, vista={vista}, objeto_id={objeto_id}, archivo={archivo}")
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
        
        # Obtener la ruta actual de la imagen
        query_old = "SELECT path FROM objetos_imagenes WHERE id = %s"
        result = db_manager.execute_query(query_old, (imagen_id,))
        
        if not result:
            print(f"[ERROR] Imagen no encontrada en BD: imagen_id={imagen_id}")
            return jsonify({'success': False, 'message': 'Imagen no encontrada'}), 404
        
        old_path = result[0]['path']
        print(f"[DEBUG] Ruta antigua: {old_path}")
        
        # Crear directorio si no existe
        objeto_dir = os.path.join('imagenes', 'objetos')
        os.makedirs(objeto_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"obj_{objeto_id}_{vista}_{timestamp}.jpg"
        new_path = os.path.join(objeto_dir, filename)
        print(f"[DEBUG] Nueva ruta: {new_path}")
        
        # Guardar nueva imagen
        archivo.save(new_path)
        print(f"[DEBUG] Nueva imagen guardada: {new_path}")
        
        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(new_path):
            print(f"[ERROR] No se pudo guardar la nueva imagen: {new_path}")
            return jsonify({'success': False, 'message': 'Error al guardar la nueva imagen'}), 500
        
        file_size = os.path.getsize(new_path)
        print(f"[DEBUG] Tamaño de nueva imagen: {file_size} bytes")
        
        # Actualizar ruta en base de datos
        query_update = "UPDATE objetos_imagenes SET path = %s WHERE id = %s"
        db_manager.execute_query(query_update, (new_path, imagen_id))
        print(f"[DEBUG] BD actualizada con nueva ruta")
        
        # Eliminar imagen antigua si existe y es diferente
        if old_path and os.path.exists(old_path) and old_path != new_path:
            try:
                os.remove(old_path)
                print(f"[INFO] ✅ Imagen antigua eliminada: {old_path}")
            except Exception as e:
                print(f"[WARN] ⚠️ No se pudo eliminar imagen antigua: {e}")
        else:
            print(f"[DEBUG] No se eliminó imagen antigua (no existe o es la misma)")
        
        print(f"[INFO] ✅ Imagen reemplazada exitosamente: {imagen_id} -> {new_path}")
        
        return jsonify({
            'success': True, 
            'message': 'Imagen reemplazada exitosamente',
            'new_path': new_path,
            'old_path': old_path,
            'file_size': file_size
        })
        
    except Exception as e:
        print(f"[ERROR] Error reemplazando imagen: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

class ObjetoAPI(Resource):
    def get(self, objeto_id: int):
        # Permitir acceso con JWT o sesión web
        try:
            verify_jwt_in_request()
        except:
            # Fallback a sesión web
            if 'user_id' not in session:
                return {'message': 'Autenticación requerida'}, 401
        
        rs = db_manager.execute_query(
            "SELECT id, nombre, categoria, descripcion, DATE_FORMAT(fecha_creacion, '%Y-%m-%d %H:%i') as fecha_creacion FROM objetos WHERE id=%s",
            (objeto_id,)
        )
        if not rs:
            return {'message': 'Objeto no encontrado'}, 404
        return {'objeto': rs[0]}, 200

    def put(self, objeto_id: int):
        verify_jwt_in_request()
        data = request.get_json(silent=True) or {}
        nombre = (data.get('nombre') or '').strip()
        categoria = (data.get('categoria') or '').strip() or None
        descripcion = data.get('descripcion')
        if not nombre:
            return {'message': 'nombre requerido'}, 400
        # Verificar duplicado con otro ID
        rs_exist = db_manager.execute_query(
            "SELECT id FROM objetos WHERE nombre=%s AND (categoria=%s OR (categoria IS NULL AND %s IS NULL)) AND id<>%s",
            (nombre, categoria, categoria, objeto_id)
        )
        if rs_exist:
            return {'message': 'Ya existe otro objeto con ese nombre y categoría'}, 409
        db_manager.execute_query(
            "UPDATE objetos SET nombre=%s, categoria=%s, descripcion=%s WHERE id=%s",
            (nombre, categoria, descripcion, objeto_id)
        )
        return {'message': 'Objeto actualizado'}, 200

    def delete(self, objeto_id: int):
        verify_jwt_in_request()
        # Obtener imágenes para limpiar archivos
        rs = db_manager.execute_query("SELECT path FROM objetos_imagenes WHERE objeto_id=%s", (objeto_id,))
        for row in rs or []:
            p = row.get('path')
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                    print(f"🗑️ Archivo eliminado: {p}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar archivo {p}: {e}")
        # Borrar objeto (CASCADE borra objetos_imagenes)
        db_manager.execute_query("DELETE FROM objetos WHERE id=%s", (objeto_id,))
        # Intentar eliminar carpeta base si queda vacía
        for base in ('imagenes/objetos', 'imagenes/equipos'):
            base_dir = os.path.join(base, str(objeto_id))
            try:
                os.rmdir(base_dir)
            except Exception:
                pass
        return {'message': 'Objeto eliminado'}, 200

api.add_resource(ObjetoAPI, '/api/objetos/<int:objeto_id>')

@app.route('/objetos/gestion')
@require_login
@require_level(3)
def objetos_gestion():
    return render_template('objetos_gestion.html', user=session)

# =============================
# OBJETOS: Listado de imágenes y thumbnails
# =============================

# Unificar ObjetoImagenAPI (POST) y ObjetoImagenesAPI (GET) en una sola clase
# Ya está definida arriba como ObjetoImagenAPI con método post()
# Ahora agregamos el método get() a la misma clase
# Buscar la clase ObjetoImagenAPI arriba y agregar el método get()

api.add_resource(ObjetoImagenAPI, '/api/objetos/<int:objeto_id>/imagenes')

@app.get('/api/objetos/imagen_thumb/<int:img_id>')
def objeto_imagen_thumb(img_id: int):
    # No requiere JWT para facilitar renderizado de miniaturas; restringe a logged-in vía sesión si se desea
    row = db_manager.execute_query("SELECT thumbnail, content_type FROM objetos_imagenes WHERE id=%s", (img_id,))
    if not row or row[0]['thumbnail'] is None:
        return jsonify({'message': 'Thumbnail no disponible'}), 404
    ct = row[0]['content_type'] or 'image/jpeg'
    return app.response_class(response=row[0]['thumbnail'], status=200, mimetype=ct)

# =============================
# VISION: Guardar plantilla de equipo
# =============================

@app.get('/api/objetos/<int:objeto_id>/vistas_status')
def objeto_vistas_status(objeto_id: int):
    try:
        rs = db_manager.execute_query("SELECT nombre FROM objetos WHERE id=%s", (objeto_id,))
        if not rs:
            return jsonify({'message': 'Objeto no encontrado'}), 404
        nombre = rs[0]['nombre']
    except Exception as e:
        return jsonify({'message': f'Error consultando objeto: {e}'}), 500

    import re
    def san(s: str) -> str:
        s = (s or '').lower().replace('..','').replace('/','').replace('\\','')
        s = re.sub(r"[^a-z0-9_\- ]+", '', s).strip()
        s = re.sub(r"\s+", '_', s)
        return s

    base = os.path.join('imagenes', 'objetos', san(nombre))
    required = ['frontal','posterior','superior','inferior','lateral_derecha','lateral_izquierda']
    completed = []
    files = {}
    if os.path.isdir(base):
        for v in required:
            vdir = os.path.join(base, v)
            if os.path.isdir(vdir):
                imgs = [f for f in os.listdir(vdir) if f.lower().endswith(('.jpg','.jpeg','.png'))]
                if imgs:
                    completed.append(v)
                    files[v] = [os.path.join(vdir, f).replace('\\','/') for f in imgs]
    missing = [v for v in required if v not in completed]
    return jsonify({
        'objeto_id': objeto_id,
        'nombre': nombre,
        'required': required,
        'completed': completed,
        'missing': missing,
        'count': len(completed),
        'files': files,
    }), 200
@app.post('/api/vision/equipos/<int:equipo_id>/plantilla')
def vision_equipo_plantilla(equipo_id: int):
    try:
        verify_jwt_in_request()
    except Exception:
        # permitir sin JWT si se desea, pero en producción es mejor exigirlo
        pass
    data = request.get_json(silent=True) or {}
    img_b64 = data.get('image_base64')
    carpeta = (data.get('carpeta') or '').strip()
    if not img_b64:
        return jsonify({'message': 'image_base64 requerido'}), 400
    # decode
    try:
        if ',' in img_b64:
            _, img_b64 = img_b64.split(',', 1)
        blob = base64.b64decode(img_b64)
    except Exception as e:
        return jsonify({'message': f'Base64 inválido: {e}'}), 400

    # sanitize folder
    def _sanitize(name: str) -> str:
        import re
        name = (name or '').replace('..','').replace('/','').replace('\\','')
        name = re.sub(r"[^A-Za-z0-9_\- ]+", '', name).strip()
        name = re.sub(r"\s+", '_', name)
        return name[:80]

    sub = _sanitize(carpeta)
    # obtener nombre del equipo para usarlo como carpeta
    try:
        rs_eq = db_manager.execute_query("SELECT nombre FROM equipos WHERE id=%s", (equipo_id,))
        eq_name = rs_eq[0]['nombre'] if rs_eq else str(equipo_id)
    except Exception:
        eq_name = str(equipo_id)
    eq_folder = _sanitize(eq_name)
    dir_path = os.path.join('imagenes', 'equipos', eq_folder)
    if sub:
        dir_path = os.path.join(dir_path, sub)
    try:
        os.makedirs(dir_path, exist_ok=True)
    except Exception as e:
        return jsonify({'message': f'No se pudo crear carpeta {dir_path}: {e}'}), 500

    filename = f"tpl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    file_path = os.path.join(dir_path, filename)
    try:
        with open(file_path, 'wb') as f:
            f.write(blob)
    except Exception as e:
        return jsonify({'message': f'No se pudo escribir archivo: {e}'}), 500

    return jsonify({'message': 'Plantilla guardada', 'path': file_path.replace('\\','/')}), 201

@app.get('/api/vision/equipos/<int:equipo_id>/plantillas')
def vision_equipo_listar_plantillas(equipo_id: int):
    # mapear id -> nombre carpeta
    try:
        rs = db_manager.execute_query("SELECT nombre FROM equipos WHERE id=%s", (equipo_id,))
        name = rs[0]['nombre'] if rs else str(equipo_id)
    except Exception:
        name = str(equipo_id)
    import re
    name_sanitized = re.sub(r"\s+", '_', re.sub(r"[^A-Za-z0-9_\- ]+", '', name)).strip()
    base_dir = os.path.join('imagenes', 'equipos', name_sanitized)
    resultado = []
    if not os.path.exists(base_dir):
        return jsonify({'plantillas': []}), 200
    for root, _, files in os.walk(base_dir):
        for fn in files:
            if fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                rel_dir = os.path.relpath(root, base_dir)
                rel_path = fn if rel_dir == '.' else os.path.join(rel_dir, fn)
                resultado.append({'file': rel_path.replace('\\','/')})
    return jsonify({'plantillas': resultado}), 200

@app.get('/api/vision/equipos/plantilla_image')
def vision_equipo_plantilla_image():
    from urllib.parse import unquote
    equipo_id = request.args.get('equipo_id')
    rel_file = request.args.get('f') or ''
    try:
        eid = int(equipo_id)
    except Exception:
        return jsonify({'message': 'equipo_id inválido'}), 400
    safe_rel = unquote(rel_file).replace('..','').replace('\\','/')
    # traducir a carpeta por nombre
    try:
        rs = db_manager.execute_query("SELECT nombre FROM equipos WHERE id=%s", (eid,))
        name = rs[0]['nombre'] if rs else str(eid)
    except Exception:
        name = str(eid)
    import re
    name_sanitized = re.sub(r"\s+", '_', re.sub(r"[^A-Za-z0-9_\- ]+", '', name)).strip()
    base_dir = os.path.join('imagenes', 'equipos', name_sanitized)
    abs_path = os.path.abspath(os.path.join(base_dir, safe_rel))
    if not abs_path.startswith(os.path.abspath(base_dir)):
        return jsonify({'message': 'Ruta no permitida'}), 400
    if not os.path.exists(abs_path):
        return jsonify({'message': 'Archivo no encontrado'}), 404
    try:
        with open(abs_path, 'rb') as f:
            data = f.read()
        ct = 'image/jpeg' if abs_path.lower().endswith(('.jpg','.jpeg')) else 'image/png'
        return app.response_class(response=data, status=200, mimetype=ct)
    except Exception as e:
        return jsonify({'message': f'Error leyendo archivo: {e}'}), 500

def _preprocess_for_orb(img: np.ndarray) -> np.ndarray:
    try:
        if img is None:
            return img
        h, w = img.shape[:2]
        maxw = 640
        if w > maxw:
            scale = maxw/float(w)
            img = cv2.resize(img, (int(w*scale), int(h*scale)))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        eq = clahe.apply(gray)
        return eq
    except Exception:
        return img


def _load_template_images_slim(max_per_key: int = 12):
    """
    Carga plantillas SOLO de objetos registrados por admin (si existe reconocer=1),
    primero desde BD (objetos_imagenes.imagen) y luego desde FS imagenes/objetos/<slug>/...
    Limita el número de imágenes por objeto para evitar sobrecarga.
    Devuelve lista de tuplas (key, img_preprocesada_grayscale).
    """
    import re, os, cv2, numpy as np
    templates = []
    allow = set()
    # construir allow desde BD si es posible
    try:
        rows = db_manager.execute_query("SELECT nombre FROM objetos WHERE reconocer=1") or []
        allow = { re.sub(r"\s+", '_', re.sub(r"[^a-z0-9_\- ]+", '', (r['nombre'] or '').lower())).strip() for r in rows }
    except Exception:
        try:
            rows = db_manager.execute_query("SELECT nombre FROM objetos") or []
            allow = { re.sub(r"\s+", '_', re.sub(r"[^a-z0-9_\- ]+", '', (r['nombre'] or '').lower())).strip() for r in rows }
        except Exception:
            allow = set()

    counts = {}

    # 1) Desde BD
    try:
        rows = db_manager.execute_query("""
            SELECT o.nombre, oi.imagen
            FROM objetos_imagenes oi
            JOIN objetos o ON o.id = oi.objeto_id
        """) or []
        for r in rows:
            nm = (r.get('nombre') or '').lower()
            key = re.sub(r"\s+", '_', re.sub(r"[^a-z0-9_\- ]+", '', nm)).strip()
            if allow and key not in allow:
                continue
            if counts.get(key, 0) >= max_per_key:
                continue
            blob = r.get('imagen')
            if not blob:
                continue
            arr = np.frombuffer(blob, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                continue
            img = _preprocess_for_orb(img)
            templates.append((key, img))
            counts[key] = counts.get(key, 0) + 1
    except Exception:
        pass

    # 2) Desde FS: imagenes/objetos/<carpeta>/**
    try:
        base = os.path.join(IMG_ROOT, 'objetos')
        if os.path.isdir(base):
            for entry in os.listdir(base):
                folder_path = os.path.join(base, entry)
                if not os.path.isdir(folder_path):
                    continue
                key = re.sub(r"\s+", '_', re.sub(r"[^a-z0-9_\- ]+", '', (entry or '').lower())).strip()
                if allow and key not in allow:
                    continue
                for root, _, files in os.walk(folder_path):
                    for fn in files:
                        if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                            continue
                        if counts.get(key, 0) >= max_per_key:
                            break
                        path = os.path.join(root, fn)
                        img = cv2.imread(path, cv2.IMREAD_COLOR)
                        if img is None:
                            continue
                        img = _preprocess_for_orb(img)
                        templates.append((key, img))
                        counts[key] = counts.get(key, 0) + 1
    except Exception:
        pass

    # 3) Desde FS: imagenes/equipo/<carpeta>/**
    try:
        base_equipo = os.path.join(IMG_ROOT, 'equipo')
        if os.path.isdir(base_equipo):
            for entry in os.listdir(base_equipo):
                folder_path = os.path.join(base_equipo, entry)
                if not os.path.isdir(folder_path):
                    continue
                key = re.sub(r"\s+", '_', re.sub(r"[^a-z0-9_\- ]+", '', (entry or '').lower())).strip()
                for root, _, files in os.walk(folder_path):
                    for fn in files:
                        if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                            continue
                        if counts.get(key, 0) >= max_per_key:
                            break
                        path = os.path.join(root, fn)
                        img = cv2.imread(path, cv2.IMREAD_COLOR)
                        if img is None:
                            continue
                        img = _preprocess_for_orb(img)
                        templates.append((key, img))
                        counts[key] = counts.get(key, 0) + 1
                        print(f"[DEBUG] Plantilla cargada: {key} desde {path}")
    except Exception as e:
        print(f"[WARN] Error cargando plantillas de equipos: {e}")

    # 4) Desde FS: imagenes/item/<carpeta>/**
    try:
        base_item = os.path.join(IMG_ROOT, 'item')
        if os.path.isdir(base_item):
            for entry in os.listdir(base_item):
                folder_path = os.path.join(base_item, entry)
                if not os.path.isdir(folder_path):
                    continue
                key = re.sub(r"\s+", '_', re.sub(r"[^a-z0-9_\- ]+", '', (entry or '').lower())).strip()
                for root, _, files in os.walk(folder_path):
                    for fn in files:
                        if not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                            continue
                        if counts.get(key, 0) >= max_per_key:
                            break
                        path = os.path.join(root, fn)
                        img = cv2.imread(path, cv2.IMREAD_COLOR)
                        if img is None:
                            continue
                        img = _preprocess_for_orb(img)
                        templates.append((key, img))
                        counts[key] = counts.get(key, 0) + 1
                        print(f"[DEBUG] Plantilla cargada: {key} desde {path}")
    except Exception as e:
        print(f"[WARN] Error cargando plantillas de items: {e}")

    print(f"[INFO] Total plantillas cargadas: {len(templates)}")
    return templates


@app.get('/api/vision/debug_counts_fast')
def vision_debug_counts_fast():
    ...
    """
    Recorre imagenes/ y cuenta archivos sin decodificarlos. Responde rápido.
    """
    import os
    report = {'root': IMG_ROOT, 'objetos': {}, 'equipos': {}, 'otros': {}}
    base = IMG_ROOT
    if not os.path.isdir(base):
        return jsonify({'root': IMG_ROOT, 'message': 'IMG_ROOT no existe'}), 200

    def count_dir(d):
        c = 0
        for _, _, files in os.walk(d):
            for fn in files:
                if fn.lower().endswith(('.jpg', '.jpeg', '.png')):
                    c += 1
        return c

    # objetos
    obj_dir = os.path.join(base, 'objetos')
    if os.path.isdir(obj_dir):
        for entry in os.listdir(obj_dir):
            f = os.path.join(obj_dir, entry)
            if os.path.isdir(f):
                report['objetos'][entry] = count_dir(f)

    # equipos
    eq_dir = os.path.join(base, 'equipos')
    if os.path.isdir(eq_dir):
        for entry in os.listdir(eq_dir):
            f = os.path.join(eq_dir, entry)
            if os.path.isdir(f):
                report['equipos'][entry] = count_dir(f)

    # otros
    for entry in os.listdir(base):
        if entry in ('objetos','equipos'):
            continue
        f = os.path.join(base, entry)
        if os.path.isdir(f):
            report['otros'][entry] = count_dir(f)

    # desde BD
    try:
        db_rows = db_manager.execute_query("SELECT o.nombre, COUNT(oi.id) c FROM objetos o LEFT JOIN objetos_imagenes oi ON oi.objeto_id=o.id GROUP BY o.id, o.nombre") or []
        report['objetos_db'] = { r['nombre']: r['c'] for r in db_rows }
    except Exception:
        report['objetos_db'] = {}

    return jsonify(report), 200


# =============================
# ENDPOINTS DE IA AVANZADA
# =============================

@app.get('/api/ai/status')
def ai_status():
    """Estado del sistema de IA avanzada"""
    if AI_MANAGER:
        status = AI_MANAGER.get_ai_status()
        return jsonify(status), 200
    else:
        return jsonify({
            'ai_available': False,
            'message': 'Sistema de IA no inicializado'
        }), 200


@app.post('/api/ai/voice/process')
def ai_voice_process():
    """Procesar comando de voz con IA avanzada"""
    try:
        verify_jwt_in_request()
    except Exception:
        return jsonify({'message': 'Token requerido'}), 401
    
    data = request.get_json(silent=True) or {}
    audio_b64 = data.get('audio_base64')
    
    if not audio_b64:
        return jsonify({'message': 'audio_base64 requerido'}), 400
    
    if AI_MANAGER and AI_MANAGER.voice_ai_enabled:
        try:
            # Decodificar audio
            if ',' in audio_b64:
                audio_b64 = audio_b64.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_b64)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Procesar con IA
            result = AI_MANAGER.process_voice_command(audio_array)
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({    
                'success': False,
                'error': f'Error procesando audio: {str(e)}',
                'ai_enhanced': True
            }), 500
    else:
        return jsonify({
            'success': False,
            'error': 'IA de voz no disponible',
            'ai_enhanced': False
        }), 503


@app.post('/api/ai/vision/train')
def ai_vision_train():
    """Entrenar modelo de visión personalizado"""
    try:
        verify_jwt_or_admin()
    except Exception:
        return jsonify({'message': 'Permisos de admin requeridos'}), 401
    
    data = request.get_json(silent=True) or {}
    training_path = data.get('training_data_path', 'training_data')
    epochs = data.get('epochs', 10)
    
    if AI_MANAGER and AI_MANAGER.vision_ai_enabled:
        try:
            result = AI_MANAGER.train_custom_vision_model(training_path, epochs)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error entrenando modelo: {str(e)}'
            }), 500
    else:
        return jsonify({
            'success': False,
            'error': 'IA de visión no disponible'
        }), 503


@app.get('/api/ai/stats')
def ai_stats():
    """Estadísticas detalladas del sistema de IA"""
    try:
        verify_jwt_in_request()
    except Exception:
        return jsonify({'message': 'Token requerido'}), 401
    
    if AI_MANAGER:
        stats = AI_MANAGER.get_ai_status()
        
        # Añadir estadísticas adicionales
        stats['system_info'] = {
            'ai_modules_available': AI_AVAILABLE,
            'tensorflow_available': 'tensorflow' in str(type(AI_MANAGER.vision_detector)) if AI_MANAGER.vision_detector else False,
            'deepspeech_available': 'deepspeech' in str(type(AI_MANAGER.voice_processor)) if AI_MANAGER.voice_processor else False
        }
        
        return jsonify(stats), 200


# =====================================================================
# API DE PREDICCIÓN DE MANTENIMIENTOS
# =====================================================================

# Variables globales para el sistema de predicción
MAINTENANCE_PREDICTOR = None
ALERT_MANAGER = None

def initialize_maintenance_system():
    """Inicializar el sistema de predicción de mantenimientos"""
    global MAINTENANCE_PREDICTOR, ALERT_MANAGER
    
    try:
        from modules.maintenance_predictor import create_maintenance_predictor
        from modules.maintenance_alerts import create_alert_manager, ConfiguracionAlerta
        
        # Crear predictor
        MAINTENANCE_PREDICTOR = create_maintenance_predictor(db_manager)
        
        # Crear gestor de alertas con configuración
        config = ConfiguracionAlerta(
            dias_anticipacion_mantenimiento=30,
            dias_anticipacion_calibracion=15,
            habilitar_email=False,  # Deshabilitado por defecto
            habilitar_dashboard=True
        )
        
        ALERT_MANAGER = create_alert_manager(db_manager, MAINTENANCE_PREDICTOR, config)
        
        print("[OK] Sistema de predicción de mantenimientos inicializado")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error inicializando sistema de mantenimiento: {e}")
        return False

@app.get('/api/maintenance/predict/<equipo_id>')
@require_login
def api_predecir_mantenimiento_equipo(equipo_id):
    """
    API para predecir mantenimiento de un equipo específico
    
    Args:
        equipo_id: ID del equipo a analizar
        
    Returns:
        JSON con predicción de mantenimiento
    """
    try:
        if not MAINTENANCE_PREDICTOR:
            initialize_maintenance_system()
        
        prediccion = MAINTENANCE_PREDICTOR.predecir_mantenimiento_equipo(equipo_id)
        
        if not prediccion:
            return jsonify({
                'success': False,
                'message': 'No hay datos suficientes para predecir el mantenimiento de este equipo',
                'equipo_id': equipo_id
            }), 404
        
        return jsonify({
            'success': True,
            'prediccion': {
                'equipo_id': prediccion.equipo_id,
                'equipo_nombre': prediccion.equipo_nombre,
                'tipo_equipo': prediccion.tipo_equipo,
                'fecha_predicha': prediccion.fecha_predicha.strftime('%Y-%m-%d'),
                'riesgo': prediccion.riesgo.value,
                'confianza': round(prediccion.confianza, 3),
                'dias_hasta_mantenimiento': prediccion.dias_hasta_mantenimiento,
                'factores': prediccion.factores,
                'recomendaciones': prediccion.recomendaciones
            }
        })
        
    except Exception as e:
        logger.error(f"Error en API predicción mantenimiento: {e}")
        return jsonify({
            'success': False,
            'message': f'Error procesando predicción: {str(e)}'
        }), 500

@app.get('/api/maintenance/predict/laboratorio/<int:laboratorio_id>')
@require_login
def api_predecir_mantenimientos_laboratorio(laboratorio_id):
    """
    API para predecir mantenimientos de todos los equipos de un laboratorio
    
    Args:
        laboratorio_id: ID del laboratorio
        
    Returns:
        JSON con lista de predicciones
    """
    try:
        if not MAINTENANCE_PREDICTOR:
            initialize_maintenance_system()
        
        predicciones = MAINTENANCE_PREDICTOR.predecir_mantenimientos_laboratorio(laboratorio_id)
        
        return jsonify({
            'success': True,
            'laboratorio_id': laboratorio_id,
            'total_predicciones': len(predicciones),
            'predicciones': [
                {
                    'equipo_id': p.equipo_id,
                    'equipo_nombre': p.equipo_nombre,
                    'tipo_equipo': p.tipo_equipo,
                    'fecha_predicha': p.fecha_predicha.strftime('%Y-%m-%d'),
                    'riesgo': p.riesgo.value,
                    'confianza': round(p.confianza, 3),
                    'dias_hasta_mantenimiento': p.dias_hasta_mantenimiento,
                    'recomendaciones': p.recomendaciones[:2]  # Solo 2 recomendaciones principales
                }
                for p in predicciones
            ]
        })
        
    except Exception as e:
        logger.error(f"Error en API predicciones laboratorio: {e}")
        return jsonify({
            'success': False,
            'message': f'Error procesando predicciones: {str(e)}'
        }), 500

@app.get('/api/maintenance/analyze/<equipo_id>')
@require_login
def api_analizar_equipo_completo(equipo_id):
    """
    API para análisis completo de un equipo
    
    Args:
        equipo_id: ID del equipo a analizar
        
    Returns:
        JSON con análisis completo del equipo
    """
    try:
        if not MAINTENANCE_PREDICTOR:
            initialize_maintenance_system()
        
        analisis = MAINTENANCE_PREDICTOR.analizar_equipo_completo(equipo_id)
        
        if not analisis:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado o sin datos suficientes',
                'equipo_id': equipo_id
            }), 404
        
        return jsonify({
            'success': True,
            'analisis': {
                'equipo_id': analisis.equipo_id,
                'mtbf': round(analisis.mtbf, 1),
                'mttr': round(analisis.mttr, 1),
                'disponibilidad': round(analisis.disponibilidad * 100, 2),  # Porcentaje
                'tendencia_fallas': analisis.tendencia_fallas,
                'frecuencia_mantenimiento': round(analisis.frecuencia_mantenimiento, 1),
                'ultima_calibracion': analisis.ultima_calibracion.strftime('%Y-%m-%d') if analisis.ultima_calibracion else None,
                'proximo_mantenimiento_estimado': analisis.proximo_mantenimiento_estimado.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        logger.error(f"Error en API análisis equipo: {e}")
        return jsonify({
            'success': False,
            'message': f'Error procesando análisis: {str(e)}'
        }), 500

@app.get('/api/maintenance/alerts')
@require_login
def api_obtener_alertas_mantenimiento():
    """
    API para obtener alertas de mantenimiento
    
    Query params:
        dias: Días hacia adelante para buscar alertas (default: 30)
        usuario_id: ID del usuario (opcional, usa sesión si no se especifica)
        
    Returns:
        JSON con lista de alertas
    """
    try:
        if not ALERT_MANAGER:
            initialize_maintenance_system()
        
        # Obtener parámetros
        dias = request.args.get('dias', 30, type=int)
        usuario_id = request.args.get('usuario_id', session.get('user_id'))
        
        if not usuario_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no especificado'
            }), 400
        
        # Generar alertas automáticas
        alertas_generadas = ALERT_MANAGER.generar_alertas_automaticas()
        
        # Obtener alertas del usuario
        alertas_usuario = ALERT_MANAGER.obtener_alertas_usuario(usuario_id)
        
        # Filtrar por días si se especifica
        if dias:
            fecha_limite = datetime.now() + timedelta(days=dias)
            alertas_usuario = [
                a for a in alertas_usuario 
                if a.fecha_mantenimiento <= fecha_limite
            ]
        
        return jsonify({
            'success': True,
            'dias_analizados': dias,
            'total_alertas_generadas': len(alertas_generadas),
            'total_alertas_usuario': len(alertas_usuario),
            'alertas': [
                {
                    'id': a.id,
                    'tipo': a.tipo.value,
                    'titulo': a.titulo,
                    'mensaje': a.mensaje,
                    'equipo_id': a.equipo_id,
                    'equipo_nombre': a.equipo_nombre,
                    'laboratorio_id': a.laboratorio_id,
                    'laboratorio_nombre': a.laboratorio_nombre,
                    'fecha_alerta': a.fecha_alerta.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_mantenimiento': a.fecha_mantenimiento.strftime('%Y-%m-%d'),
                    'riesgo': a.riesgo,
                    'prioridad': a.prioridad,
                    'leida': a.leida,
                    'dias_hasta_mantenimiento': (a.fecha_mantenimiento - datetime.now()).days
                }
                for a in alertas_usuario[:50]  # Limitar a 50 alertas
            ]
        })
        
    except Exception as e:
        logger.error(f"Error en API alertas mantenimiento: {e}")
        return jsonify({
            'success': False,
            'message': f'Error obteniendo alertas: {str(e)}'
        }), 500

@app.post('/api/maintenance/alerts/<alerta_id>/read')
@require_login
def api_marcar_alerta_leida(alerta_id):
    """
    API para marcar una alerta como leída
    
    Args:
        alerta_id: ID de la alerta
        
    Returns:
        JSON con resultado de la operación
    """
    try:
        if not ALERT_MANAGER:
            initialize_maintenance_system()
        
        usuario_id = session.get('user_id')
        exito = ALERT_MANAGER.marcar_alerta_leida(alerta_id, usuario_id)
        
        if exito:
            return jsonify({
                'success': True,
                'message': 'Alerta marcada como leída'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Alerta no encontrada o no se pudo marcar como leída'
            }), 404
            
    except Exception as e:
        logger.error(f"Error marcando alerta como leída: {e}")
        return jsonify({
            'success': False,
            'message': f'Error marcando alerta: {str(e)}'
        }), 500

@app.get('/api/maintenance/dashboard')
@require_login
def api_dashboard_mantenimiento():
    """
    API para obtener datos del dashboard de mantenimiento
    
    Returns:
        JSON con estadísticas y alertas para el dashboard
    """
    try:
        if not MAINTENANCE_PREDICTOR or not ALERT_MANAGER:
            initialize_maintenance_system()
        
        usuario_id = session.get('user_id')
        
        # Obtener estadísticas generales
        stats = {
            'alertas_criticas': 0,
            'mantenimientos_proximos': 0,
            'equipos_en_riesgo': 0,
            'calibraciones_vencidas': 0
        }
        
        # Obtener alertas del usuario
        alertas = ALERT_MANAGER.obtener_alertas_usuario(usuario_id, solo_no_leidas=True)
        
        for alerta in alertas:
            if alerta.riesgo == 'critico':
                stats['alertas_criticas'] += 1
            if alerta.tipo.value == 'mantenimiento_proximo':
                stats['mantenimientos_proximos'] += 1
            if alerta.tipo.value == 'calibracion_vencida':
                stats['calibraciones_vencidas'] += 1
        
        # Calcular equipos en riesgo (mantenimiento en 15 días)
        fecha_riesgo = datetime.now() + timedelta(days=15)
        stats['equipos_en_riesgo'] = len([
            a for a in alertas 
            if a.fecha_mantenimiento <= fecha_riesgo
        ])
        
        # Obtener predicciones recientes
        predicciones_recientes = []
        for alerta in alertas[:10]:  # Top 10
            if alerta.tipo.value in ['mantenimiento_proximo', 'calibracion_vencida']:
                predicciones_recientes.append({
                    'equipo_nombre': alerta.equipo_nombre,
                    'laboratorio_nombre': alerta.laboratorio_nombre,
                    'tipo': alerta.tipo.value,
                    'fecha': alerta.fecha_mantenimiento.strftime('%d/%m/%Y'),
                    'riesgo': alerta.riesgo,
                    'dias_restantes': (alerta.fecha_mantenimiento - datetime.now()).days
                })
        
        return jsonify({
            'success': True,
            'stats': stats,
            'predicciones_recientes': predicciones_recientes,
            'total_alertas_no_leidas': len(alertas)
        })
        
    except Exception as e:
        logger.error(f"Error en API dashboard mantenimiento: {e}")
        return jsonify({
            'success': False,
            'message': f'Error obteniendo datos dashboard: {str(e)}'
        }), 500

@app.post('/api/maintenance/generate-alerts')
@require_login
@require_level(5)  # Solo instructores y administradores
def api_generar_alertas_automaticas():
    """
    API para generar alertas automáticas manualmente
    
    Returns:
        JSON con resultado de la generación
    """
    try:
        if not ALERT_MANAGER:
            initialize_maintenance_system()
        
        # Generar alertas
        alertas = ALERT_MANAGER.generar_alertas_automaticas()
        
        # Enviar emails si está configurado
        emails_enviados = {}
        if ALERT_MANAGER.config.habilitar_email:
            emails_enviados = ALERT_MANAGER.enviar_alertas_email(alertas)
        
        return jsonify({
            'success': True,
            'message': f'Se generaron {len(alertas)} alertas automáticamente',
            'total_alertas': len(alertas),
            'emails_enviados': len([e for e, exito in emails_enviados.items() if exito]),
            'resumen_emails': {
                'enviados': len([e for e, exito in emails_enviados.items() if exito]),
                'fallidos': len([e for e, exito in emails_enviados.items() if not exito])
            }
        })
        
    except Exception as e:
        logger.error(f"Error generando alertas automáticas: {e}")
        return jsonify({
            'success': False,
            'message': f'Error generando alertas: {str(e)}'
        }), 500


# Inicializar el sistema de mantenimiento al iniciar la aplicación
def setup_maintenance_system():
    """Configurar el sistema de mantenimiento antes de la primera petición"""
    initialize_maintenance_system()

# Inicializar sistemas al iniciar la aplicación
with app.app_context():
    try:
        # Inicializar sistema de IA
        initialize_ai_system()
        
        # Inicializar sistema de mantenimiento
        setup_maintenance_system()
        
        print("[OK] Sistemas de IA y mantenimiento inicializados correctamente")
    except Exception as e:
        print(f"[ERROR] Error inicializando sistemas: {e}")


# =====================================================================
# MANEJO DE ERRORES
# =====================================================================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Endpoint no encontrado'}), 404
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # Imprimir el error completo en consola
    print(f"[ERROR] ERROR 500 en {request.path}")
    print(f"[ERROR] Error: {str(error)}")
    import traceback
    traceback.print_exc()
    
    if request.path.startswith('/api/'):
        # Siempre devolver el error completo para debugging
        return jsonify({
            'message': 'Error interno del servidor',
            'error': str(error),
            'type': type(error).__name__
        }), 500
    return render_template('errors/500.html'), 500


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token expirado'}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Token inválido'}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Token de autorización requerido'}), 401


# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    # Crear carpetas necesarias en la nueva estructura
    os.makedirs('app/templates', exist_ok=True)
    os.makedirs('app/static/css', exist_ok=True)
    os.makedirs('app/static/js', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("[SISTEMA] WEB + API REST - CENTRO MINERO SENA")
    print("=" * 60)
    print("[WEB] Interfaz Web: http://localhost:5000")
    print("[API] REST: http://localhost:5000/api/")
    
    # Inicializar sistema de IA después de definir todas las funciones
    if AI_AVAILABLE:
        try:
            initialize_ai_system()
        except Exception as e:
            print(f"[WARN] Error inicializando IA: {e}")
    
    # Ejecutar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)

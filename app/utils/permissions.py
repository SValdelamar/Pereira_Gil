#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Permisos
Sistema de Gestión de Laboratorios - Centro Minero SENA

Este módulo maneja todo lo relacionado con permisos por rol y nivel de acceso.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv

# Cargar configuración
if os.path.exists('.env_produccion'):
    load_dotenv('.env_produccion')

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('HOST', 'localhost'),
    'user': os.getenv('USUARIO_PRODUCCION', 'root'),
    'password': os.getenv('PASSWORD_PRODUCCION', ''),
    'database': os.getenv('BASE_DATOS', 'laboratorio_sistema'),
    'charset': 'utf8mb4'
}

# =====================================================================
# CONSTANTES DE NIVELES
# =====================================================================

NIVEL_APRENDIZ = 1
NIVEL_FUNCIONARIO = 2
NIVEL_INSTRUCTOR_NO_QUIMICA = 3
NIVEL_INSTRUCTOR_QUIMICA = 4
NIVEL_INSTRUCTOR_INVENTARIO = 5
NIVEL_ADMINISTRADOR = 6

ROLES_NOMBRES = {
    1: 'Aprendiz',
    2: 'Funcionario',
    3: 'Instructor (No Química)',
    4: 'Instructor (Química)',
    5: 'Instructor a cargo de Inventario',
    6: 'Administrador'
}

# =====================================================================
# CLASE DE GESTIÓN DE PERMISOS
# =====================================================================

class PermissionsManager:
    """Gestor de permisos del sistema"""
    
    def __init__(self):
        self._permisos_cache = {}
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        return mysql.connector.connect(**DB_CONFIG)
    
    def get_permisos_usuario(self, user_id):
        """
        Obtener todos los permisos de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            dict: Diccionario con permisos por módulo
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Obtener nivel de acceso del usuario
            cursor.execute("""
                SELECT nivel_acceso 
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return {}
            
            nivel = result['nivel_acceso']
            
            # Obtener permisos del nivel
            cursor.execute("""
                SELECT modulo, puede_ver, puede_crear, puede_editar, puede_eliminar
                FROM permisos_modulos
                WHERE nivel_acceso = %s
            """, (nivel,))
            
            permisos = {}
            for row in cursor.fetchall():
                permisos[row['modulo']] = {
                    'ver': row['puede_ver'],
                    'crear': row['puede_crear'],
                    'editar': row['puede_editar'],
                    'eliminar': row['puede_eliminar']
                }
            
            cursor.close()
            conn.close()
            
            return permisos
            
        except Exception as e:
            print(f"Error obteniendo permisos: {e}")
            return {}
    
    def puede_acceder(self, user_id, modulo, accion='ver'):
        """
        Verificar si un usuario puede realizar una acción en un módulo
        
        Args:
            user_id: ID del usuario
            modulo: Nombre del módulo
            accion: Tipo de acción ('ver', 'crear', 'editar', 'eliminar')
            
        Returns:
            bool: True si tiene permiso, False si no
        """
        permisos = self.get_permisos_usuario(user_id)
        
        if modulo not in permisos:
            return False
        
        return permisos[modulo].get(accion, False)
    
    def get_modulos_visibles(self, user_id):
        """
        Obtener lista de módulos visibles para un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            list: Lista de nombres de módulos con permiso de ver
        """
        permisos = self.get_permisos_usuario(user_id)
        return [modulo for modulo, perms in permisos.items() if perms.get('ver', False)]
    
    def get_nivel_usuario(self, user_id):
        """
        Obtener el nivel de acceso de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Nivel de acceso
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT nivel_acceso 
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result['nivel_acceso'] if result else 0
            
        except Exception as e:
            print(f"Error obteniendo nivel: {e}")
            return 0
    
    def es_instructor_con_inventario(self, user_id):
        """
        Verificar si el usuario es instructor a cargo de inventario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            tuple: (bool, int|None) - (es_instructor, laboratorio_id)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT a_cargo_inventario, laboratorio_id 
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result['a_cargo_inventario']:
                return (True, result['laboratorio_id'])
            return (False, None)
            
        except Exception as e:
            print(f"Error verificando instructor: {e}")
            return (False, None)
    
    def puede_gestionar_laboratorio(self, user_id, laboratorio_id):
        """
        Verificar si un usuario puede gestionar un laboratorio específico
        
        Args:
            user_id: ID del usuario
            laboratorio_id: ID del laboratorio
            
        Returns:
            bool: True si puede gestionar, False si no
        """
        nivel = self.get_nivel_usuario(user_id)
        
        # Admin puede gestionar todo
        if nivel == NIVEL_ADMINISTRADOR:
            return True
        
        # Instructor de inventario solo su laboratorio asignado
        if nivel == NIVEL_INSTRUCTOR_INVENTARIO:
            es_instructor, lab_id = self.es_instructor_con_inventario(user_id)
            return es_instructor and lab_id == laboratorio_id
        
        return False

# Instancia global del gestor
permissions_manager = PermissionsManager()

# =====================================================================
# DECORADORES DE PERMISOS
# =====================================================================

def require_permission(modulo, accion='ver'):
    """
    Decorador para verificar permisos en una ruta
    
    Args:
        modulo: Nombre del módulo
        accion: Tipo de acción requerida
        
    Usage:
        @app.route('/usuarios')
        @require_permission('usuarios', 'ver')
        def listar_usuarios():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión', 'error')
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            if not permissions_manager.puede_acceder(user_id, modulo, accion):
                flash('No tienes permisos para acceder a este módulo', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_level(nivel_minimo):
    """
    Decorador para requerir un nivel mínimo de acceso
    
    Args:
        nivel_minimo: Nivel mínimo requerido
        
    Usage:
        @app.route('/admin')
        @require_level(6)
        def admin_panel():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión', 'error')
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            nivel = permissions_manager.get_nivel_usuario(user_id)
            
            if nivel < nivel_minimo:
                flash('No tienes el nivel de acceso requerido', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_instructor_inventario(f):
    """
    Decorador para rutas que solo pueden acceder instructores a cargo de inventario
    
    Usage:
        @app.route('/aprobar-reserva')
        @require_instructor_inventario
        def aprobar_reserva():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'error')
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        es_instructor, lab_id = permissions_manager.es_instructor_con_inventario(user_id)
        
        if not es_instructor:
            flash('Solo instructores a cargo de inventario pueden acceder', 'error')
            return redirect(url_for('dashboard'))
        
        # Pasar el lab_id como contexto
        kwargs['laboratorio_asignado'] = lab_id
        return f(*args, **kwargs)
    return decorated_function

def api_require_permission(modulo, accion='ver'):
    """
    Decorador para APIs REST que verifica permisos
    
    Returns:
        JSON con error si no tiene permiso
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'No autenticado'}), 401
            
            user_id = session['user_id']
            
            if not permissions_manager.puede_acceder(user_id, modulo, accion):
                return jsonify({'success': False, 'message': 'Sin permisos'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =====================================================================
# FUNCIONES AUXILIARES
# =====================================================================

def get_permisos_session():
    """
    Obtener permisos del usuario actual desde la sesión
    Para usar en plantillas Jinja2
    
    Returns:
        dict: Diccionario de permisos
    """
    if 'user_id' not in session:
        return {}
    
    return permissions_manager.get_permisos_usuario(session['user_id'])

def tiene_permiso(modulo, accion='ver'):
    """
    Verificar si el usuario actual tiene un permiso
    Para usar en plantillas Jinja2
    
    Args:
        modulo: Nombre del módulo
        accion: Tipo de acción
        
    Returns:
        bool: True si tiene permiso
    """
    if 'user_id' not in session:
        return False
    
    return permissions_manager.puede_acceder(session['user_id'], modulo, accion)

def get_rol_nombre(nivel):
    """
    Obtener nombre del rol por nivel
    
    Args:
        nivel: Nivel de acceso (1-6)
        
    Returns:
        str: Nombre del rol
    """
    return ROLES_NOMBRES.get(nivel, 'Desconocido')

def validar_campos_requeridos(nivel, datos):
    """
    Validar que se proporcionen los campos requeridos según el nivel
    
    Args:
        nivel: Nivel de acceso del usuario
        datos: Diccionario con datos del formulario
        
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    # Aprendiz (1)
    if nivel == NIVEL_APRENDIZ:
        if not datos.get('programa') or not datos.get('ficha'):
            return (False, 'Aprendices deben especificar programa y ficha')
    
    # Funcionario (2)
    elif nivel == NIVEL_FUNCIONARIO:
        if not datos.get('cargo') or not datos.get('dependencia'):
            return (False, 'Funcionarios deben especificar cargo y dependencia')
    
    # Instructor No Química (3)
    elif nivel == NIVEL_INSTRUCTOR_NO_QUIMICA:
        if not datos.get('programa_formacion') or not datos.get('especialidad'):
            return (False, 'Instructores deben especificar programa y especialidad')
    
    # Instructor Química (4 o 5)
    elif nivel in [NIVEL_INSTRUCTOR_QUIMICA, NIVEL_INSTRUCTOR_INVENTARIO]:
        if not datos.get('especialidad'):
            return (False, 'Instructores de química deben especificar especialidad')
        
        # Si está a cargo de inventario
        if nivel == NIVEL_INSTRUCTOR_INVENTARIO and not datos.get('laboratorio_id'):
            return (False, 'Instructor a cargo debe tener laboratorio asignado')
    
    return (True, '')

# =====================================================================
# EXPORTAR PARA USO EN FLASK
# =====================================================================

__all__ = [
    'permissions_manager',
    'require_permission',
    'require_level',
    'require_instructor_inventario',
    'api_require_permission',
    'get_permisos_session',
    'tiene_permiso',
    'get_rol_nombre',
    'validar_campos_requeridos',
    'NIVEL_APRENDIZ',
    'NIVEL_FUNCIONARIO',
    'NIVEL_INSTRUCTOR_NO_QUIMICA',
    'NIVEL_INSTRUCTOR_QUIMICA',
    'NIVEL_INSTRUCTOR_INVENTARIO',
    'NIVEL_ADMINISTRADOR',
    'ROLES_NOMBRES'
]

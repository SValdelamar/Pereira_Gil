#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Instalación Automática de Base de Datos
Sistema de Gestión de Laboratorios - Centro Minero SENA

Este script crea todas las tablas necesarias y datos iniciales.
Ejecutar una sola vez después de clonar el repositorio.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import sys
from datetime import datetime

# Cargar configuración
if os.path.exists('.env_produccion'):
    load_dotenv('.env_produccion')

DB_CONFIG = {
    'host': os.getenv('HOST', 'localhost'),
    'user': os.getenv('USUARIO_PRODUCCION', 'root'),
    'password': os.getenv('PASSWORD_PRODUCCION', ''),
}

DATABASE_NAME = os.getenv('BASE_DATOS', 'laboratorio_sistema')

def print_header(text):
    """Imprimir encabezado formateado"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_step(text):
    """Imprimir paso del proceso"""
    print(f"\n  ▶ {text}")

def print_success(text):
    """Imprimir mensaje de éxito"""
    print(f"  ✓ {text}")

def print_error(text):
    """Imprimir mensaje de error"""
    print(f"  ✗ {text}")

def verificar_mysql():
    """Verificar que MySQL esté corriendo y las credenciales sean correctas"""
    print_header("PASO 1: VERIFICACIÓN DE MYSQL")
    
    try:
        print_step(f"Conectando a MySQL en {DB_CONFIG['host']}...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print_success(f"MySQL Server versión: {db_info}")
            print_success(f"Usuario: {DB_CONFIG['user']}")
            connection.close()
            return True
    except Error as e:
        print_error(f"Error de conexión: {e}")
        print("\n  💡 SOLUCIÓN:")
        print("     1. Verifica que MySQL esté corriendo")
        print("     2. Verifica las credenciales en .env_produccion")
        print("     3. Asegúrate de tener permisos suficientes")
        return False

def crear_base_datos():
    """Crear la base de datos si no existe"""
    print_header("PASO 2: CREACIÓN DE BASE DE DATOS")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print_step(f"Creando base de datos '{DATABASE_NAME}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print_success(f"Base de datos '{DATABASE_NAME}' lista")
        
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print_error(f"Error al crear base de datos: {e}")
        return False

def crear_tablas():
    """Crear todas las tablas del sistema"""
    print_header("PASO 3: CREACIÓN DE TABLAS")
    
    try:
        config = DB_CONFIG.copy()
        config['database'] = DATABASE_NAME
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # TABLA: usuarios
        print_step("Creando tabla 'usuarios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id VARCHAR(50) PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                tipo ENUM('instructor','aprendiz','administrador','coordinador','tecnico') NOT NULL DEFAULT 'aprendiz',
                programa VARCHAR(100),
                nivel_acceso INT DEFAULT 1,
                activo BOOLEAN DEFAULT TRUE,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                rostro_data LONGBLOB,
                email VARCHAR(100) UNIQUE,
                telefono VARCHAR(20),
                password_hash VARCHAR(255),
                ultimo_acceso DATETIME,
                
                INDEX idx_tipo (tipo),
                INDEX idx_nivel_acceso (nivel_acceso),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'usuarios' creada")
        
        # TABLA: laboratorios
        print_step("Creando tabla 'laboratorios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laboratorios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(20) NOT NULL UNIQUE,
                nombre VARCHAR(100) NOT NULL,
                tipo ENUM('laboratorio','aula','taller','almacen') NOT NULL DEFAULT 'laboratorio',
                ubicacion VARCHAR(200),
                capacidad_estudiantes INT DEFAULT 0,
                responsable VARCHAR(100),
                estado ENUM('activo','mantenimiento','inactivo') NOT NULL DEFAULT 'activo',
                descripcion TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_tipo (tipo),
                INDEX idx_estado (estado),
                INDEX idx_codigo (codigo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'laboratorios' creada")
        
        # TABLA: equipos
        print_step("Creando tabla 'equipos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipos (
                id VARCHAR(50) PRIMARY KEY,
                equipo_id VARCHAR(50) UNIQUE,
                nombre VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                estado ENUM('disponible','en_uso','mantenimiento','fuera_servicio') DEFAULT 'disponible',
                ubicacion VARCHAR(100),
                laboratorio_id INT DEFAULT 1,
                marca VARCHAR(100),
                modelo VARCHAR(100),
                numero_serie VARCHAR(100),
                especificaciones JSON,
                fecha_adquisicion DATE,
                ultima_calibracion DATE,
                proximo_mantenimiento DATE,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_estado (estado),
                INDEX idx_tipo (tipo),
                INDEX idx_laboratorio_id (laboratorio_id),
                FOREIGN KEY (laboratorio_id) REFERENCES laboratorios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'equipos' creada")
        
        # TABLA: inventario
        print_step("Creando tabla 'inventario'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id VARCHAR(50) PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                categoria VARCHAR(50),
                cantidad_actual INT DEFAULT 0,
                cantidad_minima INT DEFAULT 0,
                unidad VARCHAR(20) DEFAULT 'unidad',
                ubicacion VARCHAR(100),
                laboratorio_id INT DEFAULT 1,
                proveedor VARCHAR(100),
                costo_unitario DECIMAL(10,2),
                fecha_vencimiento DATE,
                lote VARCHAR(50),
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_categoria (categoria),
                INDEX idx_laboratorio_id (laboratorio_id),
                INDEX idx_cantidad (cantidad_actual),
                FOREIGN KEY (laboratorio_id) REFERENCES laboratorios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'inventario' creada")
        
        # TABLA: reservas
        print_step("Creando tabla 'reservas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id VARCHAR(50) PRIMARY KEY,
                usuario_id VARCHAR(50) NOT NULL,
                equipo_id VARCHAR(50) NOT NULL,
                fecha_inicio DATETIME NOT NULL,
                fecha_fin DATETIME NOT NULL,
                estado ENUM('programada','activa','completada','cancelada') DEFAULT 'programada',
                notas TEXT,
                observaciones TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_estado (estado),
                INDEX idx_fecha_inicio (fecha_inicio),
                INDEX idx_usuario_id (usuario_id),
                INDEX idx_equipo_id (equipo_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'reservas' creada")
        
        # TABLA: historial_uso
        print_step("Creando tabla 'historial_uso'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_uso (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id VARCHAR(50),
                equipo_id VARCHAR(50),
                fecha_uso DATETIME DEFAULT CURRENT_TIMESTAMP,
                duracion_minutos INT,
                proposito TEXT,
                observaciones TEXT,
                
                INDEX idx_fecha_uso (fecha_uso),
                INDEX idx_usuario_id (usuario_id),
                INDEX idx_equipo_id (equipo_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'historial_uso' creada")
        
        # TABLA: movimientos_inventario
        print_step("Creando tabla 'movimientos_inventario'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                inventario_id VARCHAR(50) NOT NULL,
                tipo_movimiento ENUM('entrada','salida','ajuste','transferencia') NOT NULL,
                cantidad INT NOT NULL,
                fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario_id VARCHAR(50),
                observaciones TEXT,
                destino VARCHAR(100),
                documento_referencia VARCHAR(100),
                
                INDEX idx_inventario_id (inventario_id),
                INDEX idx_tipo_movimiento (tipo_movimiento),
                INDEX idx_fecha (fecha_movimiento),
                INDEX idx_usuario_id (usuario_id),
                FOREIGN KEY (inventario_id) REFERENCES inventario(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'movimientos_inventario' creada")
        
        # TABLA: mantenimientos
        print_step("Creando tabla 'mantenimientos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mantenimientos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                equipo_id VARCHAR(50) NOT NULL,
                tipo_mantenimiento ENUM('preventivo','correctivo','calibracion','limpieza') NOT NULL,
                fecha_mantenimiento DATE NOT NULL,
                tecnico_responsable VARCHAR(100),
                descripcion TEXT,
                costo DECIMAL(10,2),
                estado ENUM('programado','en_proceso','completado','cancelado') DEFAULT 'programado',
                observaciones TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_equipo_id (equipo_id),
                INDEX idx_fecha (fecha_mantenimiento),
                INDEX idx_tipo (tipo_mantenimiento),
                INDEX idx_estado (estado),
                FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'mantenimientos' creada")
        
        # TABLA: comandos_voz
        print_step("Creando tabla 'comandos_voz'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comandos_voz (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id VARCHAR(50),
                comando TEXT,
                respuesta TEXT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                exito BOOLEAN DEFAULT TRUE,
                
                INDEX idx_fecha (fecha),
                INDEX idx_usuario_id (usuario_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'comandos_voz' creada")
        
        # TABLA: logs_seguridad
        print_step("Creando tabla 'logs_seguridad'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_seguridad (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario_id VARCHAR(50),
                accion VARCHAR(100),
                detalle TEXT,
                ip_origen VARCHAR(45),
                exitoso BOOLEAN,
                
                INDEX idx_timestamp (timestamp),
                INDEX idx_usuario (usuario_id),
                INDEX idx_accion (accion)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'logs_seguridad' creada")
        
        # TABLA: configuracion_sistema
        print_step("Creando tabla 'configuracion_sistema'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clave VARCHAR(100) UNIQUE NOT NULL,
                valor TEXT,
                descripcion TEXT,
                tipo VARCHAR(20) DEFAULT 'texto',
                fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_clave (clave)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'configuracion_sistema' creada")
        
        # TABLA: objetos (para reconocimiento visual)
        print_step("Creando tabla 'objetos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objetos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                slug VARCHAR(150),
                categoria VARCHAR(100),
                descripcion TEXT,
                reconocer TINYINT(1) NOT NULL DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE KEY unique_objeto (nombre, categoria),
                INDEX idx_slug (slug),
                INDEX idx_categoria (categoria)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'objetos' creada")
        
        # TABLA: objetos_imagenes
        print_step("Creando tabla 'objetos_imagenes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objetos_imagenes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                objeto_id INT NOT NULL,
                path VARCHAR(500),
                imagen LONGBLOB,
                thumb MEDIUMBLOB,
                thumbnail MEDIUMBLOB,
                content_type VARCHAR(50) DEFAULT 'image/jpeg',
                notas TEXT,
                fuente ENUM('upload','camera') DEFAULT 'upload',
                vista VARCHAR(50) DEFAULT NULL COMMENT 'frontal, posterior, superior, inferior, lateral_derecha, lateral_izquierda',
                fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_objeto (objeto_id),
                INDEX idx_vista (vista),
                FOREIGN KEY (objeto_id) REFERENCES objetos(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print_success("Tabla 'objetos_imagenes' creada")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print_success("Todas las tablas creadas exitosamente")
        return True
        
    except Error as e:
        print_error(f"Error al crear tablas: {e}")
        return False

def insertar_datos_iniciales():
    """Insertar datos iniciales necesarios para el sistema"""
    print_header("PASO 4: DATOS INICIALES")
    
    try:
        config = DB_CONFIG.copy()
        config['database'] = DATABASE_NAME
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Insertar laboratorios iniciales
        print_step("Insertando laboratorios iniciales...")
        laboratorios = [
            ('LAB-QUI-001', 'Laboratorio de Química General', 'laboratorio', 'Edificio A - Piso 2', 25, 'Instructor de Química'),
            ('LAB-QUI-002', 'Laboratorio de Química Analítica', 'laboratorio', 'Edificio A - Piso 2', 20, 'Instructor de Química'),
            ('LAB-MIN-001', 'Laboratorio de Mineralogía', 'laboratorio', 'Edificio B - Piso 1', 30, 'Instructor de Mineralogía'),
            ('LAB-MET-001', 'Laboratorio de Metalurgia', 'laboratorio', 'Edificio C - Piso 1', 15, 'Instructor de Metalurgia'),
            ('AULA-001', 'Aula de Química Teórica', 'aula', 'Edificio A - Piso 1', 40, 'Coordinador Académico'),
            ('TALL-001', 'Taller de Preparación de Muestras', 'taller', 'Edificio B - Sótano', 12, 'Técnico de Laboratorio'),
            ('ALM-001', 'Almacén de Reactivos', 'almacen', 'Edificio A - Sótano', 0, 'Almacenista')
        ]
        
        cursor.executemany("""
            INSERT INTO laboratorios (codigo, nombre, tipo, ubicacion, capacidad_estudiantes, responsable)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)
        """, laboratorios)
        print_success(f"{len(laboratorios)} laboratorios insertados")
        
        # Insertar usuario administrador por defecto
        print_step("Creando usuario administrador...")
        cursor.execute("""
            INSERT INTO usuarios (id, nombre, tipo, nivel_acceso, activo, email, password_hash)
            VALUES ('admin', 'Administrador', 'administrador', 4, TRUE, 'admin@sena.edu.co', 'admin123')
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)
        """)
        print_success("Usuario administrador creado (ID: admin, Password: admin123)")
        
        # Insertar configuración inicial
        print_step("Insertando configuración del sistema...")
        configuraciones = [
            ('nombre_institucion', 'Centro Minero SENA', 'Nombre de la institución'),
            ('version_sistema', '2.0', 'Versión del sistema'),
            ('backup_automatico', 'false', 'Activar backups automáticos'),
            ('dias_alerta_mantenimiento', '30', 'Días de anticipación para alertas de mantenimiento'),
            ('email_notificaciones', 'laboratorio@sena.edu.co', 'Email para notificaciones del sistema')
        ]
        
        cursor.executemany("""
            INSERT INTO configuracion_sistema (clave, valor, descripcion)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE valor=VALUES(valor)
        """, configuraciones)
        print_success(f"{len(configuraciones)} configuraciones iniciales insertadas")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print_success("Datos iniciales insertados correctamente")
        return True
        
    except Error as e:
        print_error(f"Error al insertar datos iniciales: {e}")
        return False

def verificar_instalacion():
    """Verificar que todo se instaló correctamente"""
    print_header("PASO 5: VERIFICACIÓN FINAL")
    
    try:
        config = DB_CONFIG.copy()
        config['database'] = DATABASE_NAME
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Contar tablas
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        print_success(f"Total de tablas creadas: {len(tablas)}")
        
        # Verificar datos iniciales
        cursor.execute("SELECT COUNT(*) FROM laboratorios")
        labs = cursor.fetchone()[0]
        print_success(f"Laboratorios: {labs}")
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        users = cursor.fetchone()[0]
        print_success(f"Usuarios: {users}")
        
        cursor.execute("SELECT COUNT(*) FROM configuracion_sistema")
        configs = cursor.fetchone()[0]
        print_success(f"Configuraciones: {configs}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print_error(f"Error en verificación: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  INSTALACIÓN AUTOMÁTICA DE BASE DE DATOS")
    print("  Sistema de Gestión de Laboratorios - Centro Minero SENA")
    print("  Versión 2.0")
    print("=" * 80)
    
    # Verificar archivo de configuración
    if not os.path.exists('.env_produccion'):
        print_error("No se encontró el archivo .env_produccion")
        print("\n  💡 SOLUCIÓN:")
        print("     1. Copia .env.example a .env_produccion")
        print("     2. Edita .env_produccion con tus credenciales de MySQL")
        print("     3. Ejecuta este script nuevamente")
        sys.exit(1)
    
    # Ejecutar pasos de instalación
    if not verificar_mysql():
        sys.exit(1)
    
    if not crear_base_datos():
        sys.exit(1)
    
    if not crear_tablas():
        sys.exit(1)
    
    if not insertar_datos_iniciales():
        sys.exit(1)
    
    if not verificar_instalacion():
        sys.exit(1)
    
    # Mensaje final
    print_header("✓✓✓ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("\n  🎉 La base de datos está lista para usar!")
    print("\n  📋 CREDENCIALES DE ACCESO:")
    print("     Usuario: admin")
    print("     Contraseña: admin123")
    print("\n  🚀 PRÓXIMOS PASOS:")
    print("     1. Ejecuta: python web_app.py")
    print("     2. Abre tu navegador en: http://localhost:5000")
    print("     3. Inicia sesión con las credenciales de arriba")
    print("     4. ¡IMPORTANTE! Cambia la contraseña del administrador")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n  ✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

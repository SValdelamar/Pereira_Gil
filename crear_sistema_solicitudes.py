#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear sistema de solicitudes de cambio de nivel
Parte de la corrección de seguridad del registro de usuarios
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Cargar configuración
if os.path.exists('.env_produccion'):
    load_dotenv('.env_produccion')

DB_CONFIG = {
    'host': os.getenv('HOST', 'localhost'),
    'user': os.getenv('USUARIO_PRODUCCION', 'root'),
    'password': os.getenv('PASSWORD_PRODUCCION', ''),
    'database': os.getenv('BASE_DATOS', 'laboratorio_sistema'),
    'charset': 'utf8mb4'
}

def crear_tabla_solicitudes():
    """Crear tabla para solicitudes de cambio de nivel"""
    
    sql = """
    CREATE TABLE IF NOT EXISTS solicitudes_nivel (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id VARCHAR(20) NOT NULL,
        nivel_solicitado INT NOT NULL,
        nivel_actual INT NOT NULL,
        estado ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
        fecha_solicitud DATETIME NOT NULL,
        fecha_respuesta DATETIME NULL,
        admin_revisor VARCHAR(20) NULL,
        comentario_admin TEXT NULL,
        
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
        INDEX idx_estado (estado),
        INDEX idx_usuario (usuario_id),
        INDEX idx_fecha (fecha_solicitud)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Tabla 'solicitudes_nivel' creada exitosamente")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error al crear tabla: {e}")
        return False

def main():
    print("=" * 70)
    print(" CREAR SISTEMA DE SOLICITUDES DE CAMBIO DE NIVEL")
    print("=" * 70)
    print("\nEste script crea la infraestructura para gestionar solicitudes")
    print("de cambio de nivel de usuarios de forma segura.\n")
    
    if crear_tabla_solicitudes():
        print("\n✅ Sistema de solicitudes instalado correctamente")
        print("\nAhora los administradores pueden:")
        print("  • Ver solicitudes pendientes")
        print("  • Aprobar o rechazar cambios de nivel")
        print("  • Mantener control sobre permisos\n")
    else:
        print("\n❌ Error al instalar sistema de solicitudes\n")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Sistema de Migraciones de Base de Datos
Sistema Laboratorio v2.0

Este script maneja migraciones de base de datos de forma segura y versionada.
Similar a Rails ActiveRecord Migrations, Django Migrations, Laravel Migrations.

Uso:
    python migrate.py                    # Ejecutar migraciones pendientes
    python migrate.py --status           # Ver estado de migraciones
    python migrate.py --help             # Ayuda
"""

import os
import sys
import mysql.connector
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env_produccion')  # Priorizar producción
if not os.getenv('DB_HOST'):
    load_dotenv('.env')  # Fallback a desarrollo

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'laboratorio_sistema')
}

class MigrationManager:
    """Gestor de migraciones de base de datos"""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'sql', 'migrations')
        
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            print("💡 Asegúrate de que MySQL esté corriendo y la base de datos exista")
            sys.exit(1)
    
    def ensure_migration_table(self):
        """Asegurar que la tabla de migraciones exista"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    version VARCHAR(20) NOT NULL UNIQUE,
                    nombre VARCHAR(255) NOT NULL,
                    ejecutada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tiempo_ejecucion_ms INT,
                    exito BOOLEAN DEFAULT TRUE
                )
            """)
            conn.commit()
        except mysql.connector.Error as e:
            print(f"❌ Error creando tabla de migraciones: {e}")
            sys.exit(1)
        finally:
            cursor.close()
            conn.close()
    
    def get_executed_migrations(self) -> List[str]:
        """Obtener lista de migraciones ya ejecutadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT version FROM schema_migrations WHERE exito = TRUE ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as e:
            print(f"❌ Error obteniendo migraciones ejecutadas: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_pending_migrations(self) -> List[str]:
        """Obtener lista de migraciones pendientes"""
        if not os.path.exists(self.migrations_dir):
            print(f"❌ Directorio de migraciones no encontrado: {self.migrations_dir}")
            return []
        
        # Obtener todos los archivos de migración
        migration_files = []
        for file in os.listdir(self.migrations_dir):
            if file.endswith('.sql') and file.startswith(('00', '01', '02', '03', '04', '05', '06', '07', '08', '09')):
                migration_files.append(file)
        
        # Ordenar por nombre
        migration_files.sort()
        
        # Filtrar las no ejecutadas
        executed = self.get_executed_migrations()
        pending = []
        
        for file in migration_files:
            version = file.split('_')[0]  # Extraer versión del nombre
            if version not in executed:
                pending.append(file)
        
        return pending
    
    def execute_migration(self, migration_file: str) -> bool:
        """Ejecutar una migración específica"""
        start_time = datetime.now()
        file_path = os.path.join(self.migrations_dir, migration_file)
        
        print(f"🔄 Ejecutando migración: {migration_file}")
        
        # Leer archivo SQL
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            print(f"❌ Error leyendo archivo {migration_file}: {e}")
            return False
        
        # Extraer versión y nombre del archivo
        version = migration_file.split('_')[0]
        nombre = migration_file.replace('.sql', '').replace('_', ' ').replace(version, '').strip()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Ejecutar SQL en transacción
            cursor.execute("START TRANSACTION")
            
            # Dividir y ejecutar sentencias SQL
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
            
            # Registrar migración
            cursor.execute("""
                INSERT INTO schema_migrations (version, nombre, ejecutada_en, tiempo_ejecucion_ms, exito)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (version, nombre, datetime.now(), int((datetime.now() - start_time).total_seconds() * 1000)))
            
            conn.commit()
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"✅ Migración {migration_file} ejecutada en {execution_time}ms")
            return True
            
        except mysql.connector.Error as e:
            conn.rollback()
            print(f"❌ Error ejecutando migración {migration_file}: {e}")
            
            # Registrar error
            try:
                cursor.execute("""
                    INSERT INTO schema_migrations (version, nombre, ejecutada_en, tiempo_ejecucion_ms, exito)
                    VALUES (%s, %s, %s, %s, FALSE)
                """, (version, nombre, datetime.now(), int((datetime.now() - start_time).total_seconds() * 1000)))
                conn.commit()
            except:
                pass  # Si falla el registro, no hacer nada
            
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def run_migrations(self):
        """Ejecutar todas las migraciones pendientes"""
        print("🚀 Sistema de Migraciones - Laboratorio v2.0")
        print("=" * 50)
        
        # Asegurar tabla de migraciones
        self.ensure_migration_table()
        
        # Obtener migraciones pendientes
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ No hay migraciones pendientes. Base de datos está actualizada.")
            return True
        
        print(f"📋 Se encontraron {len(pending)} migraciones pendientes:")
        for migration in pending:
            print(f"   - {migration}")
        
        # Confirmar ejecución
        response = input("\n¿Deseas ejecutar estas migraciones? (s/N): ")
        if response.lower() != 's':
            print("❌ Migraciones canceladas.")
            return False
        
        print("\n🔄 Ejecutando migraciones...\n")
        
        # Ejecutar migraciones
        success_count = 0
        for migration in pending:
            if self.execute_migration(migration):
                success_count += 1
            else:
                print(f"⚠️ Falló la migración {migration}. Deteniendo ejecución.")
                break
        
        print(f"\n{'='*50}")
        if success_count == len(pending):
            print(f"✅✅✅ TODAS LAS MIGRACIONES COMPLETADAS ({success_count}/{len(pending)})")
        else:
            print(f"⚠️ Migraciones completadas: {success_count}/{len(pending)}")
        
        return success_count == len(pending)
    
    def show_status(self):
        """Mostrar estado de las migraciones"""
        print("📊 Estado de las Migraciones")
        print("=" * 40)
        
        self.ensure_migration_table()
        
        # Obtener migraciones ejecutadas
        executed = self.get_executed_migrations()
        pending = self.get_pending_migrations()
        
        print(f"✅ Migraciones ejecutadas: {len(executed)}")
        for version in executed:
            print(f"   ✓ {version}")
        
        print(f"\n⏳ Migraciones pendientes: {len(pending)}")
        for migration in pending:
            print(f"   ○ {migration}")
        
        if not pending:
            print("\n🎉 Base de datos está completamente actualizada!")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Migraciones de Base de Datos')
    parser.add_argument('--status', action='store_true', help='Mostrar estado de migraciones')
    parser.add_argument('--version', action='version', version='Laboratorio Migraciones v1.0.0')
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.status:
        manager.show_status()
    else:
        manager.run_migrations()

if __name__ == '__main__':
    main()

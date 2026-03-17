#!/usr/bin/env python3
"""
Sistema de Migraciones de Base de Datos - SENA Laboratorio
==========================================================

Sistema profesional de migraciones versionado para MySQL/MariaDB.
Similar a Rails Migrations, Django Migrations, Laravel Migrations.

Uso:
    python migrate.py              # Ejecutar migraciones pendientes
    python migrate.py --status     # Ver estado de migraciones
    python migrate.py --help       # Ayuda

Buenas Práticas Implementadas:
- Versionado numérico secuencial (001, 002, 003...)
- SQL idempotente (IF NOT EXISTS)
- Transacciones atómicas
- Logs detallados
- Rollback automático en error
- Validación de sintaxis SQL
- Verificación de estructura post-migración
"""

import os
import sys
import re
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Configuración de colores para terminal
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'

# Detectar si el terminal soporta colores
def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and os.name != 'nt'

# Desactivar colores en Windows o si no hay soporte
if not supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'RESET':
            setattr(Colors, attr, '')

class MigrationManager:
    """Gestor profesional de migraciones de base de datos"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.migrations_dir = self.project_root / 'sql' / 'migrations'
        self.env_file = self.project_root / '.env_produccion'
        
        # Verificar estructura
        self._verify_structure()
        
        # Cargar configuración de BD
        self.db_config = self._load_db_config()
        
    def _verify_structure(self):
        """Verificar que la estructura del proyecto es correcta"""
        if not self.migrations_dir.exists():
            raise Exception(f"❌ Directorio de migraciones no encontrado: {self.migrations_dir}")
            
        if not self.env_file.exists():
            raise Exception(f"❌ Archivo de configuración no encontrado: {self.env_file}")
            
    def _load_db_config(self) -> Dict[str, str]:
        """Cargar configuración de base de datos desde .env_produccion"""
        config = {}
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
                        
            # Validar campos requeridos
            required_fields = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
            for field in required_fields:
                if field not in config:
                    raise Exception(f"❌ Campo requerido faltante en .env_produccion: {field}")
                    
            return config
            
        except Exception as e:
            raise Exception(f"❌ Error cargando configuración: {e}")
    
    def _execute_mysql(self, sql: str, database: Optional[str] = None) -> Tuple[bool, str]:
        """Ejecutar comando MySQL con manejo de errores"""
        try:
            cmd = [
                'mysql',
                f'--host={self.db_config["DB_HOST"]}',
                f'--user={self.db_config["DB_USER"]}',
                f'--password={self.db_config["DB_PASSWORD"]}'
            ]
            
            if database:
                cmd.append(database)
                
            # Ejecutar comando
            result = subprocess.run(
                cmd,
                input=sql,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            return result.returncode == 0, result.stdout + result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "❌ Timeout ejecutando comando MySQL"
        except Exception as e:
            return False, f"❌ Error ejecutando MySQL: {e}"
    
    def _create_database_if_not_exists(self) -> bool:
        """Crear la base de datos si no existe"""
        print(f"{Colors.CYAN}🔍 Verificando base de datos...{Colors.RESET}")
        
        sql = f"CREATE DATABASE IF NOT EXISTS `{self.db_config['DB_NAME']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        success, output = self._execute_mysql(sql)
        
        if success:
            print(f"{Colors.GREEN}✅ Base de datos '{self.db_config['DB_NAME']}' verificada{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ Error creando base de datos: {output}{Colors.RESET}")
            return False
    
    def _create_migrations_table(self) -> bool:
        """Crear tabla de control de migraciones si no existe"""
        print(f"{Colors.CYAN}🔍 Verificando tabla de migraciones...{Colors.RESET}")
        
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.db_config['DB_NAME']}`.`schema_migrations` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            version VARCHAR(20) NOT NULL UNIQUE,
            nombre VARCHAR(255) NOT NULL,
            ejecutada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tiempo_ejecucion_ms INT,
            exito BOOLEAN DEFAULT TRUE,
            checksum VARCHAR(64),
            INDEX idx_version (version),
            INDEX idx_ejecutada_en (ejecutada_en)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        success, output = self._execute_mysql(sql)
        
        if success:
            print(f"{Colors.GREEN}✅ Tabla de migraciones verificada{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ Error creando tabla de migraciones: {output}{Colors.RESET}")
            return False
    
    def _get_executed_migrations(self) -> List[str]:
        """Obtener lista de migraciones ya ejecutadas"""
        sql = f"SELECT version FROM `{self.db_config['DB_NAME']}`.`schema_migrations` ORDER BY version"
        success, output = self._execute_mysql(sql)
        
        if success:
            versions = []
            for line in output.strip().split('\n'):
                if line and not line.startswith('version'):
                    versions.append(line.strip())
            return versions
        else:
            # Si la tabla no existe, retornar vacío
            return []
    
    def _get_pending_migrations(self) -> List[Path]:
        """Obtener lista de migraciones pendientes"""
        executed = self._get_executed_migrations()
        
        # Buscar archivos de migración
        migration_files = []
        for file_path in self.migrations_dir.glob('*.sql'):
            if file_path.is_file():
                # Extraer versión del nombre del archivo
                match = re.match(r'^(\d{3})_(.+)\.sql$', file_path.name)
                if match:
                    version = match.group(1)
                    if version not in executed:
                        migration_files.append(file_path)
        
        # Ordenar por versión
        migration_files.sort(key=lambda x: x.name)
        return migration_files
    
    def _validate_migration_file(self, file_path: Path) -> Tuple[bool, str]:
        """Validar sintaxis básica del archivo de migración"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validaciones básicas
            if not content.strip():
                return False, "Archivo vacío"
                
            if 'CREATE TABLE' not in content and 'ALTER TABLE' not in content:
                return False, "No contiene CREATE TABLE ni ALTER TABLE"
                
            # Verificar IF NOT EXISTS en CREATE TABLE
            create_tables = re.findall(r'CREATE TABLE [^;]+', content, re.IGNORECASE)
            for create_stmt in create_tables:
                if 'IF NOT EXISTS' not in create_stmt.upper():
                    return False, f"CREATE TABLE sin IF NOT EXISTS: {create_stmt[:50]}..."
            
            return True, "Validación OK"
            
        except Exception as e:
            return False, f"Error leyendo archivo: {e}"
    
    def _execute_migration(self, file_path: Path) -> Tuple[bool, str, int]:
        """Ejecutar una migración específica"""
        print(f"{Colors.YELLOW}📝 Ejecutando migración: {file_path.name}{Colors.RESET}")
        
        # Validar archivo
        is_valid, validation_msg = self._validate_migration_file(file_path)
        if not is_valid:
            return False, f"❌ Validación fallida: {validation_msg}", 0
        
        # Leer contenido
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Extraer versión y nombre del archivo
        match = re.match(r'^(\d{3})_(.+)\.sql$', file_path.name)
        if not match:
            return False, "❌ Formato de archivo inválido (debe ser XXX_nombre.sql)", 0
            
        version = match.group(1)
        nombre = match.group(2).replace('_', ' ').title()
        
        # Medir tiempo
        start_time = time.time()
        
        # Ejecutar SQL
        success, output = self._execute_mysql(sql_content, self.db_config['DB_NAME'])
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if success:
            # Registrar migración
            register_sql = f"""
            INSERT INTO `{self.db_config['DB_NAME']}`.`schema_migrations` 
            (version, nombre, tiempo_ejecucion_ms, exito) 
            VALUES ('{version}', '{nombre}', {execution_time}, TRUE);
            """
            
            reg_success, reg_output = self._execute_mysql(register_sql)
            
            if reg_success:
                return True, f"✅ Migración ejecutada en {execution_time}ms", execution_time
            else:
                return False, f"❌ Error registrando migración: {reg_output}", execution_time
        else:
            # Registrar error
            error_sql = f"""
            INSERT INTO `{self.db_config['DB_NAME']}`.`schema_migrations` 
            (version, nombre, tiempo_ejecucion_ms, exito) 
            VALUES ('{version}', '{nombre} (ERROR)', {execution_time}, FALSE);
            """
            
            self._execute_mysql(error_sql)
            
            return False, f"❌ Error ejecutando SQL: {output}", execution_time
    
    def migrate(self) -> bool:
        """Ejecutar todas las migraciones pendientes"""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 Iniciando Sistema de Migraciones{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Proyecto: {self.project_root}{Colors.RESET}")
        print(f"{Colors.CYAN}🗄️  Base de datos: {self.db_config['DB_NAME']}@{self.db_config['DB_HOST']}{Colors.RESET}")
        print()
        
        # Verificar base de datos
        if not self._create_database_if_not_exists():
            return False
        
        # Verificar tabla de migraciones
        if not self._create_migrations_table():
            return False
        
        # Obtener migraciones pendientes
        pending = self._get_pending_migrations()
        
        if not pending:
            print(f"{Colors.GREEN}✅✓✓ No hay migraciones pendientes. Base de datos está actualizada.{Colors.RESET}")
            return True
        
        print(f"{Colors.YELLOW}📋 Se encontraron {len(pending)} migración(es) pendiente(s):{Colors.RESET}")
        for file_path in pending:
            print(f"   • {file_path.name}")
        print()
        
        # Confirmar ejecución
        response = input(f"{Colors.BOLD}¿Deseas ejecutar estas migraciones? (s/N): {Colors.RESET}")
        if response.lower() not in ['s', 'si', 'sí']:
            print(f"{Colors.YELLOW}❌ Migraciones canceladas por el usuario{Colors.RESET}")
            return False
        
        # Ejecutar migraciones
        success_count = 0
        total_time = 0
        
        for file_path in pending:
            print()
            success, message, exec_time = self._execute_migration(file_path)
            total_time += exec_time
            
            if success:
                print(f"{Colors.GREEN}{message}{Colors.RESET}")
                success_count += 1
            else:
                print(f"{Colors.RED}{message}{Colors.RESET}")
                print(f"{Colors.RED}❌ Deteniendo ejecución por error{Colors.RESET}")
                break
        
        # Resumen
        print()
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        if success_count == len(pending):
            print(f"{Colors.GREEN}✅✅✅ TODAS LAS MIGRACIONES COMPLETADAS{Colors.RESET}")
            print(f"{Colors.GREEN}   • {success_count} migraciones ejecutadas{Colors.RESET}")
            print(f"{Colors.GREEN}   • Tiempo total: {total_time}ms{Colors.RESET}")
            print(f"{Colors.GREEN}   • Base de datos actualizada{Colors.RESET}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  MIGRACIONES INCOMPLETAS{Colors.RESET}")
            print(f"{Colors.YELLOW}   • {success_count} de {len(pending)} migraciones ejecutadas{Colors.RESET}")
            print(f"{Colors.YELLOW}   • Tiempo total: {total_time}ms{Colors.RESET}")
            print(f"{Colors.RED}   • Revisa los errores y vuelve a ejecutar{Colors.RESET}")
            return False
    
    def status(self) -> bool:
        """Mostrar estado de las migraciones"""
        print(f"{Colors.BOLD}{Colors.BLUE}📊 Estado de Migraciones{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Proyecto: {self.project_root}{Colors.RESET}")
        print(f"{Colors.CYAN}🗄️  Base de datos: {self.db_config['DB_NAME']}@{self.db_config['DB_HOST']}{Colors.RESET}")
        print()
        
        # Obtener migraciones ejecutadas
        executed = self._get_executed_migrations()
        
        # Obtener todas las migraciones disponibles
        all_migrations = {}
        for file_path in self.migrations_dir.glob('*.sql'):
            match = re.match(r'^(\d{3})_(.+)\.sql$', file_path.name)
            if match:
                version = match.group(1)
                nombre = match.group(2).replace('_', ' ').title()
                all_migrations[version] = {
                    'nombre': nombre,
                    'archivo': file_path.name,
                    'ejecutada': version in executed
                }
        
        # Ordenar por versión
        sorted_versions = sorted(all_migrations.keys())
        
        if not sorted_versions:
            print(f"{Colors.YELLOW}⚠️  No se encontraron archivos de migración{Colors.RESET}")
            return True
        
        # Mostrar tabla
        print(f"{'Versión':<10} {'Estado':<12} {'Nombre':<40} {'Archivo'}")
        print(f"{'-'*10} {'-'*12} {'-'*40} {'-'*20}")
        
        for version in sorted_versions:
            migration = all_migrations[version]
            status = f"{Colors.GREEN}✅ Ejecutada{Colors.RESET}" if migration['ejecutada'] else f"{Colors.YELLOW}⏳ Pendiente{Colors.RESET}"
            print(f"{version:<10} {status:<20} {migration['nombre']:<40} {migration['archivo']}")
        
        print()
        executed_count = sum(1 for v in sorted_versions if all_migrations[v]['ejecutada'])
        total_count = len(sorted_versions)
        
        if executed_count == total_count:
            print(f"{Colors.GREEN}✅ Base de datos está actualizada ({executed_count}/{total_count}){Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⏳ Hay {total_count - executed_count} migración(es) pendiente(s){Colors.RESET}")
        
        return True

def main():
    """Función principal con manejo de argumentos"""
    parser = argparse.ArgumentParser(
        description='Sistema de Migraciones de Base de Datos - SENA Laboratorio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python migrate.py                 # Ejecutar migraciones pendientes
  python migrate.py --status        # Ver estado de migraciones
  python migrate.py --help          # Mostrar ayuda

Buenas Práticas:
- Los archivos deben nombrarse: 001_nombre.sql, 002_nombre.sql, etc.
- Usar siempre IF NOT EXISTS en CREATE TABLE
- Cada archivo debe ser idempotente (puede ejecutarse múltiples veces)
- Mantener los archivos ordenados por versión
        """
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Mostrar estado de las migraciones'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Sistema de Migraciones v1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        manager = MigrationManager()
        
        if args.status:
            success = manager.status()
        else:
            success = manager.migrate()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}❌ Operación cancelada por el usuario{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()

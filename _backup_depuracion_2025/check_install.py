#!/usr/bin/env python3
"""
Script de Verificacion de Instalacion
Sistema de Laboratorios - Centro Minero SENA

Verifica que todos los componentes esten correctamente instalados
"""

import sys
import os
from pathlib import Path

# Colores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def print_header(title):
    print(f"\n{BOLD}{'='*60}{END}")
    print(f"{BOLD}{BLUE}{title:^60}{END}")
    print(f"{BOLD}{'='*60}{END}\n")

def check_python_version():
    """Verifica version de Python"""
    print(f"{BOLD}Verificando Python...{END}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"  {GREEN}✓{END} Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  {RED}✗{END} Python {version.major}.{version.minor}.{version.micro} (Se requiere 3.11+)")
        return False

def check_dependencies():
    """Verifica dependencias principales"""
    print(f"\n{BOLD}Verificando dependencias...{END}")
    required = [
        'flask',
        'mysql.connector',
        'cv2',
        'numpy',
        'reportlab',
        'openpyxl',
        'flask_restful',
        'flask_jwt_extended',
        'flask_cors'
    ]
    
    all_ok = True
    for dep in required:
        try:
            if dep == 'mysql.connector':
                import mysql.connector
            elif dep == 'cv2':
                import cv2
            elif dep == 'flask_restful':
                import flask_restful
            elif dep == 'flask_jwt_extended':
                import flask_jwt_extended
            elif dep == 'flask_cors':
                import flask_cors
            else:
                __import__(dep)
            print(f"  {GREEN}✓{END} {dep}")
        except ImportError:
            print(f"  {RED}✗{END} {dep} (Falta instalar)")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Verifica archivo .env"""
    print(f"\n{BOLD}Verificando configuracion...{END}")
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if not env_path.exists():
        print(f"  {YELLOW}⚠{END} .env no existe")
        if env_example_path.exists():
            print(f"      Copia .env.example a .env y configuralo")
            print(f"      Windows: copy .env.example .env")
            print(f"      Linux/Mac: cp .env.example .env")
        return False
    else:
        print(f"  {GREEN}✓{END} .env existe")
        # Verificar variables importantes
        with open(env_path, 'r') as f:
            content = f.read()
            vars_to_check = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
            for var in vars_to_check:
                if var in content and 'tu_password' not in content:
                    print(f"  {GREEN}✓{END} {var} configurado")
                elif var in content:
                    print(f"  {YELLOW}⚠{END} {var} necesita configuracion")
                    return False
        return True

def check_project_structure():
    """Verifica estructura del proyecto"""
    print(f"\n{BOLD}Verificando estructura del proyecto...{END}")
    required_paths = [
        'app',
        'app/utils',
        'app/static',
        'app/templates',
        'scripts',
        'docs',
        'web_app.py',
        'run.py',
        'requirements.txt'
    ]
    
    all_ok = True
    for path in required_paths:
        p = Path(path)
        if p.exists():
            print(f"  {GREEN}✓{END} {path}")
        else:
            print(f"  {RED}✗{END} {path} (Falta)")
            all_ok = False
    
    return all_ok

def check_database_connection():
    """Verifica conexion a base de datos"""
    print(f"\n{BOLD}Verificando conexion a MySQL...{END}")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import mysql.connector
        
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        
        if not password or password == 'tu_password_mysql_aqui':
            print(f"  {YELLOW}⚠{END} Configura DB_PASSWORD en .env primero")
            return False
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        print(f"  {GREEN}✓{END} Conexion a MySQL exitosa")
        
        # Verificar si existe la base de datos
        cursor = conn.cursor()
        db_name = os.getenv('DB_NAME', 'laboratorios_db')
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if result:
            print(f"  {GREEN}✓{END} Base de datos '{db_name}' existe")
        else:
            print(f"  {YELLOW}⚠{END} Base de datos '{db_name}' no existe")
            print(f"      Ejecuta: python scripts/setup_database.py")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  {RED}✗{END} Error de conexion: {str(e)}")
        return False

def main():
    """Funcion principal"""
    print_header("VERIFICACION DE INSTALACION")
    
    results = []
    
    # Verificaciones
    results.append(("Python", check_python_version()))
    results.append(("Dependencias", check_dependencies()))
    results.append(("Estructura", check_project_structure()))
    results.append(("Configuracion", check_env_file()))
    results.append(("Base de Datos", check_database_connection()))
    
    # Resumen
    print_header("RESUMEN")
    
    all_ok = all(r[1] for r in results)
    
    for name, status in results:
        if status:
            print(f"  {GREEN}✓{END} {name}: OK")
        else:
            print(f"  {RED}✗{END} {name}: REQUIERE ATENCION")
    
    print()
    
    if all_ok:
        print(f"{BOLD}{GREEN}{'='*60}{END}")
        print(f"{BOLD}{GREEN}✓ INSTALACION COMPLETA Y CORRECTA{END}")
        print(f"{BOLD}{GREEN}{'='*60}{END}\n")
        print(f"  {BOLD}Puedes ejecutar el servidor:{END}")
        print(f"    python web_app.py")
        print(f"  {BOLD}O:{END}")
        print(f"    python run.py")
        print()
        return 0
    else:
        print(f"{BOLD}{RED}{'='*60}{END}")
        print(f"{BOLD}{RED}⚠ INSTALACION INCOMPLETA{END}")
        print(f"{BOLD}{RED}{'='*60}{END}\n")
        print(f"  Revisa los errores arriba y corrigelos.")
        print(f"  Consulta: INSTALACION_RAPIDA.md")
        print()
        return 1

if __name__ == "__main__":
    exit(main())

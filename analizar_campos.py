#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Análisis de Campos de Base de Datos
Verifica que todos los campos usados en web_app.py existan en setup_database.py
"""

import re
import os

def extraer_campos_de_query(query):
    """Extrae nombres de campos de queries INSERT o UPDATE"""
    campos = []
    
    # Para INSERT INTO tabla (campo1, campo2, ...)
    insert_match = re.search(r'INSERT INTO\s+(\w+)\s*\((.*?)\)', query, re.IGNORECASE | re.DOTALL)
    if insert_match:
        tabla = insert_match.group(1)
        campos_str = insert_match.group(2)
        campos_lista = [c.strip() for c in campos_str.split(',')]
        return tabla, campos_lista
    
    # Para UPDATE tabla SET campo1 = ..., campo2 = ...
    update_match = re.search(r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:WHERE|$)', query, re.IGNORECASE | re.DOTALL)
    if update_match:
        tabla = update_match.group(1)
        sets = update_match.group(2)
        campos_lista = [s.split('=')[0].strip() for s in sets.split(',')]
        return tabla, campos_lista
    
    return None, []

def analizar_web_app():
    """Analiza web_app.py para extraer todos los campos usados"""
    print("=" * 80)
    print("ANALIZANDO WEB_APP.PY")
    print("=" * 80)
    
    with open('web_app.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Encontrar todas las queries
    queries = re.findall(r'(?:INSERT INTO|UPDATE).*?(?="""|\'\'\').*?(?:"""|\'\'\')' , contenido, re.IGNORECASE | re.DOTALL)
    
    campos_por_tabla = {}
    
    # Buscar patrones específicos
    patterns = [
        (r'INSERT INTO\s+(\w+)\s*\((.*?)\)', 'INSERT'),
        (r'UPDATE\s+(\w+)\s+SET\s+(.*?)WHERE', 'UPDATE'),
    ]
    
    for pattern, tipo in patterns:
        matches = re.finditer(pattern, contenido, re.IGNORECASE | re.DOTALL)
        for match in matches:
            tabla = match.group(1)
            campos_str = match.group(2)
            
            if tipo == 'INSERT':
                campos = [c.strip() for c in campos_str.split(',') if c.strip()]
            else:  # UPDATE
                campos = [s.split('=')[0].strip() for s in campos_str.split(',') if '=' in s]
            
            if tabla not in campos_por_tabla:
                campos_por_tabla[tabla] = set()
            
            campos_por_tabla[tabla].update([c for c in campos if c and not c.startswith('%')])
    
    return campos_por_tabla

def analizar_setup_database():
    """Analiza setup_database.py para ver qué campos están definidos"""
    print("\n" + "=" * 80)
    print("ANALIZANDO SETUP_DATABASE.PY")
    print("=" * 80)
    
    with open('scripts/setup_database.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Extraer definiciones de CREATE TABLE
    create_tables = re.findall(r'CREATE TABLE.*?(?=\).*?ENGINE)', contenido, re.IGNORECASE | re.DOTALL)
    
    campos_definidos = {}
    
    for create_stmt in create_tables:
        # Extraer nombre de tabla
        table_match = re.search(r'CREATE TABLE.*?(\w+)\s*\(', create_stmt, re.IGNORECASE)
        if not table_match:
            continue
        
        tabla = table_match.group(1)
        
        # Extraer campos
        campos = []
        lines = create_stmt.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('CREATE') and not line.startswith('INDEX') and not line.startswith('FOREIGN') and not line.startswith('PRIMARY') and not line.startswith('UNIQUE'):
                # Extraer nombre del campo (primera palabra)
                campo_match = re.match(r'(\w+)', line)
                if campo_match:
                    campo = campo_match.group(1)
                    if campo.upper() not in ['IF', 'NOT', 'EXISTS']:
                        campos.append(campo)
        
        campos_definidos[tabla] = set(campos)
    
    return campos_definidos

def comparar_y_reportar(campos_usados, campos_definidos):
    """Compara y genera reporte de diferencias"""
    print("\n" + "=" * 80)
    print("REPORTE DE DIFERENCIAS")
    print("=" * 80)
    
    problemas_encontrados = False
    
    for tabla, campos in campos_usados.items():
        print(f"\n📋 Tabla: {tabla}")
        print("-" * 80)
        
        if tabla not in campos_definidos:
            print(f"❌ ERROR: La tabla '{tabla}' NO está definida en setup_database.py")
            print(f"   Campos usados: {', '.join(sorted(campos))}")
            problemas_encontrados = True
            continue
        
        campos_faltantes = campos - campos_definidos[tabla]
        
        if campos_faltantes:
            print(f"❌ Campos FALTANTES en setup_database.py:")
            for campo in sorted(campos_faltantes):
                print(f"   - {campo}")
            problemas_encontrados = True
        else:
            print(f"✓ Todos los campos están definidos ({len(campos)} campos)")
    
    print("\n" + "=" * 80)
    if problemas_encontrados:
        print("❌ SE ENCONTRARON PROBLEMAS - Revisar arriba")
    else:
        print("✅ TODO CORRECTO - Todos los campos están definidos")
    print("=" * 80 + "\n")
    
    return not problemas_encontrados

def main():
    print("\n" + "=" * 80)
    print("VERIFICADOR DE CAMPOS DE BASE DE DATOS")
    print("Sistema de Gestión de Laboratorios - Centro Minero SENA")
    print("=" * 80 + "\n")
    
    # Verificar que existan los archivos
    if not os.path.exists('web_app.py'):
        print("❌ ERROR: No se encontró web_app.py")
        return
    
    if not os.path.exists('scripts/setup_database.py'):
        print("❌ ERROR: No se encontró scripts/setup_database.py")
        return
    
    # Analizar archivos
    campos_usados = analizar_web_app()
    campos_definidos = analizar_setup_database()
    
    # Comparar y reportar
    todo_correcto = comparar_y_reportar(campos_usados, campos_definidos)
    
    if not todo_correcto:
        print("\n💡 RECOMENDACIÓN:")
        print("   Actualiza scripts/setup_database.py con los campos faltantes")
        print("   para que las instalaciones nuevas no tengan errores.\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para verificar la estructura real de movimientos_inventario y conservar información
"""

import sys
import os
sys.path.append('.')

def verificar_y_mejorar_estructura():
    """Verificar estructura real y proponer solución mejorada"""
    try:
        print("🔍 Verificando Estructura y Conservación de Información")
        print("=" * 60)
        
        from web_app import db_manager
        
        # 1. Intentar obtener estructura real
        print("\n📋 Intentando obtener estructura de movimientos_inventario:")
        try:
            # Método 1: DESCRIBE
            query_describe = "DESCRIBE movimientos_inventario"
            estructura = db_manager.execute_query(query_describe)
            
            if estructura:
                print(f"✅ Estructura obtenida: {len(estructura)} columnas")
                print("\n📋 Columnas reales encontradas:")
                for i, col in enumerate(estructura, 1):
                    print(f"   {i:2d}. {col['Field']} ({col['Type']})")
                
                # Analizar columnas importantes
                columnas_importantes = {
                    'id': 'ID del movimiento',
                    'item_id': 'ID del item (o inventario_id)',
                    'inventario_id': 'ID del item (alternativa)',
                    'tipo_movimiento': 'Tipo de movimiento',
                    'cantidad': 'Cantidad movida',
                    'motivo': 'Motivo del movimiento',
                    'observaciones': 'Observaciones',
                    'usuario_id': 'ID del usuario',
                    'laboratorio_id': 'ID del laboratorio',
                    'fecha_movimiento': 'Fecha del movimiento',
                    'referencia': 'Referencia adicional'
                }
                
                print(f"\n🎯 Análisis de columnas importantes:")
                for col, desc in columnas_importantes.items():
                    existe = any(c['Field'] == col for c in estructura)
                    print(f"   {'✅' if existe else '❌'} {col}: {desc}")
                
                return estructura
                
            else:
                print("❌ No se pudo obtener estructura con DESCRIBE")
                
        except Exception as e:
            print(f"❌ Error con DESCRIBE: {e}")
        
        # 2. Método alternativo: Mostrar primeros registros
        print("\n🔍 Intentando mostrar primeros registros:")
        try:
            query_muestra = "SELECT * FROM movimientos_inventario LIMIT 3"
            muestra = db_manager.execute_query(query_muestra)
            
            if muestra:
                print(f"✅ Muestra obtenida: {len(muestra)} registros")
                if muestra:
                    primer_registro = muestra[0]
                    print(f"\n📋 Columnas en primer registro:")
                    for i, (campo, valor) in enumerate(primer_registro.items(), 1):
                        print(f"   {i:2d}. {campo}: {valor}")
                    return list(primer_registro.keys())
            else:
                print("⚠️ No hay registros en la tabla")
                return []
                
        except Exception as e:
            print(f"❌ Error con muestra: {e}")
            return []
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return []

def proponer_solucion_conservadora(columnas_disponibles):
    """Proponer solución que conserve toda la información"""
    print(f"\n🎯 Propuesta de Solución Conservadora")
    print("=" * 40)
    
    if not columnas_disponibles:
        print("❌ No se pueden determinar las columnas disponibles")
        return
    
    # Columnas que buscamos y sus alternativas
    mapeo_columnas = {
        'item_id': ['inventario_id', 'item_id', 'id_item'],
        'motivo': ['motivo', 'razon', 'descripcion'],
        'observaciones': ['observaciones', 'notas', 'comentarios'],
        'usuario_id': ['usuario_id', 'user_id', 'id_usuario'],
        'laboratorio_id': ['laboratorio_id', 'lab_id', 'id_laboratorio']
    }
    
    print("📋 Mapeo de columnas (preferencia -> alternativa):")
    for objetivo, alternativas in mapeo_columnas.items():
        for alt in alternativas:
            if alt in columnas_disponibles:
                print(f"   ✅ {objetivo} -> {alt}")
                break
        else:
            print(f"   ❌ {objetivo} -> No encontrada")
    
    # Proponer consulta SQL dinámica
    print(f"\n🔧 Consulta SQL dinámica propuesta:")
    
    # Construir SELECT dinámicamente
    columnas_select = []
    for col in columnas_disponibles:
        if col not in ['id']:  # Excluir ID que ya está implícito
            columnas_select.append(col)
    
    if columnas_select:
        consulta_select = ", ".join(columnas_select)
        consulta = f"SELECT {consulta_select} FROM movimientos_inventario WHERE tipo_movimiento = 'salida'"
        print(f"   📋 {consulta}")
    else:
        print("   📋 SELECT * FROM movimientos_inventario WHERE tipo_movimiento = 'salida'")

if __name__ == "__main__":
    columnas = verificar_y_mejorar_estructura()
    if columnas:
        proponer_solucion_conservadora(columnas)

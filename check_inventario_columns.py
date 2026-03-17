#!/usr/bin/env python3
"""
Script para verificar las columnas reales de la tabla inventario
"""

import sys
import os
sys.path.append('.')

def verificar_columnas_inventario():
    """Verificar qué columnas realmente existen en la tabla inventario"""
    try:
        print("🔍 Verificando Columnas Reales de Tabla inventario")
        print("=" * 50)
        
        # Importar el gestor de base de datos
        from web_app import db_manager
        
        # 1. Intentar obtener la estructura de la tabla
        print("\n📋 Obteniendo estructura de tabla inventario:")
        try:
            query_describe = "DESCRIBE inventario"
            estructura = db_manager.execute_query(query_describe)
            
            if estructura:
                print(f"✅ Estructura obtenida: {len(estructura)} columnas")
                print("\n📋 Columnas encontradas:")
                for i, columna in enumerate(estructura, 1):
                    print(f"   {i:2d}. {columna['Field']} ({columna['Type']})")
                
                # Buscar columnas de fecha
                columnas_fecha = [col for col in estructura if 'fecha' in col['Field'].lower()]
                if columnas_fecha:
                    print(f"\n📅 Columnas de fecha encontradas ({len(columnas_fecha)}):")
                    for col in columnas_fecha:
                        print(f"   📅 {col['Field']} ({col['Type']})")
                else:
                    print("\n⚠️ No se encontraron columnas de fecha")
                
                # Verificar si existe fecha_actualizacion
                fecha_actualizacion_existe = any(col['Field'] == 'fecha_actualizacion' for col in estructura)
                fecha_creacion_existe = any(col['Field'] == 'fecha_creacion' for col in estructura)
                
                print(f"\n🔍 Verificación de columnas específicas:")
                print(f"   {'✅' if fecha_actualizacion_existe else '❌'} fecha_actualizacion: {'Existe' if fecha_actualizacion_existe else 'No existe'}")
                print(f"   {'✅' if fecha_creacion_existe else '❌'} fecha_creacion: {'Existe' if fecha_creacion_existe else 'No existe'}")
                
                return estructura
            else:
                print("❌ No se pudo obtener la estructura de la tabla")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo estructura: {e}")
            return None
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        import traceback
        traceback.print_exc()
        return None

def probar_consulta_simple():
    """Probar una consulta simple para ver qué columnas funcionan"""
    try:
        print("\n🧪 Probando consulta simple:")
        from web_app import db_manager
        
        # Intentar consulta básica
        query_simple = "SELECT id, nombre, cantidad_actual FROM inventario LIMIT 3"
        resultado = db_manager.execute_query(query_simple)
        
        if resultado:
            print(f"✅ Consulta simple funciona: {len(resultado)} registros")
            for item in resultado:
                print(f"   📦 {item['nombre']} - Stock: {item['cantidad_actual']}")
        else:
            print("⚠️ Consulta simple no retornó resultados")
            
    except Exception as e:
        print(f"❌ Error en consulta simple: {e}")

if __name__ == "__main__":
    estructura = verificar_columnas_inventario()
    
    if estructura:
        probar_consulta_simple()
        
        print(f"\n🎯 Recomendación:")
        columnas_disponibles = [col['Field'] for col in estructura]
        
        # Buscar columnas de fecha disponibles
        columnas_fecha = [col for col in columnas_disponibles if 'fecha' in col.lower()]
        
        if columnas_fecha:
            print(f"   📅 Usa una de estas columnas de fecha: {', '.join(columnas_fecha)}")
        else:
            print(f"   📅 No hay columnas de fecha disponibles, elimina la actualización de fecha")
            print(f"   📅 O considera agregar la columna: ALTER TABLE inventario ADD COLUMN fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    else:
        print("❌ No se pudo determinar la estructura de la tabla")

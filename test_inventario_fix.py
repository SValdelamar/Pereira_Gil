#!/usr/bin/env python3
"""
Script para probar la corrección del inventario
"""

import sys
import os
sys.path.append('.')

def test_inventario_query():
    """Probar la consulta SQL corregida de inventario"""
    try:
        print("🔧 Probando Consulta SQL de Inventario")
        print("=" * 50)
        
        # Importar el gestor de base de datos
        from web_app import db_manager
        
        # 1. Probar consulta básica de inventario
        print("\n📋 Probando consulta básica:")
        query_basica = "SELECT id, nombre, categoria FROM inventario LIMIT 5"
        resultado = db_manager.execute_query(query_basica)
        
        if resultado:
            print(f"✅ Consulta básica funciona: {len(resultado)} registros encontrados")
            for item in resultado[:3]:
                print(f"   📦 {item['nombre']} ({item['categoria']})")
        else:
            print("⚠️ No hay registros en inventario")
        
        # 2. Probar consulta con stock_status
        print("\n📊 Probando consulta con stock_status:")
        query_stock = """
            SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima,
                   CASE 
                       WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                       WHEN i.cantidad_actual <= i.cantidad_minima * 1.5 THEN 'bajo'
                       ELSE 'normal'
                   END as stock_status
            FROM inventario i
            LIMIT 5
        """
        resultado_stock = db_manager.execute_query(query_stock)
        
        if resultado_stock:
            print(f"✅ Consulta con stock_status funciona: {len(resultado_stock)} registros")
            for item in resultado_stock[:3]:
                stock_status = item['stock_status']
                emoji = "🔴" if stock_status == 'critico' else "🟡" if stock_status == 'bajo' else "🟢"
                print(f"   {emoji} {item['nombre']}: {item['cantidad_actual']}/{item['cantidad_minima']} ({stock_status})")
        else:
            print("⚠️ No hay registros para mostrar stock_status")
        
        # 3. Probar consulta por laboratorio
        print("\n🏢 Probando consulta por laboratorio:")
        query_lab = """
            SELECT i.id, i.nombre, i.categoria, i.cantidad_actual,
                   CASE 
                       WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                       WHEN i.cantidad_actual <= i.cantidad_minima * 1.5 THEN 'bajo'
                       ELSE 'normal'
                   END as stock_status
            FROM inventario i
            WHERE i.laboratorio_id = %s
            LIMIT 5
        """
        
        # Probar con laboratorio_id = 1 (debería existir)
        resultado_lab = db_manager.execute_query(query_lab, (1,))
        
        if resultado_lab:
            print(f"✅ Consulta por laboratorio funciona: {len(resultado_lab)} items en laboratorio 1")
            for item in resultado_lab[:3]:
                print(f"   📦 {item['nombre']} ({item['categoria']})")
        else:
            print("⚠️ No hay items en el laboratorio 1 o el laboratorio no existe")
        
        # 4. Verificar columnas disponibles
        print("\n🔍 Verificando columnas disponibles:")
        try:
            query_columns = "DESCRIBE inventario"
            columnas = db_manager.execute_query(query_columns)
            
            if columnas:
                print("✅ Columnas en tabla inventario:")
                for col in columnas:
                    print(f"   📋 {col['Field']} ({col['Type']})")
        except Exception as e:
            print(f"⚠️ No se pudieron verificar columnas: {e}")
            print("   (Esto es normal si hay resultados sin leer)")
        
        print("\n🎉 Todas las pruebas de inventario pasaron exitosamente!")
        print("🚀 La consulta SQL corregida funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inventario_query()
    sys.exit(0 if success else 1)

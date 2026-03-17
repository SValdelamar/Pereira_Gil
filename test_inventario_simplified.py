#!/usr/bin/env python3
"""
Script para probar la consulta SQL simplificada de inventario
"""

import sys
import os
sys.path.append('.')

def test_inventario_simplified():
    """Probar la consulta SQL simplificada de inventario"""
    try:
        print("🔧 Probando Consulta SQL Simplificada de Inventario")
        print("=" * 50)
        
        # Importar el gestor de base de datos
        from web_app import db_manager
        
        # 1. Probar consulta simplificada
        print("\n📋 Probando consulta simplificada:")
        query_simplificada = """
            SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima, i.unidad,
                   i.ubicacion, i.proveedor, i.costo_unitario, i.laboratorio_id,
                   CASE 
                       WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                       WHEN i.cantidad_actual <= i.cantidad_minima * 1.5 THEN 'bajo'
                       ELSE 'normal'
                   END as stock_status
            FROM inventario i
            LIMIT 5
        """
        resultado = db_manager.execute_query(query_simplificada)
        
        if resultado:
            print(f"✅ Consulta simplificada funciona: {len(resultado)} registros encontrados")
            for item in resultado[:3]:
                stock_status = item['stock_status']
                emoji = "🔴" if stock_status == 'critico' else "🟡" if stock_status == 'bajo' else "🟢"
                print(f"   {emoji} {item['nombre']}: {item['cantidad_actual']}/{item['cantidad_minima']} ({stock_status})")
        else:
            print("⚠️ No hay registros en inventario")
        
        # 2. Probar consulta por laboratorio con la versión simplificada
        print("\n🏢 Probando consulta por laboratorio (simplificada):")
        query_lab = """
            SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima, i.unidad,
                   i.ubicacion, i.proveedor, i.costo_unitario, i.laboratorio_id,
                   CASE 
                       WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                       WHEN i.cantidad_actual <= i.cantidad_minima * 1.5 THEN 'bajo'
                       ELSE 'normal'
                   END as stock_status
            FROM inventario i
            WHERE i.laboratorio_id = %s
            LIMIT 5
        """
        
        # Probar con laboratorio_id = 1
        resultado_lab = db_manager.execute_query(query_lab, (1,))
        
        if resultado_lab:
            print(f"✅ Consulta por laboratorio funciona: {len(resultado_lab)} items en laboratorio 1")
            for item in resultado_lab[:3]:
                print(f"   📦 {item['nombre']} ({item['categoria']})")
        else:
            print("⚠️ No hay items en el laboratorio 1 o el laboratorio no existe")
        
        # 3. Verificar qué laboratorios tienen inventario
        print("\n🏢 Verificando laboratorios con inventario:")
        query_labs = """
            SELECT DISTINCT i.laboratorio_id, l.nombre as lab_nombre, COUNT(*) as total_items
            FROM inventario i
            LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
            GROUP BY i.laboratorio_id, l.nombre
            ORDER BY total_items DESC
            LIMIT 5
        """
        
        try:
            resultado_labs = db_manager.execute_query(query_labs)
            if resultado_labs:
                print("✅ Laboratorios con inventario:")
                for lab in resultado_labs:
                    print(f"   🏢 {lab['lab_nombre'] or 'ID ' + str(lab['laboratorio_id'])}: {lab['total_items']} items")
            else:
                print("⚠️ No hay laboratorios con inventario")
        except Exception as e:
            print(f"⚠️ Error verificando laboratorios: {e}")
        
        print("\n🎉 Prueba de consulta simplificada completada exitosamente!")
        print("🚀 La consulta SQL simplificada funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inventario_simplified()
    sys.exit(0 if success else 1)

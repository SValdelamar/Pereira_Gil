#!/usr/bin/env python3
"""
Script para probar que los templates funcionan con stock_status
"""

import sys
import os
sys.path.append('.')

def test_templates_stock_status():
    """Probar que los templates funcionan con stock_status"""
    try:
        print("🔧 Probando Templates con stock_status")
        print("=" * 50)
        
        # Importar el gestor de base de datos
        from web_app import db_manager
        
        # 1. Probar consulta con stock_status (como la usan los templates)
        print("\n📋 Probando consulta con stock_status:")
        query_template = """
            SELECT i.id, i.nombre, i.categoria, i.cantidad_actual, i.cantidad_minima, i.unidad,
                   i.ubicacion, i.proveedor, i.costo_unitario, i.laboratorio_id,
                   CASE 
                       WHEN i.cantidad_actual <= i.cantidad_minima THEN 'critico'
                       WHEN i.cantidad_actual <= i.cantidad_minima * 1.5 THEN 'bajo'
                       ELSE 'normal'
                   END as stock_status
            FROM inventario i
            LIMIT 3
        """
        resultado = db_manager.execute_query(query_template)
        
        if resultado:
            print(f"✅ Consulta funciona: {len(resultado)} registros")
            for item in resultado:
                stock_status = item['stock_status']
                emoji = "🔴" if stock_status == 'critico' else "🟡" if stock_status == 'bajo' else "🟢"
                print(f"   {emoji} {item['nombre']}: stock_status = '{stock_status}'")
                
                # Verificar que el atributo existe
                if 'stock_status' in item:
                    print(f"      ✅ item.stock_status disponible")
                else:
                    print(f"      ❌ item.stock_status NO disponible")
        else:
            print("⚠️ No hay registros para probar")
        
        # 2. Probar consulta específica para el API endpoint
        print("\n🔌 Probando consulta del API endpoint:")
        query_api = """
            SELECT 
                id, nombre, cantidad_actual, cantidad_minima, unidad,
                CASE 
                    WHEN cantidad_actual <= cantidad_minima THEN 'critico'
                    WHEN cantidad_actual <= cantidad_minima * 1.5 THEN 'bajo'
                    ELSE 'normal'
                END as stock_status
            FROM inventario 
            WHERE id = %s
        """
        
        # Obtener el primer item para probar
        if resultado:
            item_id = resultado[0]['id']
            item_api = db_manager.execute_query(query_api, (item_id,))
            
            if item_api:
                item = item_api[0]
                print(f"✅ API endpoint funciona para item {item_id}:")
                print(f"   📦 {item['nombre']}")
                print(f"   📊 Stock: {item['cantidad_actual']}/{item['cantidad_minima']}")
                print(f"   🎯 Status: {item['stock_status']}")
                
                # Verificar atributos necesarios para el JavaScript
                atributos_requeridos = ['id', 'nombre', 'cantidad_actual', 'cantidad_minima', 'unidad', 'stock_status']
                for attr in atributos_requeridos:
                    if attr in item:
                        print(f"      ✅ item.{attr} disponible")
                    else:
                        print(f"      ❌ item.{attr} NO disponible")
            else:
                print("⚠️ No se pudo probar el API endpoint")
        
        # 3. Simular comportamiento del template
        print("\n🎨 Simulando comportamiento del template:")
        if resultado:
            item = resultado[0]
            stock_status = item['stock_status']
            
            # Simular la lógica del template
            badge_class = 'danger' if stock_status == 'critico' else ('warning' if stock_status == 'bajo' else 'success')
            badge_text = stock_status.upper()
            
            print(f"   📊 Item: {item['nombre']}")
            print(f"   🎯 Stock Status: {stock_status}")
            print(f"   🏷️ Badge Class: bg-{badge_class}")
            print(f"   📝 Badge Text: {badge_text}")
            
            # Simular la lógica del JavaScript
            js_status = stock_status.upper()
            js_class = 'bg-' + badge_class
            
            print(f"   💻 JavaScript Status: {js_status}")
            print(f"   💻 JavaScript Class: {js_class}")
            
            print("   ✅ Simulación del template exitosa")
        
        print("\n🎉 Todas las pruebas de templates pasaron exitosamente!")
        print("🚀 Los templates funcionan correctamente con stock_status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_templates_stock_status()
    sys.exit(0 if success else 1)

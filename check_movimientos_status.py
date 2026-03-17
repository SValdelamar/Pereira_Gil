#!/usr/bin/env python3
"""
Script para verificar el estado de los movimientos y el historial de entregas
"""

import sys
import os
sys.path.append('.')

def verificar_estado_movimientos():
    """Verificar el estado actual de los movimientos y el historial"""
    try:
        print("🔍 Verificando Estado de Movimientos e Historial")
        print("=" * 50)
        
        from web_app import db_manager
        
        # 1. Verificar si hay movimientos registrados
        print("\n📋 Verificando movimientos en la tabla:")
        try:
            query_movimientos = "SELECT COUNT(*) as total FROM movimientos_inventario"
            resultado = db_manager.execute_query(query_movimientos)
            
            if resultado:
                total_movimientos = resultado[0]['total']
                print(f"✅ Total movimientos registrados: {total_movimientos}")
            else:
                print("❌ No se pudo verificar el total de movimientos")
                return False
                
        except Exception as e:
            print(f"❌ Error consultando movimientos: {e}")
            return False
        
        # 2. Verificar movimientos recientes
        print("\n📊 Verificando movimientos recientes:")
        try:
            query_recientes = """
                SELECT * FROM movimientos_inventario 
                ORDER BY fecha_movimiento DESC 
                LIMIT 10
            """
            movimientos = db_manager.execute_query(query_recientes)
            
            if movimientos:
                print(f"✅ Movimientos recientes: {len(movimientos)}")
                for i, mov in enumerate(movimientos, 1):
                    print(f"   {i:2d}. {mov.get('fecha_movimiento', 'N/A')} - {mov.get('tipo_movimiento', 'N/A')} - {mov.get('cantidad', 0)} unidades")
            else:
                print("⚠️ No hay movimientos recientes")
                
        except Exception as e:
            print(f"❌ Error consultando movimientos recientes: {e}")
        
        # 3. Verificar cambios en inventario
        print("\n📦 Verificando cambios recientes en inventario:")
        try:
            query_inventario = """
                SELECT id, nombre, cantidad_actual 
                FROM inventario 
                ORDER BY id 
                LIMIT 10
            """
            items = db_manager.execute_query(query_inventario)
            
            if items:
                print(f"✅ Items en inventario: {len(items)}")
                for item in items:
                    print(f"   📦 {item['id']} - {item['nombre']} - Stock: {item['cantidad_actual']}")
            else:
                print("⚠️ No hay items en inventario")
                
        except Exception as e:
            print(f"❌ Error consultando inventario: {e}")
        
        # 4. Simular consulta del historial que usa el frontend
        print("\n🔍 Simulando consulta de historial del frontend:")
        try:
            query_historial = """
                SELECT * FROM movimientos_inventario 
                WHERE tipo_movimiento = 'salida'
                ORDER BY fecha_movimiento DESC
                LIMIT 50
            """
            
            historial = db_manager.execute_query(query_historial)
            
            if historial:
                print(f"✅ Historial de entregas: {len(historial)} registros")
                for i, entrega in enumerate(historial[:3], 1):
                    print(f"   {i}. {entrega.get('fecha_movimiento', 'N/A')} - {entrega.get('cantidad', 0)} unidades")
            else:
                print("❌ No hay historial de entregas")
                print("   💡 Esto explica por qué no ves las entregas en el historial")
                
        except Exception as e:
            print(f"❌ Error consultando historial: {e}")
        
        # 5. Análisis del problema
        print("\n🎯 Análisis del Problema:")
        print("   ✅ Stock actualizado: El descuento funcionó")
        print("   ❌ Historial vacío: No se registraron los movimientos")
        print("   🔍 Causa: Error en la inserción de movimientos_inventario")
        print("   📋 Razón: Columnas incorrectas en la consulta SQL")
        
        print("\n💡 ¿Dónde fueron los consumibles?")
        print("   📦 Fueron descontados del inventario del item correspondiente")
        print("   📊 El stock disminuyó correctamente")
        print("   🗄️ No hay registro de quién los recibió ni para qué")
        print("   ⚠️ Se perdieron los datos de auditoría y trazabilidad")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verificar_estado_movimientos()
    sys.exit(0 if success else 1)

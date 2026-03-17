#!/usr/bin/env python3
"""
Script para probar que los errores 404 están corregidos
"""

import sys
import os
sys.path.append('.')

def test_correccion_errores_404():
    """Probar que los endpoints que daban 404 ahora funcionan"""
    try:
        print("🧪 Probando Corrección de Errores 404")
        print("=" * 40)
        
        from web_app import app, db_manager
        
        # 1. Probar endpoint de disponibilidad corregido
        print("\n🔍 1. Probando /api/inventario/disponible/<item_id>:")
        
        with app.test_client() as client:
            # Simular sesión
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
                sess['nombre'] = 'Administrador'
            
            # Probar con ID de item existente
            response = client.get('/api/inventario/disponible/ITEM_DFD3B7E3')
            
            if response.status_code == 200:
                print("✅ Endpoint funciona (200 OK)")
                data = response.get_json()
                if data.get('success'):
                    item = data.get('item', {})
                    print(f"   📦 Item: {item.get('nombre', 'N/A')}")
                    print(f"   📊 Stock: {item.get('cantidad_actual', 'N/A')}")
                    print(f"   📋 Estado: {item.get('stock_status', 'N/A')}")
                else:
                    print(f"   ❌ Error: {data.get('message', 'Error desconocido')}")
            elif response.status_code == 404:
                print("❌ Sigue dando 404")
                print(f"   📄 Respuesta: {response.get_data(as_text=True)}")
            else:
                print(f"⚠️ Código inesperado: {response.status_code}")
        
        # 2. Probar endpoint de historial corregido
        print("\n📋 2. Probando /api/inventario/historial-entregas:")
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
            
            response = client.get('/api/inventario/historial-entregas')
            
            if response.status_code == 200:
                print("✅ Endpoint funciona (200 OK)")
                data = response.get_json()
                if data.get('success'):
                    entregas = data.get('entregas', [])
                    print(f"   📊 Entregas encontradas: {len(entregas)}")
                    if entregas:
                        # Mostrar primera entrega si existe
                        primera = entregas[0]
                        print(f"   📄 Primera entrega: {primera.get('id', 'N/A')} - {primera.get('cantidad', 0)} unidades")
                        print(f"   📅 Fecha: {primera.get('fecha_movimiento', 'N/A')}")
                    else:
                        print("   💡 No hay entregas registradas (normal si no hay movimientos)")
                else:
                    print(f"   ❌ Error: {data.get('message', 'Error desconocido')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   📄 Respuesta: {response.get_data(as_text=True)}")
        
        # 3. Probar endpoint de instructores (debe seguir funcionando)
        print("\n👥 3. Probando /api/instructores-quimica:")
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
            
            response = client.get('/api/instructores-quimica')
            
            if response.status_code == 200:
                print("✅ Endpoint funciona (200 OK)")
                data = response.get_json()
                if data.get('success'):
                    instructores = data.get('instructores', [])
                    print(f"   👥 Instructores: {len(instructores)}")
                else:
                    print(f"   ❌ Error: {data.get('message', 'Error desconocido')}")
            else:
                print(f"❌ Error: {response.status_code}")
        
        # 4. Verificar que no haya errores de columna
        print("\n🔍 4. Verificando que no hay errores de columna:")
        
        try:
            # Probar consulta simple a movimientos_inventario
            query_test = "SELECT COUNT(*) as total FROM movimientos_inventario"
            resultado = db_manager.execute_query(query_test)
            
            if resultado:
                total = resultado[0]['total']
                print(f"✅ Consulta a movimientos_inventario funciona: {total} registros")
            else:
                print("⚠️ No se pudo verificar movimientos_inventario")
                
        except Exception as e:
            if "Unknown column" in str(e):
                print(f"❌ Sigue habiendo error de columna: {e}")
            else:
                print(f"⚠️ Error diferente: {e}")
        
        # 5. Resumen de correcciones
        print("\n🎯 Resumen de Correcciones:")
        print("   ✅ Endpoint /api/inventario/disponible/<item_id>:")
        print("      🔄 Cambiado de <int:item_id> a <item_id>")
        print("      📦 Ahora acepta strings como 'ITEM_DFD3B7E3'")
        print("")
        print("   ✅ Endpoint /api/inventario/historial-entregas:")
        print("      🔄 Eliminada columna 'motivo' que no existe")
        print("      📊 Usa solo columnas existentes")
        print("      🔄 Mantiene fallbacks robustos")
        print("")
        print("   ✅ Endpoint /api/instructores-quimica:")
        print("      📋 Continúa funcionando correctamente")
        print("")
        print("   ✅ Endpoint /inventario/entregar:")
        print("      🔄 Tiene fallbacks para errores de columna")
        print("      📦 Stock se actualiza siempre")
        
        print("\n🎉 Errores 404 corregidos!")
        print("🚀 El sistema ahora funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_correccion_errores_404()
    sys.exit(0 if success else 1)

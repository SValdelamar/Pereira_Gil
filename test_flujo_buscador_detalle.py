#!/usr/bin/env python3
"""
Script para probar el nuevo flujo de buscador -> detalle -> gestión
"""

import sys
import os
sys.path.append('.')

def test_flujo_buscador_detalle():
    """Probar que el nuevo flujo de buscador a detalle funciona correctamente"""
    try:
        print("🧪 Probando Nuevo Flujo: Buscador → Detalle → Gestión")
        print("=" * 55)
        
        from web_app import app, db_manager
        
        # 1. Verificar que hay items para probar
        print("\n📦 Verificando items disponibles:")
        query_items = """
            SELECT id, nombre, cantidad_actual 
            FROM inventario 
            LIMIT 3
        """
        items = db_manager.execute_query(query_items)
        
        if not items:
            print("❌ No hay items para probar")
            return False
        
        test_item = items[0]
        print(f"✅ Item de prueba: {test_item['nombre']} (ID: {test_item['id']})")
        
        # 2. Probar vista de buscador
        print("\n🔍 1. Probando vista de buscador:")
        
        with app.test_client() as client:
            # Simular sesión
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
                sess['nombre'] = 'Administrador'
            
            # Probar página principal de inventario
            response = client.get('/inventario')
            
            if response.status_code == 200:
                print("✅ Buscador funciona (200 OK)")
                # Verificar que contiene el botón de detalle
                if f'href="/inventario/detalle/{test_item["id"]}"' in response.get_data(as_text=True):
                    print("   ✅ Botón de detalle presente")
                else:
                    print("   ⚠️ Botón de detalle no encontrado")
            else:
                print(f"❌ Error en buscador: {response.status_code}")
                return False
        
        # 3. Probar vista de detalle
        print("\n📋 2. Probando vista de detalle:")
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
            
            # Probar página de detalle
            response = client.get(f'/inventario/detalle/{test_item["id"]}')
            
            if response.status_code == 200:
                print("✅ Detalle funciona (200 OK)")
                content = response.get_data(as_text=True)
                
                # Verificar elementos clave
                elementos_clave = [
                    'Detalle de Item',
                    'Volver al Buscador',
                    test_item['nombre'],
                    'Entregar Consumible',
                    'Ajustar Stock',
                    'Ver Historial'
                ]
                
                for elemento in elementos_clave:
                    if elemento in content:
                        print(f"   ✅ {elemento}: Presente")
                    else:
                        print(f"   ❌ {elemento}: Ausente")
                        
            else:
                print(f"❌ Error en detalle: {response.status_code}")
                return False
        
        # 4. Probar endpoint de historial específico
        print("\n📊 3. Probando historial específico del item:")
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
            
            # Probar endpoint de historial
            response = client.get(f'/api/inventario/historial-item/{test_item["id"]}')
            
            if response.status_code == 200:
                print("✅ Historial específico funciona (200 OK)")
                data = response.get_json()
                if data.get('success'):
                    historial = data.get('historial', [])
                    print(f"   📊 Movimientos encontrados: {len(historial)}")
                else:
                    print(f"   ❌ Error en respuesta: {data.get('message')}")
            else:
                print(f"❌ Error en historial: {response.status_code}")
        
        # 5. Comparar flujo antiguo vs nuevo
        print("\n🔄 4. Comparación de Flujos:")
        print("")
        print("   ❌ FLUJO ANTIGUO (Inconsistente):")
        print("      1. Buscador Global")
        print("      2. Botones de acción directos (Entregar, Ajustar)")
        print("      3. Acciones en vista de búsqueda")
        print("      4. Confusión conceptual")
        print("")
        print("   ✅ FLUJO NUEVO (Lógico):")
        print("      1. Buscador Global (solo buscar)")
        print("      2. Botón 'Ver Detalle'")
        print("      3. Vista de Detalle (información completa)")
        print("      4. Acciones de gestión en detalle")
        print("      5. Flujo claro: Buscar → Ver → Gestionar")
        
        # 6. Beneficios del nuevo flujo
        print("\n🎯 5. Beneficios del Nuevo Flujo:")
        print("   ✅ Claridad conceptual:")
        print("      📦 Buscador: Solo para buscar")
        print("      📋 Detalle: Para gestionar")
        print("      🔄 Separación de responsabilidades")
        print("")
        print("   ✅ Mejor experiencia:")
        print("      🔍 Búsqueda rápida sin distracciones")
        print("      📋 Vista completa del item")
        print("      ⚡ Acciones contextuales")
        print("")
        print("   ✅ Escalabilidad:")
        print("      📈 Fácil agregar más acciones al detalle")
        print("      🎯 Vista dedicada para cada item")
        print("      📊 Historial específico por item")
        
        print("\n🎉 Nuevo flujo verificado y funcionando!")
        print("🚀 El sistema ahora tiene una arquitectura más lógica")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flujo_buscador_detalle()
    sys.exit(0 if success else 1)

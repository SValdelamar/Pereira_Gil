#!/usr/bin/env python3
"""
Script simplificado para probar el flujo básico
"""

import sys
import os
sys.path.append('.')

def test_flujo_simplificado():
    """Probar el flujo básico sin complicaciones"""
    try:
        print("🧪 Probando Flujo Simplificado")
        print("=" * 35)
        
        from web_app import app, db_manager
        
        # 1. Verificar que hay items
        print("\n📦 Items disponibles:")
        query_items = "SELECT id, nombre FROM inventario LIMIT 2"
        items = db_manager.execute_query(query_items)
        
        if not items:
            print("❌ No hay items")
            return False
        
        test_item = items[0]
        print(f"✅ Item: {test_item['nombre']} ({test_item['id']})")
        
        # 2. Probar buscador
        print("\n🔍 Probando buscador:")
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
            
            response = client.get('/inventario')
            print(f"   Código: {response.status_code}")
            
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                if 'href="/inventario/detalle/' in content:
                    print("   ✅ Botones de detalle presentes")
                else:
                    print("   ❌ Botones de detalle ausentes")
                    # Buscar qué botones hay
                    if 'btn' in content:
                        print("   📋 Botones encontrados:")
                        import re
                        botones = re.findall(r'<button[^>]*>([^<]*)</button>', content)
                        for btn in botones[:3]:
                            print(f"      - {btn.strip()}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                return False
        
        # 3. Probar detalle directamente
        print("\n📋 Probando detalle:")
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
            
            response = client.get(f'/inventario/detalle/{test_item["id"]}')
            print(f"   Código: {response.status_code}")
            
            if response.status_code == 302:
                # Seguir redirección
                location = response.headers.get('Location', '')
                print(f"   🔄 Redirigido a: {location}")
                
                # Hacer seguimiento
                response2 = client.get(location)
                print(f"   Código final: {response2.status_code}")
                
            elif response.status_code == 200:
                print("   ✅ Vista de detalle funciona")
                content = response.get_data(as_text=True)
                if test_item['nombre'] in content:
                    print("   ✅ Nombre del item presente")
                else:
                    print("   ❌ Nombre del item ausente")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📄 Respuesta: {response.get_data(as_text=True)[:200]}")
        
        print("\n🎯 Análisis del Problema:")
        print("   🔍 El buscador funciona pero no muestra botones de detalle")
        print("   📋 La vista de detalle redirige (probablemente por error)")
        print("   💡 Necesario revisar el template y los datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_flujo_simplificado()

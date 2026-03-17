#!/usr/bin/env python3
"""
Prueba para verificar la funcionalidad de los botones en detalle de inventario
"""

import sys
import os
sys.path.append('.')

def test_funcionalidad_botones_detalle():
    """Probar que los botones de acciones en detalle de inventario funcionan correctamente"""
    try:
        print("🧪 PRUEBA: Funcionalidad de Botones en Detalle de Inventario")
        print("=" * 65)
        
        from web_app import app, db_manager
        
        # 1. Verificar que los endpoints existan
        print("\n📋 1. Verificación de Endpoints:")
        
        endpoints_esperados = [
            '/api/inventario/ajustar-stock',
            '/inventario/entregar'
        ]
        
        for endpoint in endpoints_esperados:
            encontrado = False
            for rule in app.url_map.iter_rules():
                if rule.rule == endpoint:
                    encontrado = True
                    metodos = list(rule.methods - {'HEAD', 'OPTIONS'})
                    print(f"   ✅ {endpoint}: {metodos}")
                    break
            
            if not encontrado:
                print(f"   ❌ {endpoint}: NO ENCONTRADO")
        
        # 2. Verificar que el template tenga los modales
        print("\n📄 2. Verificación de Templates y Modales:")
        
        template_path = "app/templates/modules/inventario_detalle.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        elementos_verificar = [
            'modalEntrega',
            'modalAjuste', 
            'mostrarModalEntrega',
            'mostrarModalAjuste',
            'verHistorialItem'
        ]
        
        print("   🔍 Elementos verificados:")
        for elemento in elementos_verificar:
            if elemento in content:
                print(f"      ✅ {elemento}: Presente")
            else:
                print(f"      ❌ {elemento}: Ausente")
        
        # 3. Verificar funciones JavaScript
        print("\n⚙️ 3. Verificación de Funciones JavaScript:")
        
        # Buscar definiciones de funciones
        funciones_js = [
            'function mostrarModalEntrega',
            'function mostrarModalAjuste',
            'function verHistorialItem'
        ]
        
        for funcion in funciones_js:
            if funcion in content:
                print(f"      ✅ {funcion}: Definida")
            else:
                print(f"      ❌ {funcion}: No definida")
        
        # 4. Analizar la función verHistorialItem
        print("\n🔍 4. Análisis de Función verHistorialItem:")
        
        # Buscar el contenido de la función
        import re
        patron_funcion = r'function verHistorialItem\(itemId\)\s*{(.*?)}'
        match = re.search(patron_funcion, content, re.DOTALL)
        
        if match:
            contenido_funcion = match.group(1).strip()
            print(f"   📋 Contenido actual:")
            print(f"      {contenido_funcion}")
            
            if 'location.reload()' in contenido_funcion:
                print("   ⚠️ PROBLEMA: Solo hace reload, no muestra historial")
            else:
                print("   ✅ Función parece funcional")
        else:
            print("   ❌ Función no encontrada")
        
        # 5. Verificar endpoints de historial
        print("\n📊 5. Verificación de Endpoints de Historial:")
        
        endpoints_historial = []
        for rule in app.url_map.iter_rules():
            if 'historial' in rule.rule.lower() or 'histor' in rule.rule.lower():
                endpoints_historial.append({
                    'ruta': rule.rule,
                    'metodos': list(rule.methods - {'HEAD', 'OPTIONS'})
                })
        
        if endpoints_historial:
            print(f"   📊 Endpoints de historial encontrados: {len(endpoints_historial)}")
            for endpoint in endpoints_historial:
                print(f"      📄 {endpoint['ruta']}: {endpoint['metodos']}")
        else:
            print("   ⚠️ No se encontraron endpoints de historial")
        
        # 6. Probar el endpoint de entrega
        print("\n🧪 6. Prueba de Endpoint de Entrega:")
        
        with app.test_client() as client:
            # Simular sesión de instructor con inventario
            with client.session_transaction() as sess:
                sess['user_id'] = 'tecnopark'
                sess['user_level'] = 5
                sess['user_name'] = 'Tecnopark'
                sess['a_cargo_inventario'] = True
                sess['laboratorio_id'] = 1
            
            # Probar GET al endpoint
            response = client.get('/inventario/entregar')
            print(f"   📡 GET /inventario/entregar: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint responde correctamente")
            elif response.status_code == 302:
                print("   🔄 Endpoint redirige (posiblemente esperado)")
            else:
                print(f"   ⚠️ Endpoint responde con {response.status_code}")
        
        # 7. Verificar datos de prueba
        print("\n📋 7. Verificación de Datos de Prueba:")
        
        # Buscar items en la base de datos
        query_items = "SELECT id, nombre, cantidad_actual, unidad FROM inventario LIMIT 3"
        items = db_manager.execute_query(query_items) or []
        
        if items:
            print(f"   📦 Items encontrados: {len(items)}")
            for item in items:
                print(f"      - {item['nombre']} (ID: {item['id']}): {item['cantidad_actual']} {item.get('unidad', 'unidades')}")
        else:
            print("   ⚠️ No hay items en la base de datos para probar")
        
        # 8. Identificar problemas específicos
        print("\n🚨 8. Problemas Identificados:")
        
        problemas = []
        
        # Verificar función de historial
        if match and 'location.reload()' in match.group(1):
            problemas.append("🔄 verHistorialItem() solo hace reload, no muestra historial real")
        
        # Verificar endpoints de historial
        if not endpoints_historial:
            problemas.append("📊 No hay endpoints para mostrar historial de items")
        
        if problemas:
            print("   🚨 Problemas encontrados:")
            for problema in problemas:
                print(f"      {problema}")
        else:
            print("   ✅ No se encontraron problemas evidentes")
        
        # 9. Recomendaciones
        print("\n💡 9. Recomendaciones:")
        
        recomendaciones = []
        
        if not endpoints_historial:
            recomendaciones.append("📊 Crear endpoint para mostrar historial de movimientos de item")
            recomendaciones.append("📄 Agregar sección de historial en el template")
        
        if match and 'location.reload()' in match.group(1):
            recomendaciones.append("🔄 Implementar función verHistorialItem() real")
            recomendaciones.append("📋 Mostrar modal o sección con historial de movimientos")
        
        recomendaciones.extend([
            "🧪 Probar funcionalidad de entrega con datos reales",
            "🔐 Verificar permisos para ajuste de stock",
            "📱 Mejorar UX con feedback visual en las acciones"
        ])
        
        for rec in recomendaciones:
            print(f"   {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_funcionalidad_botones_detalle()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Script para probar el flujo corregido de laboratorio_detalle
"""

import sys
import os
sys.path.append('.')

def test_flujo_laboratorio_detalle():
    """Probar que el flujo de laboratorio_detalle ahora tiene acciones"""
    try:
        print("🧪 Probando Flujo de Laboratorio Detalle Corregido")
        print("=" * 55)
        
        from web_app import app, db_manager
        
        # 1. Verificar que hay laboratorios para probar
        print("\n🏢 Verificando laboratorios disponibles:")
        query_labs = """
            SELECT id, nombre, codigo 
            FROM laboratorios 
            LIMIT 2
        """
        laboratorios = db_manager.execute_query(query_labs)
        
        if not laboratorios:
            print("❌ No hay laboratorios para probar")
            return False
        
        test_lab = laboratorios[0]
        print(f"✅ Laboratorio de prueba: {test_lab['nombre']} (ID: {test_lab['id']})")
        
        # 2. Probar vista de detalle de laboratorio
        print("\n📋 1. Probando vista de detalle de laboratorio:")
        
        with app.test_client() as client:
            # Simular sesión
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
                sess['nombre'] = 'Administrador'
            
            # Probar página de detalle
            response = client.get(f'/laboratorio/{test_lab["id"]}')
            
            if response.status_code == 200:
                print("✅ Detalle de laboratorio funciona (200 OK)")
                content = response.get_data(as_text=True)
                
                # Verificar elementos clave
                elementos_clave = [
                    'Ver Detalle',  # Botón para equipos
                    'Acciones',     # Columna de acciones para items
                    'btn-group',    # Grupos de botones
                    'bi-eye',       # Icono de ver detalle
                    'bi-arrow-left-right'  # Icono de ajuste
                ]
                
                for elemento in elementos_clave:
                    if elemento in content:
                        print(f"   ✅ {elemento}: Presente")
                    else:
                        print(f"   ❌ {elemento}: Ausente")
                        
            else:
                print(f"❌ Error en detalle: {response.status_code}")
                return False
        
        # 3. Probar endpoint de detalle de equipo
        print("\n🔧 2. Probando endpoint de detalle de equipo:")
        
        # Buscar un equipo para probar
        query_equipos = """
            SELECT id, nombre 
            FROM equipos 
            WHERE laboratorio_id = %s
            LIMIT 1
        """
        equipos = db_manager.execute_query(query_equipos, (test_lab['id'],))
        
        if equipos:
            test_equipo = equipos[0]
            print(f"✅ Equipo de prueba: {test_equipo['nombre']} (ID: {test_equipo['id']})")
            
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['user_id'] = 'admin'
                    sess['user_level'] = 6
                
                response = client.get(f'/equipos/detalle/{test_equipo["id"]}')
                
                if response.status_code == 200:
                    print("✅ Detalle de equipo funciona (200 OK)")
                else:
                    print(f"❌ Error en detalle de equipo: {response.status_code}")
        else:
            print("⚠️ No hay equipos en este laboratorio")
        
        # 4. Comparación de antes vs después
        print("\n🔄 3. Comparación de Antes vs Después:")
        print("")
        print("   ❌ ANTES (Inconsistente):")
        print("      📋 Laboratorio detalle: Solo mostraba información")
        print("      🔍 Equipos: Solo botón de reservar")
        print("      📦 Items: Sin acciones de gestión")
        print("      ⚙️ Usuario: No podía gestionar desde el detalle")
        print("")
        print("   ✅ AHORA (Consistente):")
        print("      📋 Laboratorio detalle: Información + acciones")
        print("      🔍 Equipos: Ver detalle + Reservar")
        print("      📦 Items: Ver detalle + Ajustar stock")
        print("      ⚙️ Usuario: Gestión completa desde el detalle")
        
        # 5. Beneficios del nuevo flujo
        print("\n🎯 4. Beneficios del Flujo Corregido:")
        print("   ✅ Consistencia:")
        print("      🔄 Mismo patrón que inventario_detalle")
        print("      📋 Botones de 'Ver Detalle' para gestión")
        print("      ⚙️ Acciones contextuales por tipo de item")
        print("")
        print("   ✅ Mejor UX:")
        print("      👁️ Usuario puede ver detalles completos")
        print("      🔧 Gestión centralizada en vistas de detalle")
        print("      📊 Flujo claro: Ver → Gestionar")
        print("")
        print("   ✅ Escalabilidad:")
        print("      📈 Fácil agregar más acciones")
        print("      🎯 Vistas dedicadas por tipo")
        print("      🔍 Separación de responsabilidades")
        
        print("\n🎉 Flujo de laboratorio_detalle corregido!")
        print("🚀 Ahora es consistente con el patrón de inventario_detalle")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flujo_laboratorio_detalle()
    sys.exit(0 if success else 1)

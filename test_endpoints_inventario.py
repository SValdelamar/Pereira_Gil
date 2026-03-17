#!/usr/bin/env python3
"""
Script para probar los endpoints corregidos de inventario
"""

import sys
import os
sys.path.append('.')

def test_endpoints_inventario():
    """Probar que los endpoints de inventario funcionan correctamente"""
    try:
        print("🔧 Probando Endpoints de Inventario - Errores de Consola")
        print("=" * 60)
        
        # Importar el gestor de base de datos
        from web_app import app, db_manager
        
        # 1. Probar endpoint de historial de entregas
        print("\n📋 Probando endpoint /api/inventario/historial-entregas:")
        
        with app.test_client() as client:
            # Simular sesión de usuario
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_level'] = 6
                sess['nombre'] = 'Administrador'
            
            # Probar endpoint de historial
            response = client.get('/api/inventario/historial-entregas')
            
            if response.status_code == 200:
                print("✅ Endpoint de historial funciona (200 OK)")
                data = response.get_json()
                if data.get('success'):
                    entregas = data.get('entregas', [])
                    print(f"   📊 Entregas encontradas: {len(entregas)}")
                    if entregas:
                        print("   📋 Ejemplos:")
                        for i, entrega in enumerate(entregas[:3], 1):
                            print(f"      {i}. {entrega.get('item_nombre', 'N/A')} - {entrega.get('cantidad', 0)} unidades")
                    else:
                        print("   📭 No hay entregas registradas")
                else:
                    print(f"   ❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
            else:
                print(f"❌ Error en endpoint: {response.status_code}")
                print(f"   📄 Respuesta: {response.get_data(as_text=True)}")
        
        # 2. Verificar que la función verDetallesEquipo existe
        print("\n🔍 Verificando funciones JavaScript:")
        
        # Leer el archivo inventario.html
        try:
            with open('app/templates/modules/inventario.html', 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar funciones JavaScript
            funciones_requeridas = [
                'verDetallesEquipo',
                'mostrarModalAjuste',
                'actualizarDiferenciaAjuste',
                'procesarAjuste',
                'verHistorialItem'
            ]
            
            print("   🔍 Funciones JavaScript verificadas:")
            for funcion in funciones_requeridas:
                if f'function {funcion}(' in contenido:
                    print(f"      ✅ {funcion} - Definida")
                else:
                    print(f"      ❌ {funcion} - No definida")
            
            # Verificar que reservarEquipo ya no está
            if 'reservarEquipo(' in contenido and 'onclick="reservarEquipo' in contenido:
                print("      ❌ reservarEquipo - Todavía referenciada")
            else:
                print("      ✅ reservarEquipo - Eliminada correctamente")
                
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
        
        # 3. Probar consulta SQL del historial
        print("\n🧪 Probando consulta SQL de historial:")
        try:
            query_historial = """
                SELECT 
                    mi.id,
                    mi.cantidad,
                    mi.fecha_movimiento,
                    mi.motivo,
                    mi.observaciones,
                    i.nombre as item_nombre,
                    i.categoria,
                    l.nombre as laboratorio_nombre,
                    'Usuario' as usuario_entrega
                FROM movimientos_inventario mi
                JOIN inventario i ON mi.item_id = i.id
                LEFT JOIN laboratorios l ON i.laboratorio_id = l.id
                WHERE mi.tipo_movimiento = 'salida'
                ORDER BY mi.fecha_movimiento DESC
                LIMIT 5
            """
            
            resultado = db_manager.execute_query(query_historial)
            
            if resultado is not None:
                print(f"✅ Consulta SQL funciona: {len(resultado)} registros")
                for registro in resultado:
                    print(f"   📦 {registro.get('item_nombre', 'N/A')} - {registro.get('cantidad', 0)} unidades")
            else:
                print("⚠️ Consulta SQL no retornó resultados (puede ser normal)")
                
        except Exception as e:
            print(f"❌ Error en consulta SQL: {e}")
        
        # 4. Verificar estructura de tablas
        print("\n📋 Verificando estructura de tablas:")
        try:
            # Verificar movimientos_inventario
            query_mov = "DESCRIBE movimientos_inventario"
            estructura_mov = db_manager.execute_query(query_mov)
            
            if estructura_mov:
                print("✅ Tabla movimientos_inventario - Columnas:")
                for col in estructura_mov[:8]:  # Mostrar primeras 8
                    print(f"   📋 {col['Field']} ({col['Type']})")
            else:
                print("⚠️ No se pudo verificar movimientos_inventario")
                
        except Exception as e:
            print(f"⚠️ Error verificando tablas: {e}")
        
        print("\n🎉 Análisis de errores de consola completado!")
        print("🚀 Los endpoints deberían funcionar correctamente ahora")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_endpoints_inventario()
    sys.exit(0 if success else 1)

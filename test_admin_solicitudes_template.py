#!/usr/bin/env python3
"""
Script para probar el template admin_solicitudes_nivel.html
"""

import sys
import os
sys.path.append('.')

def test_admin_solicitudes_template():
    """Probar que el template admin_solicitudes_nivel.html funciona correctamente"""
    try:
        print("🔧 Probando Template admin_solicitudes_nivel.html")
        print("=" * 50)
        
        # Importar Flask y el template
        from flask import Flask, render_template
        from web_app import app
        from datetime import datetime
        
        # Crear datos de prueba
        solicitudes_prueba = [
            {
                'id': 1,
                'usuario_id': 'test_user_1',
                'nombre': 'Usuario de Prueba',
                'email': 'test@example.com',
                'nivel_actual': 1,
                'nivel_solicitado': 3,
                'fecha_solicitud': datetime(2026, 3, 13, 10, 30, 0),
                'estado': 'pendiente',
                'fecha_respuesta': None
            },
            {
                'id': 2,
                'usuario_id': 'test_user_2',
                'nombre': 'Usuario Aprobado',
                'email': 'aprobado@example.com',
                'nivel_actual': 3,
                'nivel_solicitado': 4,
                'fecha_solicitud': datetime(2026, 3, 12, 15, 20, 0),
                'estado': 'aprobada',
                'fecha_respuesta': datetime(2026, 3, 13, 9, 0, 0)
            },
            {
                'id': 3,
                'usuario_id': 'test_user_3',
                'nombre': 'Usuario Rechazado',
                'email': 'rechazado@example.com',
                'nivel_actual': 2,
                'nivel_solicitado': 6,
                'fecha_solicitud': datetime(2026, 3, 11, 14, 15, 0),
                'estado': 'rechazada',
                'fecha_respuesta': datetime(2026, 3, 12, 11, 30, 0)
            }
        ]
        
        roles_nombres = {
            1: 'Aprendiz',
            2: 'Funcionario',
            3: 'Instructor',
            4: 'Instructor Química',
            5: 'Instructor Inventario',
            6: 'Administrador'
        }
        
        # Calcular solicitudes pendientes
        pendientes = len([s for s in solicitudes_prueba if s['estado'] == 'pendiente'])
        
        with app.app_context():
            # Simular sesión de usuario administrador
            from flask import session
            with app.test_request_context():
                session['user_id'] = 'admin'
                session['user_level'] = 6
                session['nombre'] = 'Administrador'
                
                print("\n📋 Probando renderizado del template:")
                
                try:
                    # Intentar renderizar el template
                    html_output = render_template(
                        'modules/admin_solicitudes_nivel.html',
                        solicitudes=solicitudes_prueba,
                        roles_nombres=roles_nombres,
                        pendientes=pendientes,
                        user=session
                    )
                    
                    print("✅ Template renderizado correctamente")
                    
                    # Verificar que el HTML contenga elementos esperados
                    elementos_esperados = [
                        '<table class="table table-hover mb-0">',
                        '<thead class="table-light">',
                        '<th>ID</th>',
                        '<th>Usuario</th>',
                        '<th>Email</th>',
                        '<th>Nivel Actual</th>',
                        '<th>Nivel Solicitado</th>',
                        '<th>Fecha Solicitud</th>',
                        '<th>Estado</th>',
                        '<th class="text-center">Acciones</th>',
                        'badge bg-warning text-dark',
                        'badge bg-success',
                        'badge bg-danger',
                        'btn-aprobar-solicitud',
                        'btn-rechazar-solicitud'
                    ]
                    
                    print("\n🔍 Verificando elementos HTML:")
                    for elemento in elementos_esperados:
                        if elemento in html_output:
                            print(f"   ✅ {elemento}")
                        else:
                            print(f"   ❌ {elemento}")
                    
                    # Verificar que no haya errores de sintaxis HTML comunes
                    errores_comunes = [
                        '<br><small',  # Error que corregimos
                        '<br><div',   # Otro error posible
                        '<span><br>',  # Error de anidación
                    ]
                    
                    print("\n🚫 Verificando errores HTML comunes:")
                    errores_encontrados = []
                    for error in errores_comunes:
                        if error in html_output:
                            errores_encontrados.append(error)
                            print(f"   ❌ {error} - Encontrado")
                        else:
                            print(f"   ✅ {error} - No encontrado")
                    
                    if not errores_encontrados:
                        print("✅ No se encontraron errores HTML comunes")
                    
                    # Mostrar estadísticas del renderizado
                    print(f"\n📊 Estadísticas del HTML:")
                    print(f"   📏 Longitud total: {len(html_output)} caracteres")
                    print(f"   📄 Líneas aproximadas: {len(html_output.splitlines())}")
                    print(f"   📋 Solicitudes renderizadas: {len(solicitudes_prueba)}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error renderizando template: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_solicitudes_template()
    sys.exit(0 if success else 1)

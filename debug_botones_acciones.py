#!/usr/bin/env python3
"""
Depuración de los botones de acciones en reservas
"""

import sys
import os
sys.path.append('.')

def debug_botones_acciones():
    """Depurar por qué solo se muestra el botón de cancelar"""
    try:
        print("🧪 DEPURACIÓN: Botones de Acciones en Reservas")
        print("=" * 50)
        
        from web_app import app, db_manager
        
        # 1. Verificar estados de reserva existentes
        print("\n📊 1. Estados de Reserva Existentes:")
        
        query_estados = """
            SELECT DISTINCT estado, estado_aprobacion, COUNT(*) as cantidad
            FROM reservas
            GROUP BY estado, estado_aprobacion
            ORDER BY estado, estado_aprobacion
        """
        estados = db_manager.execute_query(query_estados) or []
        
        print("   📋 Estados encontrados:")
        for estado in estados:
            print(f"      - Estado: {estado['estado']}, Aprobación: {estado['estado_aprobacion']} ({estado['cantidad']} reservas)")
        
        # 2. Verificar usuarios y sus permisos
        print("\n👥 2. Usuarios y Permisos:")
        
        query_users = """
            SELECT id, nombre, nivel_acceso, a_cargo_inventario, laboratorio_id
            FROM usuarios 
            WHERE activo = TRUE
            ORDER BY nivel_acceso DESC
        """
        usuarios = db_manager.execute_query(query_users) or []
        
        for usuario in usuarios:
            nivel = usuario['nivel_acceso']
            tiene_inventario = usuario.get('a_cargo_inventario', 0) == 1
            nivel_nombre = {
                1: "Aprendiz",
                2: "Funcionario", 
                3: "Instructor No Química",
                4: "Instructor Química",
                5: "Instructor Inventario",
                6: "Administrador"
            }.get(nivel, f"Nivel {nivel}")
            
            print(f"      - {usuario['nombre']} ({nivel_nombre})")
            print(f"        user_level >= 5: {nivel >= 5}")
            print(f"        a_cargo_inventario: {tiene_inventario}")
            print(f"        Puede aprobar/rechazar: {nivel >= 5 and tiene_inventario}")
        
        # 3. Analizar la lógica actual de botones
        print("\n🔍 3. Análisis de Lógica de Botones:")
        
        print("   📋 CONDICIONES ACTUALES:")
        print("      ✅ APROBAR/RECHAZAR:")
        print("         - user.user_level >= 5")
        print("         - user.a_cargo_inventario = True")
        print("         - r.estado_aprobacion == 'pendiente'")
        print()
        print("      ✅ CANCELAR:")
        print("         - r.estado in ['programada','activa','aprobada']")
        print("         - (user.user_level >= 3 or r.usuario_id == user.user_id)")
        print()
        
        # 4. Simular diferentes escenarios
        print("\n🎭 4. Simulación de Escenarios:")
        
        # Buscar reservas de ejemplo
        query_reservas = """
            SELECT r.id, r.estado, r.estado_aprobacion, r.usuario_id,
                   u.nombre as usuario_nombre, u.nivel_acceso as usuario_nivel,
                   e.nombre as equipo_nombre
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN equipos e ON r.equipo_id = e.id
            ORDER BY r.fecha_creacion DESC
            LIMIT 5
        """
        reservas = db_manager.execute_query(query_reservas) or []
        
        print("   📋 ESCENARIOS DE RESERVA:")
        for reserva in reservas:
            print(f"\n      📝 Reserva {reserva['id']}:")
            print(f"         Estado: {reserva['estado']}")
            print(f"         Aprobación: {reserva['estado_aprobacion']}")
            print(f"         Usuario: {reserva['usuario_nombre']} (Nivel {reserva['usuario_nivel']})")
            
            # Simular como instructor con inventario
            instructor_level = 5
            instructor_inventario = True
            
            # Evaluar condiciones
            puede_aprobar = (instructor_level >= 5 and 
                            instructor_inventario and 
                            reserva['estado_aprobacion'] == 'pendiente')
            
            puede_cancelar = (reserva['estado'] in ['programada','activa','aprobada'] and 
                            (instructor_level >= 3 or reserva['usuario_id'] == 'instructor_test'))
            
            print(f"         👨‍🏫 Como instructor (Nivel 5, con inventario):")
            print(f"            📝 Puede aprobar/rechazar: {puede_aprobar}")
            print(f"            ❌ Puede cancelar: {puede_cancelar}")
            
            # Mostrar qué botones debería ver
            if puede_aprobar:
                print(f"            🔘 Botones: [✅ Aprobar] [❌ Rechazar]")
            elif puede_cancelar:
                print(f"            🔘 Botones: [❌ Cancelar]")
            else:
                print(f"            🔘 Botones: [Ninguno]")
        
        # 5. Identificar el problema
        print("\n🚨 5. Diagnóstico del Problema:")
        
        # Contar reservas pendientes
        query_pendientes = """
            SELECT COUNT(*) as cantidad
            FROM reservas 
            WHERE estado_aprobacion = 'pendiente'
        """
        pendientes = db_manager.execute_query(query_pendientes)[0]['cantidad']
        
        print(f"   📊 Reservas pendientes: {pendientes}")
        
        if pendientes == 0:
            print("   🎯 PROBLEMA IDENTIFICADO:")
            print("      ❌ No hay reservas en estado 'pendiente'")
            print("      🔍 Por eso no se muestran botones de aprobar/rechazar")
            print("      💡 Solo se ven botones de cancelar para otras reservas")
        else:
            print("   ✅ Hay reservas pendientes, el problema puede ser otro")
        
        # 6. Recomendaciones
        print("\n💡 6. Recomendaciones:")
        
        print("   🔧 MEJORAS POSIBLES:")
        print("      1. Verificar que las reservas se creen con estado_aprobacion = 'pendiente'")
        print("      2. Asegurar que el instructor tenga a_cargo_inventario = True")
        print("      3. Agregar botones para diferentes estados")
        print("      4. Mejorar la lógica de visibilidad de botones")
        print()
        
        print("   🎯 ACCIONES INMEDIATAS:")
        print("      1. Revisar el endpoint de creación de reservas")
        print("      2. Verificar el campo a_cargo_inventario del instructor")
        print("      3. Probar con diferentes usuarios y estados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en depuración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_botones_acciones()
    sys.exit(0 if success else 1)

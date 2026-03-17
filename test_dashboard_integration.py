#!/usr/bin/env python3
"""
Script para probar el dashboard con el sistema de módulos
"""

import sys
import os
sys.path.append('.')

def test_dashboard_modulos():
    """Probar la integración del dashboard con el sistema de módulos"""
    try:
        print("🧪 Probando Dashboard con Sistema de Módulos")
        print("=" * 50)
        
        # 1. Importar las funciones del dashboard
        from web_app import dashboard
        from app.utils.modulos_config import get_modulos_disponibles, get_acciones_rapidas_disponibles, get_estadisticas_disponibles
        print("✅ Importaciones correctas")
        
        # 2. Simular sesión de usuario para cada nivel
        print("\n📊 Probando para cada nivel de usuario:")
        print("-" * 40)
        
        for nivel in range(1, 7):
            print(f"\n👤 Probando Nivel {nivel}:")
            
            # Simular sesión
            mock_session = {
                'user_id': f'test_{nivel}',
                'user_level': nivel,
                'nombre': f'Usuario Nivel {nivel}',
                'user_type': 'Test'
            }
            
            # Obtener módulos para este nivel
            modulos = get_modulos_disponibles(nivel)
            acciones = get_acciones_rapidas_disponibles(nivel)
            estadisticas = get_estadisticas_disponibles(nivel)
            
            print(f"   📦 Módulos: {len(modulos)}")
            print(f"   ⚡ Acciones: {len(acciones)}")
            print(f"   📊 Estadísticas: {len(estadisticas)}")
            
            # Verificar módulos principales
            if modulos:
                nombres_modulos = [m.nombre for m in modulos[:3]]
                print(f"   🎯 Principales: {', '.join(nombres_modulos)}")
            
            # Verificar que no haya errores en los datos
            assert modulos is not None, f"Error: modulos es None para nivel {nivel}"
            assert acciones is not None, f"Error: acciones es None para nivel {nivel}"
            assert estadisticas is not None, f"Error: estadisticas es None para nivel {nivel}"
            
            # Verificar estructura de datos
            for modulo in modulos:
                assert hasattr(modulo, 'nombre'), f"Módulo sin nombre: {modulo}"
                assert hasattr(modulo, 'url'), f"Módulo sin url: {modulo}"
                assert hasattr(modulo, 'nivel_minimo'), f"Módulo sin nivel_minimo: {modulo}"
            
            for accion in acciones:
                assert 'nombre' in accion, f"Acción sin nombre: {accion}"
                assert 'url' in accion, f"Acción sin url: {accion}"
                assert 'color' in accion, f"Acción sin color: {accion}"
        
        # 3. Verificar consistencia de niveles
        print("\n🔒 Verificación de Consistencia de Niveles:")
        print("-" * 40)
        
        # Nivel 1 no debería ver usuarios
        modulos_nivel_1 = get_modulos_disponibles(1)
        usuarios_nivel_1 = [m for m in modulos_nivel_1 if m.id == 'usuarios']
        print(f"   Aprendiz puede ver Usuarios: {'❌' if usuarios_nivel_1 else '✅'}")
        
        # Nivel 6 sí debería ver usuarios
        modulos_nivel_6 = get_modulos_disponibles(6)
        usuarios_nivel_6 = [m for m in modulos_nivel_6 if m.id == 'usuarios']
        print(f"   Administrador puede ver Usuarios: {'✅' if usuarios_nivel_6 else '❌'}")
        
        # Nivel 6 debería tener más módulos que nivel 1
        assert len(modulos_nivel_6) > len(modulos_nivel_1), "Administrador debe tener más módulos que Aprendiz"
        print(f"   ✅ Administrador tiene más módulos ({len(modulos_nivel_6)}) que Aprendiz ({len(modulos_nivel_1)})")
        
        # 4. Verificar estadísticas por nivel
        print("\n📈 Verificación de Estadísticas por Nivel:")
        print("-" * 40)
        
        for nivel in range(1, 7):
            estadisticas = get_estadisticas_disponibles(nivel)
            print(f"   Nivel {nivel}: {len(estadisticas)} estadísticas")
            
            # Verificar que siempre tenga estadísticas básicas
            assert 'equipos_activos' in estadisticas, f"Nivel {nivel} debe tener equipos_activos"
            assert 'total_laboratorios' in estadisticas, f"Nivel {nivel} debe tener total_laboratorios"
        
        print("\n🎉 Todas las pruebas del dashboard pasaron exitosamente!")
        print("🚀 Dashboard con sistema de módulos funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_modulos()
    sys.exit(0 if success else 1)

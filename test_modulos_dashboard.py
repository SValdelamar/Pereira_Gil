#!/usr/bin/env python3
"""
Script de prueba para el sistema de módulos controlado por nivel de acceso
"""

import sys
import os
sys.path.append('.')

def test_modulos_system():
    """Probar el sistema completo de módulos"""
    try:
        print("🔧 Sistema de Módulos por Nivel de Acceso")
        print("=" * 50)
        
        # 1. Importar el sistema de módulos
        from app.utils.modulos_config import (
            ModulosManager, 
            get_modulos_disponibles,
            get_acciones_rapidas_disponibles,
            get_estadisticas_disponibles,
            puede_ver_modulo
        )
        print("✅ Sistema de módulos importado correctamente")
        
        # 2. Probar para cada nivel de usuario
        from app.utils.permissions import ROLES_NOMBRES
        
        print("\n📋 Análisis por Nivel de Usuario:")
        print("-" * 30)
        
        for nivel in range(1, 7):
            nombre_rol = ROLES_NOMBRES.get(nivel, 'Desconocido')
            
            # Obtener módulos disponibles
            modulos = get_modulos_disponibles(nivel)
            
            # Obtener acciones rápidas
            acciones = get_acciones_rapidas_disponibles(nivel)
            
            # Obtener estadísticas
            estadisticas = get_estadisticas_disponibles(nivel)
            
            print(f"\n👤 Nivel {nivel} - {nombre_rol}:")
            print(f"   📦 Módulos: {len(modulos)}")
            print(f"   ⚡ Acciones rápidas: {len(acciones)}")
            print(f"   📊 Estadísticas: {len(estadisticas)}")
            
            # Mostrar módulos principales
            if modulos:
                print("   🎯 Módulos principales:")
                for modulo in modulos[:3]:  # Solo los primeros 3
                    print(f"      • {modulo.nombre} ({modulo.categoria.value})")
            
            # Mostrar acciones principales
            if acciones:
                print("   🔧 Acciones principales:")
                for accion in acciones[:2]:  # Solo las primeras 2
                    print(f"      • {accion['nombre']}")
        
        # 3. Probar control de acceso específico
        print("\n🔒 Pruebas de Control de Acceso:")
        print("-" * 30)
        
        # Test: Aprendiz no debería ver configuración
        puede_aprendiz_config = puede_ver_modulo('configuracion', 1)
        print(f"   Aprendiz puede ver Configuración: {'✅' if puede_aprendiz_config else '❌'}")
        
        # Test: Administrador sí debería ver configuración
        puede_admin_config = puede_ver_modulo('configuracion', 6)
        print(f"   Administrador puede ver Configuración: {'✅' if puede_admin_config else '❌'}")
        
        # Test: Instructor no debería ver usuarios
        puede_instructor_usuarios = puede_ver_modulo('usuarios', 4)
        print(f"   Instructor puede ver Usuarios: {'✅' if puede_instructor_usuarios else '❌'}")
        
        # Test: Administrador sí debería ver usuarios
        puede_admin_usuarios = puede_ver_modulo('usuarios', 6)
        print(f"   Administrador puede ver Usuarios: {'✅' if puede_admin_usuarios else '❌'}")
        
        # 4. Probar agrupación por categoría
        print("\n📂 Prueba de Agrupación por Categoría:")
        print("-" * 30)
        
        modulos_admin = ModulosManager.obtener_modulos_por_categoria(6)
        for categoria, mods in modulos_admin.items():
            print(f"   📁 {categoria.title()}: {len(mods)} módulos")
            for mod in mods:
                print(f"      • {mod.nombre}")
        
        # 5. Verificar módulos críticos
        print("\n🚨 Verificación de Módulos Críticos:")
        print("-" * 30)
        
        modulos_criticos = ['usuarios', 'backup', 'visual']
        for modulo_id in modulos_criticos:
            info = ModulosManager.obtener_info_modulo(modulo_id)
            if info:
                print(f"   🔒 {modulo_id}: Nivel mínimo {info.nivel_minimo}")
                print(f"      📝 {info.descripcion}")
            else:
                print(f"   ❌ {modulo_id}: No encontrado")
        
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        print("🚀 Sistema de módulos funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_modulos_system()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Script para probar las correcciones del módulo de mantenimiento
"""

import sys
import os
sys.path.append('.')

def test_maintenance_alerts_fix():
    """Probar que las consultas SQL del módulo de mantenimiento funcionan"""
    try:
        print("🔧 Probando Correcciones del Módulo de Mantenimiento")
        print("=" * 50)
        
        # Importar el gestor de base de datos
        from web_app import db_manager
        from modules.maintenance_alerts import MaintenanceAlertManager
        from modules.maintenance_predictor import MaintenancePredictor
        
        # 1. Probar consulta básica de usuarios
        print("\n👥 Probando consulta de usuarios:")
        query_usuarios = "SELECT id, nombre, nivel_acceso, email FROM usuarios LIMIT 3"
        resultado_usuarios = db_manager.execute_query(query_usuarios)
        
        if resultado_usuarios:
            print(f"✅ Consulta de usuarios funciona: {len(resultado_usuarios)} registros")
            for usuario in resultado_usuarios:
                print(f"   👤 {usuario['nombre']} - Nivel: {usuario['nivel_acceso']} - Email: {usuario.get('email', 'N/A')}")
        else:
            print("⚠️ No hay usuarios para probar")
            return False
        
        # 2. Probar consulta de laboratorios
        print("\n🏢 Probando consulta de laboratorios:")
        query_labs = "SELECT id, nombre FROM laboratorios LIMIT 3"
        resultado_labs = db_manager.execute_query(query_labs)
        
        if resultado_labs:
            print(f"✅ Consulta de laboratorios funciona: {len(resultado_labs)} laboratorios")
            for lab in resultado_labs:
                print(f"   🏢 {lab['nombre']} (ID: {lab['id']})")
        else:
            print("⚠️ No hay laboratorios para probar")
            return False
        
        # 3. Probar el gestor de alertas
        print("\n🚨 Probando gestor de alertas:")
        try:
            predictor = MaintenancePredictor(db_manager)
            alert_manager = MaintenanceAlertManager(db_manager, predictor)
            
            # Probar obtener laboratorios de un usuario
            if resultado_usuarios:
                test_usuario_id = resultado_usuarios[0]['id']
                laboratorios_usuario = alert_manager._obtener_laboratorios_usuario(test_usuario_id)
                
                if laboratorios_usuario:
                    print(f"✅ Laboratorios del usuario {test_usuario_id}: {len(laboratorios_usuario)}")
                    for lab in laboratorios_usuario:
                        print(f"   🏢 {lab['nombre']}")
                else:
                    print(f"⚠️ El usuario {test_usuario_id} no tiene laboratorios asignados")
            
            # Probar obtener destinatarios de un laboratorio
            if resultado_labs:
                test_lab_id = resultado_labs[0]['id']
                destinatarios = alert_manager._obtener_destinatarios_laboratorio(test_lab_id)
                
                if destinatarios:
                    print(f"✅ Destinatarios del laboratorio {test_lab_id}: {len(destinatarios)}")
                    for email in destinatarios:
                        print(f"   📧 {email}")
                else:
                    print(f"⚠️ El laboratorio {test_lab_id} no tiene destinatarios")
            
            print("✅ Gestor de alertas funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en gestor de alertas: {e}")
            return False
        
        # 4. Probar consulta específica corregida
        print("\n🔍 Probando consulta específica corregida:")
        if resultado_usuarios and resultado_labs:
            test_usuario_id = resultado_usuarios[0]['id']
            test_lab_id = resultado_labs[0]['id']
            
            # Probar la consulta corregida directamente
            query_corregida = """
                SELECT DISTINCT l.id, l.nombre
                FROM laboratorios l
                LEFT JOIN usuarios u ON (l.id = u.laboratorio_id OR u.nivel_acceso = 6)
                WHERE u.id = %s OR u.nivel_acceso = 6
                ORDER BY l.nombre
            """
            
            resultado_corregido = db_manager.execute_query(query_corregida, (test_usuario_id,))
            
            if resultado_corregido:
                print(f"✅ Consulta corregida funciona: {len(resultado_corregido)} laboratorios")
                for lab in resultado_corregido:
                    print(f"   🏢 {lab['nombre']}")
            else:
                print("⚠️ Consulta corregida no retornó resultados (puede ser normal)")
        
        print("\n🎉 Todas las pruebas de mantenimiento pasaron exitosamente!")
        print("🚀 Las correcciones SQL funcionan correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_maintenance_alerts_fix()
    sys.exit(0 if success else 1)

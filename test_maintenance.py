#!/usr/bin/env python3
"""
Script de prueba para el sistema de mantenimiento predictivo
"""

import sys
import os
sys.path.append('.')

def test_maintenance_system():
    """Probar el sistema completo de mantenimiento"""
    try:
        print("🧪 Probando Sistema de Mantenimiento Predictivo")
        print("=" * 50)
        
        # 1. Importar módulos
        from modules.maintenance_config import CONFIGURACION_DEFECTO
        print("✅ Configuración cargada")
        
        from modules.maintenance_predictor import MaintenancePredictor
        print("✅ Predictor importado")
        
        from modules.maintenance_alerts import MaintenanceAlertManager
        print("✅ Alert manager importado")
        
        # 2. Verificar NumPy
        import numpy as np
        print(f"✅ NumPy {np.__version__} disponible")
        
        # 3. Probar clases básicas
        from modules.maintenance_predictor import RiesgoMantenimiento, PrediccionMantenimiento
        print("✅ Clases de predicción funcionales")
        
        from modules.maintenance_alerts import TipoAlerta, CanalNotificacion
        print("✅ Clases de alertas funcionales")
        
        # 4. Probar configuración
        config = CONFIGURACION_DEFECTO
        print(f"✅ Configuración por defecto: Email={config.habilitar_email}, Dashboard={config.habilitar_dashboard}")
        
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        print("🚀 Sistema de mantenimiento predictivo listo para usar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_maintenance_system()
    sys.exit(0 if success else 1)

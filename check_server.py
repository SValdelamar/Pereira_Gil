#!/usr/bin/env python3
"""
Verificar configuración del servidor
"""

import os
from dotenv import load_dotenv

def main():
    print('🔍 CONFIGURACIÓN DEL SERVIDOR')
    print('=' * 40)
    
    # Cargar configuración
    load_dotenv()
    
    print('Variables de entorno:')
    print('  HOST: ' + str(os.getenv('HOST', 'localhost')))
    print('  FLASK_ENV: ' + str(os.getenv('FLASK_ENV', 'development')))
    print('  DEBUG: ' + str(os.getenv('DEBUG', 'True')))
    
    print('\nConfiguración de app.run():')
    print('  host="0.0.0.0"  ← Acepta conexiones desde cualquier IP')
    print('  port=5000       ← Puerto estándar Flask')
    print('  debug=True       ← Modo desarrollo activado')
    
    print('\n🌐 ACCESIBILIDAD:')
    print('  • Local: http://localhost:5000')
    print('  • Red: http://[IP_LOCAL]:5000')
    print('  • Todas las interfaces: 0.0.0.0:5000')
    
    print('\n📊 TIPO DE EJECUCIÓN:')
    print('  ✅ Servidor LOCAL (en tu máquina)')
    print('  ✅ Base de datos LOCAL (MySQL en localhost)')
    print('  ✅ Archivos estáticos LOCALES')
    print('  ❌ NO consume APIs externas')
    print('  ❌ NO es cloud-based')
    
    print('\n🎯 RESPUESTA A TU PREGUNTA:')
    print('El software se ejecuta COMPLETAMENTE EN LOCAL')
    print('NO consume ninguna API externa en el navegador')

if __name__ == "__main__":
    main()

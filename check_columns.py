#!/usr/bin/env python3
import sys
sys.path.append('.')

from web_app import db_manager

try:
    # Verificar columnas de la tabla inventario
    result = db_manager.execute_query('DESCRIBE inventario')
    print('Columnas en tabla inventario:')
    for col in result:
        print(f'  📋 {col["Field"]} ({col["Type"]})')
except Exception as e:
    print(f'Error: {e}')

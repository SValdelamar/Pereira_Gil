#!/usr/bin/env python3
"""
Script para verificar las columnas reales de movimientos_inventario
"""

import sys
import os
sys.path.append('.')

def verificar_columnas_movimientos():
    """Verificar qué columnas existen realmente en movimientos_inventario"""
    try:
        print("🔍 Verificando Columnas de movimientos_inventario")
        print("=" * 50)
        
        from web_app import db_manager
        
        # Obtener estructura de la tabla
        query_estructura = "DESCRIBE movimientos_inventario"
        estructura = db_manager.execute_query(query_estructura)
        
        if estructura:
            print(f"✅ Columnas encontradas: {len(estructura)}")
            print("\n📋 Lista de columnas:")
            
            columnas = []
            for i, col in enumerate(estructura, 1):
                nombre_col = col['Field']
                tipo_col = col['Type']
                columnas.append(nombre_col)
                print(f"   {i:2d}. {nombre_col} ({tipo_col})")
            
            # Buscar columnas importantes
            columnas_importantes = {
                'id': 'ID del movimiento',
                'item_id': 'ID del item (antiguo)',
                'inventario_id': 'ID del inventario (nuevo)',
                'tipo_movimiento': 'Tipo de movimiento',
                'cantidad': 'Cantidad movida',
                'fecha_movimiento': 'Fecha del movimiento',
                'motivo': 'Motivo del movimiento',
                'observaciones': 'Observaciones',
                'usuario_id': 'ID del usuario',
                'referencia': 'Referencia'
            }
            
            print(f"\n🎯 Verificación de columnas importantes:")
            for col, desc in columnas_importantes.items():
                existe = col in columnas
                print(f"   {'✅' if existe else '❌'} {col}: {'Existe' if existe else 'No existe'} - {desc}")
            
            # Sugerir columnas para consulta
            print(f"\n💡 Columnas recomendadas para consulta:")
            columnas_recomendadas = []
            for col in ['id', 'cantidad', 'fecha_movimiento', 'usuario_id']:
                if col in columnas:
                    columnas_recomendadas.append(col)
            
            if columnas_recomendadas:
                print(f"   📊 Básicas: {', '.join(columnas_recomendadas)}")
            
            # Buscar columnas de texto para motivo
            columnas_texto = [col for col in columnas if 'text' in col['Type'].lower() or 'varchar' in col['Type'].lower() for col in estructura]
            if columnas_texto:
                print(f"   📝 Para motivo: {', '.join([col['Field'] for col in columnas_texto[:3]])}")
            
            return columnas
            
        else:
            print("❌ No se pudo obtener la estructura")
            return []
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    verificar_columnas_movimientos()

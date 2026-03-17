#!/usr/bin/env python3
"""
Script simplificado para verificar las columnas de movimientos_inventario
"""

import sys
import os
sys.path.append('.')

def verificar_columnas_movimientos_simple():
    """Verificar columnas de movimientos_inventario sin errores de cursor"""
    try:
        print("🔍 Verificando Columnas de movimientos_inventario")
        print("=" * 50)
        
        from web_app import db_manager
        
        # Consulta simple para obtener una fila y ver sus columnas
        query_test = "SELECT * FROM movimientos_inventario LIMIT 1"
        
        try:
            resultado = db_manager.execute_query(query_test)
            
            if resultado:
                # Obtener columnas de la primera fila
                columnas = list(resultado[0].keys())
                print(f"✅ Columnas encontradas: {len(columnas)}")
                print("\n📋 Lista de columnas:")
                
                for i, col in enumerate(columnas, 1):
                    print(f"   {i:2d}. {col}")
                
                # Verificar columnas importantes
                columnas_importantes = ['id', 'item_id', 'inventario_id', 'tipo_movimiento', 'cantidad', 'fecha_movimiento', 'motivo', 'observaciones', 'usuario_id']
                
                print(f"\n🎯 Verificación de columnas importantes:")
                for col in columnas_importantes:
                    existe = col in columnas
                    print(f"   {'✅' if existe else '❌'} {col}: {'Existe' if existe else 'No existe'}")
                
                return columnas
            else:
                print("⚠️ No hay datos en movimientos_inventario")
                print("   💡 Intentando con DESCRIBE...")
                
                # Intentar con DESCRIBE como fallback
                try:
                    query_describe = "DESCRIBE movimientos_inventario"
                    estructura = db_manager.execute_query(query_describe)
                    
                    if estructura:
                        columnas = [col['Field'] for col in estructura]
                        print(f"✅ Columnas obtenidas con DESCRIBE: {len(columnas)}")
                        
                        for i, col in enumerate(columnas, 1):
                            print(f"   {i:2d}. {col}")
                        
                        return columnas
                    else:
                        print("❌ No se pudo obtener estructura")
                        return []
                        
                except Exception as e2:
                    print(f"❌ Error con DESCRIBE: {e2}")
                    return []
                
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            return []
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    columnas = verificar_columnas_movimientos_simple()
    
    if columnas:
        print(f"\n💡 Resumen:")
        print(f"   📊 Total columnas: {len(columnas)}")
        print(f"   🔍 Columna para motivo: {'motivo' if 'motivo' in columnas else 'No existe'}")
        print(f"   🔍 Columna para item: {'inventario_id' if 'inventario_id' in columnas else 'item_id' if 'item_id' in columnas else 'No existe'}")

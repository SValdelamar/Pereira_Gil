#!/usr/bin/env python3
"""
Función para obtener la foto frontal de items y equipos
"""

import os
import glob

def obtener_foto_frontal(item_id, item_nombre, item_type='item'):
    """
    Obtiene la foto frontal de un item o equipo
    
    Args:
        item_id: ID del item/equipo
        item_nombre: Nombre del item/equipo
        item_type: 'item' o 'equipo'
    
    Returns:
        str: Ruta relativa a la foto frontal o None si no existe
    """
    try:
        # Buscar en ambas ubicaciones posibles
        rutas_busqueda = []
        
        # Ruta 1: imagenes/entrenamiento/{tipo}/{id}/
        ruta_entrenamiento = f'imagenes/entrenamiento/{item_type}/{item_id}'
        if os.path.exists(ruta_entrenamiento):
            rutas_busqueda.append(ruta_entrenamiento)
        
        # Ruta 2: imagenes/{tipo}/{nombre}/
        # Limpiar el nombre para usar como ruta
        nombre_limpio = item_nombre.replace(' ', '_').replace('/', '_').replace('\\', '_')
        ruta_registro = f'imagenes/{item_type}/{nombre_limpio}'
        if os.path.exists(ruta_registro):
            rutas_busqueda.append(ruta_registro)
        
        print(f"[DEBUG] Buscando foto para {item_type} {item_id} en rutas: {rutas_busqueda}")
        
        foto_frontal = None
        
        for ruta in rutas_busqueda:
            # Buscar archivos que contengan "frontal" en el nombre
            archivos_frontal = glob.glob(os.path.join(ruta, '*frontal*.jpg'))
            if archivos_frontal:
                foto_frontal = archivos_frontal[0]
                print(f"[DEBUG] Foto frontal encontrada: {foto_frontal}")
                break
            
            # Si no hay "frontal", buscar la primera imagen
            archivos_jpg = glob.glob(os.path.join(ruta, '*.jpg'))
            if archivos_jpg:
                foto_frontal = archivos_jpg[0]
                print(f"[DEBUG] Primera imagen encontrada: {foto_frontal}")
                break
        
        # Convertir a ruta relativa para el template
        if foto_frontal:
            ruta_relativa = os.path.relpath(foto_frontal, '.').replace('\\', '/')
            print(f"[DEBUG] Ruta relativa: {ruta_relativa}")
            return ruta_relativa
        
        print(f"[DEBUG] No se encontró foto para {item_type} {item_id}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo foto frontal: {e}")
        return None

def test_obtener_fotos():
    """Probar la función de obtener fotos"""
    print("🧪 PRUEBA: Obtener Fotos Frontales")
    print("=" * 40)
    
    # Probar con algunos IDs de ejemplo
    ejemplos = [
        {'id': '1', 'nombre': 'Control de televisor', 'type': 'equipo'},
        {'id': '1', 'nombre': 'Laptop Dell', 'type': 'item'},
    ]
    
    for ejemplo in ejemplos:
        print(f"\n📋 Probando {ejemplo['type']} {ejemplo['id']}: {ejemplo['nombre']}")
        foto = obtener_foto_frontal(ejemplo['id'], ejemplo['nombre'], ejemplo['type'])
        if foto:
            print(f"   ✅ Foto encontrada: {foto}")
        else:
            print(f"   ❌ No se encontró foto")

if __name__ == "__main__":
    test_obtener_fotos()

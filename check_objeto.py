#!/usr/bin/env python3
"""
Verificar estado del objeto para reconocimiento visual con buenas prácticas
"""

import mysql.connector
import os
from dotenv import load_dotenv

def verificar_objeto_reconocimiento():
    """Verificar y configurar objeto para IA visual"""
    try:
        # Cargar variables de entorno con buenas prácticas
        load_dotenv('.env_produccion')
        
        # Conectar a BD con configuración segura
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'laboratorio_sistema'),
            autocommit=False  # Control manual de transacciones
        )
        cursor = conn.cursor()
        
        print('🔗 Conexión a BD exitosa')
        
        # Verificar estructura de tablas
        cursor.execute('SHOW TABLES LIKE %s', ('objetos',))
        if not cursor.fetchone():
            print('❌ Tabla objetos no existe')
            print('🔧 Ejecuta: python migrate.py')
            return False
        
        print('✅ Tabla objetos existe')
        
        # Verificar si obj_4 ya existe
        cursor.execute('SELECT id, nombre, reconocer FROM objetos WHERE nombre = %s', ('obj_4',))
        result = cursor.fetchone()
        
        if result:
            obj_id, nombre, reconocer = result
            print(f'✅ Objeto encontrado: ID={obj_id}, Nombre={nombre}, Reconocer={reconocer}')
            
            # Verificar imágenes asociadas
            cursor.execute('SELECT vista, nombre_archivo FROM objetos_imagenes WHERE objeto_id = %s', (obj_id,))
            imagenes = cursor.fetchall()
            
            if imagenes:
                print(f'✅ Imágenes asociadas ({len(imenes)}):')
                for vista, archivo in imagenes:
                    print(f'  📸 {vista}: {archivo}')
            else:
                print('❌ No hay imágenes asociadas al objeto')
                registrar_imagenes(cursor, obj_id)
            
            # Verificar si reconocer está activado
            if not reconocer:
                print('⚠️  El objeto existe pero reconocer=0 (desactivado)')
                print('🔧 Activando reconocimiento...')
                cursor.execute('UPDATE objetos SET reconocer = 1 WHERE id = %s', (obj_id,))
                conn.commit()
                print('✅ Reconocimiento activado')
                
        else:
            print('❌ El objeto obj_4 no existe en BD')
            print('🔧 Creando objeto con buenas prácticas...')
            cursor.execute(
                'INSERT INTO objetos (nombre, categoria, descripcion, reconocer) VALUES (%s, %s, %s, %s)',
                ('obj_4', 'equipo', 'Objeto de prueba para IA visual', 1)
            )
            conn.commit()
            
            # Obtener ID del objeto creado
            cursor.execute('SELECT id FROM objetos WHERE nombre = %s', ('obj_4',))
            obj_id = cursor.fetchone()[0]
            print(f'✅ Objeto creado con ID={obj_id} y reconocer=1')
            
            # Registrar imágenes
            registrar_imagenes(cursor, obj_id)
        
        # Verificar estado final
        verificar_estado_final(cursor, obj_id if 'obj_id' in locals() else result[0])
        
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f'❌ Error de BD: {e}')
        print('💡 Verifica tus credenciales en .env_produccion')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def registrar_imagenes(cursor, obj_id):
    """Registrar imágenes del objeto en BD con buenas prácticas"""
    img_dir = 'imagenes/objetos'
    
    if not os.path.exists(img_dir):
        print(f'❌ Directorio {img_dir} no existe')
        return
    
    imagenes_registradas = 0
    
    for filename in os.listdir(img_dir):
        if filename.startswith('obj_4_') and filename.endswith('.jpg'):
            filepath = os.path.join(img_dir, filename)
            vista = filename.replace('obj_4_', '').replace('.jpg', '')
            
            try:
                # Leer archivo de forma segura
                with open(filepath, 'rb') as f:
                    img_data = f.read()
                
                # Insertar con parámetros seguros
                cursor.execute(
                    'INSERT IGNORE INTO objetos_imagenes (objeto_id, vista, imagen, nombre_archivo) VALUES (%s, %s, %s, %s)',
                    (obj_id, vista, img_data, filename)
                )
                
                imagenes_registradas += 1
                print(f'  📸 Imagen registrada: {filename} (vista: {vista})')
                
            except Exception as e:
                print(f'  ⚠️  Error registrando {filename}: {e}')
    
    if imagenes_registradas > 0:
        print(f'✅ {imagenes_registradas} imágenes registradas exitosamente')

def verificar_estado_final(cursor, obj_id):
    """Verificar estado final del objeto"""
    print('\n📊 Estado final del objeto:')
    
    # Verificar objeto
    cursor.execute('SELECT nombre, reconocer FROM objetos WHERE id = %s', (obj_id,))
    obj = cursor.fetchone()
    print(f'  Objeto: {obj[0]}, Reconocer: {obj[1]}')
    
    # Verificar imágenes
    cursor.execute('SELECT vista, nombre_archivo FROM objetos_imagenes WHERE objeto_id = %s', (obj_id,))
    imagenes = cursor.fetchall()
    print(f'  Imágenes: {len(imenes)} registradas')
    
    for vista, archivo in imagenes:
        print(f'    📸 {vista}: {archivo}')

if __name__ == "__main__":
    print("🔍 Verificando objeto para reconocimiento visual...")
    print("=" * 50)
    
    if verificar_objeto_reconocimiento():
        print("\n✅ Verificación completada")
        print("🎯 El objeto está configurado para reconocimiento visual")
        print("📝 Reinicia el servidor Flask si es necesario")
    else:
        print("\n❌ No se pudo completar la verificación")

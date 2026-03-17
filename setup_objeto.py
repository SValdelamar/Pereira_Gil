#!/usr/bin/env python3.    
"""
Script para registrar objeto de prueba en BD para reconocimiento visual
"""

import mysql.connector
import os

def setup_objeto_reconocimiento():
    try:
        # Conectar a BD
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='laboratorio_sistema'
        )
        cursor = conn.cursor()
        
        print("🔗 Conectado a la base de datos")
        
        # Verificar tabla objetos
        cursor.execute("SHOW TABLES LIKE 'objetos'")
        if not cursor.fetchone():
            print("❌ La tabla 'objetos' no existe. Ejecuta las migraciones primero.")
            return False
        
        print("✅ Tabla 'objetos' encontrada")
        
        # Insertar objeto de prueba
        cursor.execute("""
            INSERT IGNORE INTO objetos (nombre, categoria, descripcion, reconocer) 
            VALUES ('obj_4', 'equipo', 'Objeto de prueba para reconocimiento visual', 1)
        """)
        
        # Obtener ID del objeto
        cursor.execute("SELECT id FROM objetos WHERE nombre='obj_4'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ No se pudo crear el objeto")
            return False
        
        obj_id = result[0]
        print(f"✅ Objeto creado con ID: {obj_id}")
        
        # Procesar imágenes
        img_dir = 'imagenes/objetos'
        if not os.path.exists(img_dir):
            print(f"❌ Directorio {img_dir} no existe")
            return False
        
        imagenes_encontradas = 0
        for filename in os.listdir(img_dir):
            if filename.startswith('obj_4_') and filename.endswith('.jpg'):
                filepath = os.path.join(img_dir, filename)
                vista = filename.replace('obj_4_', '').replace('.jpg', '')
                
                # Leer archivo
                with open(filepath, 'rb') as f:
                    img_data = f.read()
                
                # Insertar en BD
                cursor.execute("""
                    INSERT IGNORE INTO objetos_imagenes 
                    (objeto_id, vista, imagen, nombre_archivo) 
                    VALUES (%s, %s, %s, %s)
                """, (obj_id, vista, img_data, filename))
                
                imagenes_encontradas += 1
                print(f"  📸 Imagen registrada: {filename} (vista: {vista})")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Proceso completado: {imagenes_encontradas} imágenes registradas")
        print("🎯 El objeto 'obj_4' está listo para reconocimiento visual")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando objeto para reconocimiento visual...")
    if setup_objeto_reconocimiento():
        print("\n✅ ¡Listo! Ahora puedes probar el reconocimiento visual.")
        print("📝 Reinicia el servidor Flask y prueba con las imágenes del objeto.")
    else:
        print("\n❌ No se pudo completar la configuración.")

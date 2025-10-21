#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para poblar la base de datos con datos realistas para testing
Genera datos como si fueran ingresados por usuarios reales
"""

import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import json
from faker import Faker

# Cargar configuración
if os.path.exists('.env_produccion'):
    load_dotenv('.env_produccion')

DB_CONFIG = {
    'host': os.getenv('HOST', 'localhost'),
    'user': os.getenv('USUARIO_PRODUCCION', 'root'),
    'password': os.getenv('PASSWORD_PRODUCCION', ''),
    'database': os.getenv('BASE_DATOS', 'laboratorio_sistema'),
    'charset': 'utf8mb4'
}

# Colores para consola
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_step(text):
    print(f"{Colors.OKCYAN}▶ {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

# Inicializar Faker en español
fake = Faker('es_CO')  # Colombia

# Datos realistas para el contexto del SENA
PROGRAMAS_FORMACION = [
    'Técnico en Química',
    'Técnico en Análisis de Muestras',
    'Técnico en Operaciones Químicas',
    'Técnico en Control de Calidad',
    'Técnico en Laboratorio Clínico',
    'Tecnólogo en Química Industrial',
    'Técnico en Sistemas',
    'Técnico en Mecánica',
    'Técnico en Electrónica'
]

ESPECIALIDADES_QUIMICA = [
    'Química Analítica',
    'Química Orgánica',
    'Química Inorgánica',
    'Química Industrial',
    'Análisis Instrumental',
    'Control de Calidad',
    'Química Ambiental'
]

CARGOS_FUNCIONARIOS = [
    'Secretario Académico',
    'Asistente Administrativo',
    'Coordinador de Área',
    'Auxiliar de Biblioteca',
    'Coordinador de Bienestar'
]

DEPENDENCIAS = [
    'Coordinación Académica',
    'Dirección',
    'Bienestar al Aprendiz',
    'Biblioteca',
    'Recursos Educativos'
]

CATEGORIAS_EQUIPOS = [
    'Microscopios',
    'Balanzas',
    'Espectrofotómetros',
    'Centrífugas',
    'pHmetros',
    'Agitadores',
    'Estufas',
    'Refrigeradores',
    'Destiladores'
]

CATEGORIAS_ITEMS = [
    'Reactivos',
    'Material de Vidrio',
    'Consumibles',
    'Equipos de Protección',
    'Material de Limpieza'
]

EQUIPOS_TIPOS = {
    'Microscopios': ['Microscopio Óptico Binocular', 'Microscopio Trinocular', 'Microscopio Estereoscópico'],
    'Balanzas': ['Balanza Analítica', 'Balanza de Precisión', 'Balanza Granataria'],
    'Espectrofotómetros': ['Espectrofotómetro UV-Vis', 'Espectrofotómetro IR', 'Espectrofotómetro de Absorción Atómica'],
    'Centrífugas': ['Centrífuga de Mesa', 'Microcentrífuga', 'Centrífuga Refrigerada'],
    'pHmetros': ['pHmetro de Mesa', 'pHmetro Portátil', 'Electrodo de pH'],
    'Agitadores': ['Agitador Magnético', 'Agitador Mecánico', 'Vortex'],
    'Estufas': ['Estufa de Secado', 'Mufla', 'Incubadora'],
}

ITEMS_TIPOS = {
    'Reactivos': ['Ácido Sulfúrico', 'Hidróxido de Sodio', 'Ácido Clorhídrico', 'Etanol', 'Acetona'],
    'Material de Vidrio': ['Vaso de Precipitado', 'Matraz Erlenmeyer', 'Probeta', 'Pipeta Volumétrica', 'Bureta'],
    'Consumibles': ['Guantes de Nitrilo', 'Papel Filtro', 'Tubos de Ensayo', 'Cajas de Petri', 'Puntas para Micropipeta'],
}

MARCAS_EQUIPOS = ['Mettler Toledo', 'Thermo Fisher', 'Ohaus', 'Hanna Instruments', 'IKA', 'Labnet', 'Cole-Parmer']

def generar_ficha():
    """Genera número de ficha realista del SENA"""
    return f"{random.randint(2800000, 2900000)}"

def generar_documento():
    """Genera número de documento realista colombiano"""
    return f"{random.randint(1000000000, 1099999999)}"

def seed_usuarios(cursor, conn, num_aprendices=15, num_funcionarios=5, num_instructores=8):
    """Generar usuarios realistas"""
    print_step(f"Generando {num_aprendices} aprendices, {num_funcionarios} funcionarios y {num_instructores} instructores...")
    
    query = """
        INSERT INTO usuarios (id, nombre, tipo, nivel_acceso, password_hash, email, telefono, activo, 
                             programa, ficha, cargo, dependencia, programa_formacion, especialidad, 
                             a_cargo_inventario, laboratorio_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    usuarios_creados = []
    
    # APRENDICES (Nivel 1)
    for i in range(num_aprendices):
        nombre = fake.name()
        doc_id = generar_documento()
        programa = random.choice(PROGRAMAS_FORMACION)
        ficha = generar_ficha()
        email = f"{nombre.lower().replace(' ', '.')}@misena.edu.co"
        telefono = f"30{random.randint(10000000, 99999999)}"
        
        try:
            cursor.execute(query, (
                doc_id, nombre, 'aprendiz', 1, 'pass123', email, telefono, 1,
                programa, ficha, None, None, None, None, 0, None
            ))
            usuarios_creados.append((doc_id, nombre, 'Aprendiz'))
        except mysql.connector.IntegrityError:
            pass
    
    # FUNCIONARIOS (Nivel 2)
    for i in range(num_funcionarios):
        nombre = fake.name()
        doc_id = generar_documento()
        cargo = random.choice(CARGOS_FUNCIONARIOS)
        dependencia = random.choice(DEPENDENCIAS)
        email = f"{nombre.lower().replace(' ', '.')}@sena.edu.co"
        telefono = f"31{random.randint(10000000, 99999999)}"
        
        try:
            cursor.execute(query, (
                doc_id, nombre, 'funcionario', 2, 'pass123', email, telefono, 1,
                None, None, cargo, dependencia, None, None, 0, None
            ))
            usuarios_creados.append((doc_id, nombre, 'Funcionario'))
        except mysql.connector.IntegrityError:
            pass
    
    # INSTRUCTORES - Niveles 3, 4 y 5
    niveles_instructores = [
        (3, num_instructores // 3, None),  # No química
        (4, num_instructores // 3, 'Química'),  # Química sin inventario
        (5, num_instructores - (2 * (num_instructores // 3)), 'Química')  # Química con inventario
    ]
    
    for nivel, cantidad, programa_base in niveles_instructores:
        for i in range(cantidad):
            nombre = fake.name()
            doc_id = generar_documento()
            
            if programa_base == 'Química':
                programa = 'Química'
                especialidad = random.choice(ESPECIALIDADES_QUIMICA)
            else:
                programa = random.choice([p for p in PROGRAMAS_FORMACION if 'Química' not in p])
                especialidad = programa
            
            email = f"{nombre.lower().replace(' ', '.')}@sena.edu.co"
            telefono = f"32{random.randint(10000000, 99999999)}"
            
            a_cargo = 1 if nivel == 5 else 0
            lab_id = random.randint(1, 2) if nivel == 5 else None
            
            try:
                cursor.execute(query, (
                    doc_id, nombre, 'instructor', nivel, 'pass123', email, telefono, 1,
                    None, None, None, None, programa, especialidad, a_cargo, lab_id
                ))
                tipo_instructor = f"Instructor Nivel {nivel}"
                if nivel == 5:
                    tipo_instructor += " (A cargo)"
                usuarios_creados.append((doc_id, nombre, tipo_instructor))
            except mysql.connector.IntegrityError:
                pass
    
    # ADMIN
    try:
        cursor.execute(query, (
            'admin', 'Administrador Sistema', 'administrador', 6, 'admin123',
            'admin@sena.edu.co', '3501234567', 1,
            None, None, None, None, None, None, 0, None
        ))
        usuarios_creados.append(('admin', 'Administrador Sistema', 'Administrador'))
    except mysql.connector.IntegrityError:
        pass
    
    conn.commit()
    print_success(f"{len(usuarios_creados)} usuarios creados")
    
    return usuarios_creados

def seed_equipos(cursor, conn, num_equipos=30):
    """Generar equipos realistas"""
    print_step(f"Generando {num_equipos} equipos...")
    
    query = """
        INSERT INTO equipos (id, equipo_id, nombre, tipo, estado, ubicacion, laboratorio_id,
                           marca, modelo, numero_serie, especificaciones, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    equipos_creados = []
    estados = ['disponible', 'disponible', 'disponible', 'en_uso', 'mantenimiento']
    
    for i in range(num_equipos):
        categoria = random.choice(list(EQUIPOS_TIPOS.keys()))
        tipo_equipo = random.choice(EQUIPOS_TIPOS[categoria])
        marca = random.choice(MARCAS_EQUIPOS)
        modelo = f"{fake.bothify(text='??-###')}"
        serie = f"{fake.bothify(text='SN-########')}"
        estado = random.choice(estados)
        lab_id = random.randint(1, 2)
        ubicacion = f"Mesón {random.randint(1, 10)}, Lab {lab_id}"
        
        equipo_id = f"EQ-{categoria[:3].upper()}-{i+1:03d}"
        id_equipo = f"equipo_{equipo_id.lower().replace('-', '_')}"
        
        especificaciones = {
            "capacidad": f"{random.choice(['100g', '200g', '500g', '1kg', '5L', '10L'])}",
            "precision": f"±{random.choice(['0.001', '0.01', '0.1'])}",
            "voltaje": "110-220V"
        }
        
        observaciones = random.choice([
            "Equipo en excelente estado",
            "Requiere calibración trimestral",
            "Uso exclusivo para análisis cuantitativos",
            "Verificar limpieza después de cada uso",
            None
        ])
        
        try:
            cursor.execute(query, (
                id_equipo, equipo_id, f"{marca} {tipo_equipo}", categoria, estado, ubicacion, lab_id,
                marca, modelo, serie, json.dumps(especificaciones), observaciones
            ))
            equipos_creados.append((id_equipo, tipo_equipo, estado))  # Guardar id_equipo, no equipo_id
        except mysql.connector.IntegrityError:
            pass
    
    conn.commit()
    print_success(f"{len(equipos_creados)} equipos creados")
    
    return equipos_creados

def seed_inventario(cursor, conn, num_items=40):
    """Generar items de inventario realistas"""
    print_step(f"Generando {num_items} items de inventario...")
    
    query = """
        INSERT INTO inventario (id, nombre, categoria, cantidad_actual, cantidad_minima, unidad,
                               ubicacion, laboratorio_id, proveedor, costo_unitario, 
                               fecha_vencimiento, lote, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    items_creados = []
    proveedores = ['LabChem S.A.', 'QuímicaPro', 'Reactivos Unidos', 'Sigma-Aldrich', 'Merck']
    
    for i in range(num_items):
        categoria = random.choice(list(ITEMS_TIPOS.keys()))
        tipo_item = random.choice(ITEMS_TIPOS[categoria])
        
        if categoria == 'Reactivos':
            unidad = random.choice(['mL', 'L', 'g', 'kg'])
            cantidad_actual = random.randint(100, 5000)
            cantidad_minima = cantidad_actual // 4
            costo_unitario = round(random.uniform(15.00, 250.00), 2)
            fecha_venc = (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d')
        elif categoria == 'Material de Vidrio':
            unidad = 'unidades'
            cantidad_actual = random.randint(5, 50)
            cantidad_minima = 5
            costo_unitario = round(random.uniform(5.00, 80.00), 2)
            fecha_venc = None
        else:
            unidad = random.choice(['unidades', 'cajas', 'paquetes'])
            cantidad_actual = random.randint(10, 100)
            cantidad_minima = 10
            costo_unitario = round(random.uniform(8.00, 120.00), 2)
            fecha_venc = None
        
        lab_id = random.randint(1, 2)
        ubicacion = f"Estante {random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 5)}, Lab {lab_id}"
        
        item_id = f"INV-{categoria[:3].upper()}-{i+1:03d}"
        proveedor = random.choice(proveedores)
        lote = f"L{fake.bothify(text='####??')}" if categoria == 'Reactivos' else None
        
        observaciones = random.choice([
            f"Grado Analítico - {random.choice(['Alta pureza', 'Uso general', 'Certificado'])}",
            "Almacenar en lugar fresco y seco",
            "Manipular con precaución",
            "Revisar fecha de vencimiento",
            None
        ])
        
        try:
            cursor.execute(query, (
                item_id, tipo_item, categoria, cantidad_actual, cantidad_minima, unidad,
                ubicacion, lab_id, proveedor, costo_unitario, fecha_venc, lote, observaciones
            ))
            items_creados.append((item_id, tipo_item, cantidad_actual, unidad))
        except mysql.connector.IntegrityError:
            pass
    
    conn.commit()
    print_success(f"{len(items_creados)} items creados")
    
    return items_creados

def seed_reservas(cursor, conn, usuarios, equipos, num_reservas=20):
    """Generar reservas realistas"""
    print_step(f"Generando {num_reservas} reservas...")
    
    # Filtrar solo aprendices
    aprendices = [u for u in usuarios if u[2] == 'Aprendiz']
    if not aprendices or not equipos:
        print_warning("No hay suficientes usuarios o equipos para generar reservas")
        return []
    
    query = """
        INSERT INTO reservas (usuario_id, equipo_id, fecha_reserva, hora_inicio, hora_fin, 
                            estado, practica, observaciones, aprobada_por, fecha_aprobacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    reservas_creadas = []
    estados = ['pendiente', 'aprobada', 'aprobada', 'aprobada', 'completada', 'cancelada']
    
    for i in range(num_reservas):
        usuario = random.choice(aprendices)
        equipo = random.choice(equipos)
        
        fecha_reserva = fake.date_between(start_date='-30d', end_date='+30d')
        hora_inicio = f"{random.randint(7, 16):02d}:00:00"
        hora_fin = f"{random.randint(int(hora_inicio[:2])+1, 18):02d}:00:00"
        
        estado = random.choice(estados)
        practica = random.choice([
            'Análisis Volumétrico',
            'Preparación de Soluciones',
            'Análisis Gravimétrico',
            'Identificación de Sustancias',
            'Control de Calidad',
            'Práctica de Titulación'
        ])
        
        observaciones = random.choice([
            f"Práctica con el instructor {fake.name()}",
            "Trabajo en grupo",
            "Proyecto de formación",
            None
        ])
        
        aprobada_por = None
        fecha_aprobacion = None
        if estado in ['aprobada', 'completada']:
            aprobada_por = '5001'  # Instructor a cargo
            fecha_aprobacion = fecha_reserva - timedelta(days=random.randint(1, 3))
        
        try:
            cursor.execute(query, (
                usuario[0], equipo[0], fecha_reserva, hora_inicio, hora_fin,
                estado, practica, observaciones, aprobada_por, fecha_aprobacion
            ))
            reservas_creadas.append((usuario[1], equipo[1], estado))
        except Exception as e:
            pass
    
    conn.commit()
    print_success(f"{len(reservas_creadas)} reservas creadas")
    
    return reservas_creadas

def asignar_responsables_laboratorios(cursor, conn, usuarios):
    """Asignar instructores reales como responsables de laboratorios"""
    print_step("Asignando instructores responsables a laboratorios...")
    
    # Filtrar instructores nivel 5 (a cargo de inventario)
    instructores_nivel5 = [u for u in usuarios if 'Instructor Nivel 5' in u[2]]
    
    if not instructores_nivel5:
        print_warning("No hay instructores nivel 5 para asignar")
        return
    
    # Obtener laboratorios existentes
    cursor.execute("SELECT id, codigo, nombre FROM laboratorios WHERE tipo = 'laboratorio'")
    laboratorios = cursor.fetchall()
    
    if not laboratorios:
        print_warning("No hay laboratorios para asignar")
        return
    
    asignaciones = []
    for i, lab in enumerate(laboratorios):
        # Asignar un instructor (rotar si hay más labs que instructores)
        instructor = instructores_nivel5[i % len(instructores_nivel5)]
        
        try:
            cursor.execute("""
                UPDATE laboratorios 
                SET responsable = %s 
                WHERE id = %s
            """, (instructor[0], lab[0]))  # instructor[0] es el ID del usuario
            asignaciones.append((lab[2], instructor[1]))  # nombre lab, nombre instructor
        except Exception as e:
            print_warning(f"Error asignando {instructor[1]} a {lab[2]}: {e}")
    
    conn.commit()
    print_success(f"{len(asignaciones)} laboratorios asignados a instructores")
    
    # Mostrar asignaciones
    for lab_nombre, instructor_nombre in asignaciones:
        print(f"  • {lab_nombre} → {instructor_nombre}")
    
    return asignaciones

def main():
    print_header("SEED DATABASE - CENTRO MINERO SENA")
    print("Este script generará datos realistas para testing")
    print("Los datos simulan información ingresada por usuarios reales\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ").lower()
    if respuesta != 's':
        print_warning("Operación cancelada")
        return
    
    try:
        # Conectar a la base de datos
        print_step("Conectando a la base de datos...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print_success("Conectado exitosamente")
        
        # Generar datos
        usuarios = seed_usuarios(cursor, conn, num_aprendices=15, num_funcionarios=5, num_instructores=9)
        asignar_responsables_laboratorios(cursor, conn, usuarios)  # NUEVO
        equipos = seed_equipos(cursor, conn, num_equipos=30)
        items = seed_inventario(cursor, conn, num_items=40)
        reservas = seed_reservas(cursor, conn, usuarios, equipos, num_reservas=20)
        
        # Resumen
        print_header("RESUMEN DE DATOS GENERADOS")
        print(f"✓ Usuarios: {len(usuarios)}")
        print(f"  - Aprendices: {len([u for u in usuarios if u[2] == 'Aprendiz'])}")
        print(f"  - Funcionarios: {len([u for u in usuarios if u[2] == 'Funcionario'])}")
        print(f"  - Instructores: {len([u for u in usuarios if 'Instructor' in u[2]])}")
        print(f"  - Administrador: 1")
        print(f"\n✓ Equipos: {len(equipos)}")
        print(f"✓ Items de inventario: {len(items)}")
        print(f"✓ Reservas: {len(reservas)}")
        
        print("\n" + "="*80)
        print_success("BASE DE DATOS POBLADA EXITOSAMENTE")
        print("="*80)
        print("\n📝 Credenciales de prueba:")
        print("  Usuario: admin | Contraseña: admin123")
        print("  Usuarios generados: (documento) | Contraseña: pass123")
        print("\n🚀 Ahora puedes probar el sistema con datos realistas!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

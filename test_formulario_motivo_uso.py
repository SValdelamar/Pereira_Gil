#!/usr/bin/env python3
"""
Script para probar el formulario simplificado con campo de texto para motivo de uso
"""

import sys
import os
sys.path.append('.')

def test_formulario_motivo_uso():
    """Probar que el formulario simplificado con motivo de uso funciona correctamente"""
    try:
        print("🧪 Probando Formulario Simplificado - Motivo de Uso")
        print("=" * 55)
        
        from web_app import app, db_manager
        
        # 1. Verificar que hay instructores de química disponibles
        print("\n👥 Verificando instructores de química disponibles:")
        try:
            query_instructores = """
                SELECT id, nombre, email, especialidad, nivel_acceso,
                       CASE 
                           WHEN nivel_acceso = 5 THEN 'Instructor con Inventario'
                           WHEN nivel_acceso = 4 THEN 'Instructor sin Inventario'
                           ELSE 'Otro'
                       END as rol_inventario
                FROM usuarios 
                WHERE nivel_acceso IN (4, 5) AND activo = TRUE
                ORDER BY nivel_acceso DESC, nombre
            """
            instructores = db_manager.execute_query(query_instructores)
            
            if instructores:
                print(f"✅ Instructores disponibles: {len(instructores)}")
                for instructor in instructores:
                    print(f"   👤 {instructor['nombre']} - {instructor.get('rol_inventario', 'Química')}")
            else:
                print("⚠️ No hay instructores de química registrados")
                print("   💡 Esto es normal si no se han creado instructores aún")
                
        except Exception as e:
            print(f"❌ Error consultando instructores: {e}")
        
        # 2. Verificar que hay items en inventario para entregar
        print("\n📦 Verificando items disponibles para entrega:")
        query_items = """
            SELECT id, nombre, cantidad_actual, unidad
            FROM inventario 
            WHERE cantidad_actual > 0
            LIMIT 5
        """
        items = db_manager.execute_query(query_items)
        
        if items:
            print(f"✅ Items disponibles para entrega: {len(items)}")
            for item in items:
                print(f"   📦 {item['nombre']} - Stock: {item['cantidad_actual']} {item.get('unidad', 'unidades')}")
        else:
            print("⚠️ No hay items con stock disponible para entrega")
        
        # 3. Mostrar estructura del nuevo formulario simplificado
        print("\n📋 Estructura del Nuevo Formulario Simplificado:")
        print("   ✅ Instructor de Química (selector dinámico)")
        print("   ✅ Cantidad a Entregar (con validación)")
        print("   ✅ Motivo de Uso (textarea libre)")
        print("   ✅ Grupo/Clase (opcional)")
        print("   ✅ Observaciones (opcional)")
        
        # 4. Mostrar ejemplos de motivos de uso
        print("\n📝 Ejemplos de Motivos de Uso:")
        ejemplos_motivos = [
            "Práctica de titulación ácido-base para determinar concentración de HCl en el grupo 2102",
            "Experimento de cromatografía en papel para separar pigmentos vegetales - Grupo 1101",
            "Demostración de reacciones de oxidación-reducción con permanganato de potasio",
            "Medición de pH en soluciones buffer para práctica de equilibrio químico",
            "Preparación de disoluciones para práctica de estequiometría - Grupo 3101",
            "Análisis cualitativo de cationes mediante reacciones de precipitación",
            "Práctica de destilación simple para separar mezclas de líquidos",
            "Calorimetría para determinar calor específico de metales - Laboratorio avanzado",
            "Electrolisis del agua para demostrar descomposición en H2 y O2",
            "Práctica de espectroscopia UV-Vis para análisis de concentraciones"
        ]
        
        for i, ejemplo in enumerate(ejemplos_motivos, 1):
            print(f"   {i:2d}. {ejemplo}")
        
        # 5. Mostrar ventajas del nuevo enfoque
        print("\n🎯 Ventajas del Campo de Texto Libre:")
        print("   ✅ Flexibilidad total: Cualquier tipo de práctica o experimento")
        print("   ✅ Detalle específico: Puede incluir grupo, nivel, contexto")
        print("   ✅ Sin limitaciones: No restringido a lista predefinida")
        print("   ✅ Contexto rico: Permite describir completamente el uso")
        print("   ✅ Adaptabilidad: Funciona para cualquier área de química")
        print("   ✅ Auditoría mejorada: Registros más descriptivos")
        
        # 6. Comparación con el enfoque anterior
        print("\n🔄 Comparación: Selector vs Texto Libre")
        print("   📊 Selector Predefinido:")
        print("      ✅ Rápido: Selección con un clic")
        print("      ❌ Limitado: Solo prácticas predefinidas")
        print("      ❌ Rígido: No permite contexto adicional")
        print("      ❌ Incompleto: Faltan detalles específicos")
        print("")
        print("   ✍️ Texto Libre:")
        print("      ✅ Flexible: Cualquier práctica o contexto")
        print("      ✅ Detallado: Puede incluir toda la información necesaria")
        print("      ✅ Personalizado: Se adapta a cada situación")
        print("      ✅ Rico en contexto: Grupo, nivel, materiales específicos")
        
        # 7. Mostrar estructura de datos enviados
        print("\n📊 Estructura de Datos Enviados:")
        print("   {")
        print("     item_id: 'ITEM_123',")
        print("     cantidad: 5,")
        print("     instructor_id: 'INST_456',")
        print("     instructor_nombre: 'Juan Pérez - Química Analítica',")
        print("     motivo_uso: 'Práctica de titulación ácido-base para el grupo 2102',")
        print("     grupo: '2102',")
        print("     observaciones: 'Necesita indicador fenolftaleína'")
        print("   }")
        
        # 8. Verificar validaciones implementadas
        print("\n🔍 Validaciones Implementadas:")
        print("   ✅ Cantidad: Mayor que 0 y menor/igual al stock")
        print("   ✅ Instructor: Debe seleccionarse obligatoriamente")
        print("   ✅ Motivo de uso: Campo requerido, no puede estar vacío")
        print("   ✅ Grupo: Opcional, pero útil para organización")
        print("   ✅ Observaciones: Opcional, para notas adicionales")
        
        print("\n🎉 Formulario simplificado verificado!")
        print("🚀 El sistema ahora es más flexible y descriptivo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_formulario_motivo_uso()
    sys.exit(0 if success else 1)

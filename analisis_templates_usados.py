#!/usr/bin/env python3
"""
Análisis detallado de templates realmente utilizados vs existentes
"""

import sys
import os
import re
sys.path.append('.')

def analizar_templates_usados():
    """Analizar qué templates realmente se usan en el código"""
    try:
        print("🔍 ANÁLISIS DETALLADO: TEMPLATES UTILIZADOS VS EXISTENTES")
        print("=" * 65)
        
        # 1. Leer el código fuente de web_app.py
        print("\n📋 1. Análisis de web_app.py:")
        
        web_app_path = "web_app.py"
        with open(web_app_path, 'r', encoding='utf-8') as f:
            web_app_content = f.read()
        
        # Buscar todas las referencias a render_template
        render_template_matches = re.findall(r'render_template\([\'"]([^\'\"]+)[\'"]', web_app_content)
        
        print(f"   📊 Total referencias a render_template: {len(render_template_matches)}")
        
        # Contar frecuencia de cada template
        template_usos = {}
        for template in render_template_matches:
            template_usos[template] = template_usos.get(template, 0) + 1
        
        print("\n   📋 Templates referenciados en web_app.py:")
        for template, count in sorted(template_usos.items()):
            print(f"      📄 {template}: {count} vez(es)")
        
        # 2. Templates existentes en el sistema
        print("\n📁 2. Templates existentes en el sistema:")
        
        templates_dir = "app/templates/modules"
        templates_existentes = []
        
        for file in os.listdir(templates_dir):
            if file.endswith('.html'):
                templates_existentes.append(f"modules/{file}")
        
        print(f"   📊 Total templates existentes: {len(templates_existentes)}")
        
        for template in sorted(templates_existentes):
            print(f"      📄 {template}")
        
        # 3. Comparación: usados vs existentes
        print("\n🔄 3. Comparación: Templates Usados vs Existentes:")
        
        templates_usados = set(template_usos.keys())
        templates_existentes_set = set(templates_existentes)
        
        # Templates usados que no existen
        usados_no_existentes = templates_usados - templates_existentes_set
        if usados_no_existentes:
            print(f"   🚨 Templates referenciados pero no existen: {len(usados_no_existentes)}")
            for template in sorted(usados_no_existentes):
                print(f"      ❌ {template}")
        else:
            print("   ✅ Todos los templates referenciados existen")
        
        # Templates existentes pero no usados
        existentes_no_usados = templates_existentes_set - templates_usados
        if existentes_no_usados:
            print(f"   ⚠️ Templates existentes pero no referenciados: {len(existentes_no_usados)}")
            for template in sorted(existentes_no_usados):
                print(f"      ⚠️ {template}")
        else:
            print("   ✅ Todos los templates existentes están referenciados")
        
        # 4. Análisis específico de templates problemáticos
        print("\n🎯 4. Análisis de Templates Específicos:")
        
        templates_analizar = [
            'modules/inventario_detalle_simple.html',
            'modules/equipo_detalle.html',
            'modules/laboratorio_detalle.html',
            'modules/ayuda.html',
            'modules/backup.html',
            'modules/configuracion.html'
        ]
        
        for template in templates_analizar:
            if template in templates_usados:
                print(f"   ✅ {template}: EN USO ({template_usos[template]} referencia/s)")
            else:
                print(f"   ❌ {template}: NO USADO")
        
        # 5. Análisis de tamaño y complejidad
        print("\n📏 5. Análisis de Tamaño y Complejidad:")
        
        template_info = []
        for template in templates_existentes:
            template_path = os.path.join(templates_dir, template.replace('modules/', ''))
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                template_info.append({
                    'nombre': template,
                    'tamano': len(content),
                    'lineas': len(content.splitlines()),
                    'usado': template in templates_usados
                })
        
        # Ordenar por tamaño
        template_info.sort(key=lambda x: x['tamano'], reverse=True)
        
        print("   📋 Templates por tamaño:")
        for info in template_info:
            estado = "✅" if info['usado'] else "❌"
            print(f"      {estado} {info['nombre']}: {info['tamano']:,} bytes, {info['lineas']} líneas")
        
        # 6. Recomendaciones específicas
        print("\n💡 6. Recomendaciones Específicas:")
        
        recomendaciones = []
        
        # Templates no usados
        if existentes_no_usados:
            recomendaciones.append("🗑️ ELIMINAR templates no utilizados:")
            for template in sorted(existentes_no_usados):
                # Obtener tamaño
                info = next((i for i in template_info if i['nombre'] == template), None)
                if info:
                    recomendaciones.append(f"   - {template} ({info['tamano']:,} bytes)")
        
        # Templates duplicados
        if 'modules/inventario_detalle_simple.html' in existentes_no_usados:
            recomendaciones.append("🔄 CONSOLIDAR templates duplicados:")
            recomendaciones.append("   - inventario_detalle_simple.html es redundante con inventario_detalle.html")
        
        # Templates grandes no usados
        grandes_no_usados = [i for i in template_info if not i['usado'] and i['tamano'] > 10000]
        if grandes_no_usados:
            recomendaciones.append("📊 REVISAR templates grandes no usados:")
            for info in grandes_no_usados:
                recomendaciones.append(f"   - {info['nombre']} ({info['tamano']:,} bytes)")
        
        # Templates pequeños
        pequenos = [i for i in template_info if i['tamano'] < 5000]
        if pequenos:
            recomendaciones.append("📏 ANALIZAR templates pequeños:")
            for info in pequenos:
                estado = "usado" if info['usado'] else "no usado"
                recomendaciones.append(f"   - {info['nombre']} ({info['tamano']:,} bytes) - {estado}")
        
        for rec in recomendaciones:
            print(f"   {rec}")
        
        # 7. Plan de acción
        print("\n🚀 7. Plan de Acción Sugerido:")
        
        print("   🎯 PRIORIDAD ALTA:")
        print("      1. Eliminar inventario_detalle_simple.html (obsoleto)")
        print("      2. Revisar si equipo_detalle.html realmente se usa")
        print("      3. Verificar laboratorio_detalle.html")
        print()
        
        print("   🎯 PRIORIDAD MEDIA:")
        print("      4. Analizar templates grandes no usados")
        print("      5. Consolidar funcionalidades duplicadas")
        print("      6. Documentar mapa de navegación")
        print()
        
        print("   🎯 PRIORIDAD BAJA:")
        print("      7. Optimizar templates grandes")
        print("      8. Estandarizar estructura de templates")
        print("      9. Mejorar documentación")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analizar_templates_usados()
    sys.exit(0 if success else 1)

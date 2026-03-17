#!/usr/bin/env python3
"""
Análisis completo de templates para identificar inconsistencias y funcionalidades no utilizadas
"""

import sys
import os
import re
sys.path.append('.')

def analizar_templates():
    """Analizar todos los templates para encontrar inconsistencias"""
    try:
        print("🔍 ANÁLISIS COMPLETO DE TEMPLATES")
        print("=" * 50)
        
        from web_app import app
        
        # 1. Obtener todas las rutas definidas en Flask
        print("\n📋 1. Rutas Definidas en Flask:")
        
        rutas_flask = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                rutas_flask.append({
                    'ruta': rule.rule,
                    'metodos': list(rule.methods - {'HEAD', 'OPTIONS'}),
                    'endpoint': rule.endpoint
                })
        
        print(f"   📊 Total rutas encontradas: {len(rutas_flask)}")
        
        # Agrupar rutas por tipo
        rutas_get = [r for r in rutas_flask if 'GET' in r['metodos']]
        rutas_post = [r for r in rutas_flask if 'POST' in r['metodos']]
        
        print(f"      📄 Rutas GET: {len(rutas_get)}")
        print(f"      📝 Rutas POST: {len(rutas_post)}")
        
        # 2. Analizar templates existentes
        print("\n📁 2. Templates Existentes:")
        
        templates_dir = "app/templates/modules"
        templates = []
        
        for file in os.listdir(templates_dir):
            if file.endswith('.html'):
                file_path = os.path.join(templates_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                templates.append({
                    'nombre': file,
                    'ruta': file_path,
                    'tamano': len(content),
                    'contenido': content
                })
        
        print(f"   📊 Total templates: {len(templates)}")
        
        # Ordenar por tamaño
        templates.sort(key=lambda x: x['tamano'], reverse=True)
        
        print("\n   📋 Templates por tamaño:")
        for template in templates:
            print(f"      📄 {template['nombre']}: {template['tamano']:,} bytes")
        
        # 3. Mapear rutas a templates
        print("\n🔗 3. Mapeo Rutas → Templates:")
        
        # Buscar referencias a templates en el código
        ruta_template_map = {}
        
        for ruta in rutas_flask:
            if 'GET' in ruta['metodos']:
                # Buscar en el código fuente qué template usa esta ruta
                endpoint_name = ruta['endpoint']
                
                # Intentar encontrar el template asociado
                template_asociado = None
                
                # Buscar patrones comunes
                if 'dashboard' in endpoint_name:
                    template_asociado = 'dashboard/dashboard.html'
                elif 'login' in endpoint_name:
                    template_asociado = 'auth/login.html'
                elif 'inventario' in endpoint_name:
                    if 'detalle' in endpoint_name:
                        template_asociado = 'modules/inventario_detalle.html'
                    else:
                        template_asociado = 'modules/inventario.html'
                elif 'equipos' in endpoint_name:
                    if 'detalle' in endpoint_name:
                        template_asociado = 'modules/equipo_detalle.html'
                    else:
                        template_asociado = 'modules/equipos.html'
                elif 'laboratorios' in endpoint_name:
                    if 'detalle' in endpoint_name:
                        template_asociado = 'modules/laboratorio_detalle.html'
                    else:
                        template_asociado = 'modules/laboratorios.html'
                elif 'reservas' in endpoint_name:
                    template_asociado = 'modules/reservas.html'
                elif 'usuarios' in endpoint_name:
                    template_asociado = 'modules/usuarios.html'
                elif 'reportes' in endpoint_name:
                    template_asociado = 'modules/reportes.html'
                elif 'perfil' in endpoint_name:
                    template_asociado = 'modules/perfil.html'
                
                ruta_template_map[ruta['ruta']] = {
                    'endpoint': endpoint_name,
                    'template': template_asociado,
                    'metodos': ruta['metodos']
                }
        
        # 4. Identificar templates no referenciados
        print("\n🚨 4. Templates Posiblemente No Utilizados:")
        
        templates_usados = set()
        for info in ruta_template_map.values():
            if info['template']:
                templates_usados.add(info['template'])
        
        templates_no_usados = []
        for template in templates:
            template_path = f"modules/{template['nombre']}"
            if template_path not in templates_usados:
                templates_no_usados.append(template)
        
        if templates_no_usados:
            print(f"   ⚠️ Templates potencialmente no usados: {len(templates_no_usados)}")
            for template in templates_no_usados:
                print(f"      📄 {template['nombre']} ({template['tamano']:,} bytes)")
        else:
            print("   ✅ Todos los templates parecen estar referenciados")
        
        # 5. Analizar navegación y enlaces
        print("\n🔗 5. Análisis de Navegación:")
        
        # Buscar enlaces internos en los templates
        enlaces_internos = {}
        
        for template in templates:
            enlaces = re.findall(r'href=["\']([^"\']+)["\']', template['contenido'])
            enlaces_internos[template['nombre']] = enlaces
        
        # Analizar consistencia de navegación
        print("   🔍 Enlaces internos encontrados:")
        for template_name, enlaces in enlaces_internos.items():
            enlaces_validos = [e for e in enlaces if e.startswith('/') and not e.startswith('//')]
            if enlaces_validos:
                print(f"      📄 {template_name}: {len(enlaces_validos)} enlaces")
        
        # 6. Identificar funcionalidades duplicadas
        print("\n🔄 6. Funcionalidades Potencialmente Duplicadas:")
        
        # Buscar templates con nombres similares
        nombres_similares = {}
        
        for template in templates:
            nombre_base = template['nombre'].replace('.html', '')
            
            # Buscar patrones comunes
            if 'detalle' in nombre_base:
                if 'detalles' not in nombres_similares:
                    nombres_similares['detalles'] = []
                nombres_similares['detalles'].append(template['nombre'])
            elif 'registro' in nombre_base:
                if 'registros' not in nombres_similares:
                    nombres_similares['registros'] = []
                nombres_similares['registros'].append(template['nombre'])
        
        for categoria, templates_cat in nombres_similares.items():
            if len(templates_cat) > 1:
                print(f"   ⚠️ {categoria}: {templates_cat}")
        
        # 7. Analizar templates pequeños (posiblemente obsoletos)
        print("\n📏 7. Templates Pequeños (posiblemente obsoletos):")
        
        templates_pequenos = [t for t in templates if t['tamano'] < 5000]
        
        if templates_pequenos:
            print(f"   📏 Templates pequeños (< 5KB): {len(templates_pequenos)}")
            for template in templates_pequenos:
                print(f"      📄 {template['nombre']}: {template['tamano']:,} bytes")
                
                # Analizar contenido
                if 'inventario_detalle_simple' in template['nombre']:
                    print("         → Posiblemente versión simplificada obsoleta")
        else:
            print("   ✅ No hay templates unusually pequeños")
        
        # 8. Recomendaciones
        print("\n💡 8. Recomendaciones:")
        
        recomendaciones = []
        
        if templates_no_usados:
            recomendaciones.append(f"🗑️ Revisar {len(templates_no_usados)} templates potencialmente no usados")
        
        if templates_pequenos:
            recomendaciones.append(f"📏 Analizar {len(templates_pequenos)} templates pequeños")
        
        if any(len(cat) > 1 for cat in nombres_similares.values()):
            recomendaciones.append("🔄 Consolidar funcionalidades duplicadas")
        
        recomendaciones.extend([
            "🔗 Verificar consistencia de enlaces internos",
            "📋 Documentar mapa de navegación actual",
            "🧹 Limpiar código no utilizado",
            "📊 Optimizar templates grandes"
        ])
        
        for rec in recomendaciones:
            print(f"   {rec}")
        
        # 9. Análisis específico de templates problemáticos
        print("\n🎯 9. Análisis Específico:")
        
        # Template inventario_detalle_simple
        template_simple = next((t for t in templates if 'inventario_detalle_simple' in t['nombre']), None)
        if template_simple:
            print(f"   📄 inventario_detalle_simple.html:")
            print(f"      📏 Tamaño: {template_simple['tamano']:,} bytes")
            print(f"      🔍 Contenido: {template_simple['contenido'][:200]}...")
            print(f"      ⚠️ Posiblemente obsoleto, ya existe inventario_detalle.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analizar_templates()
    sys.exit(0 if success else 1)

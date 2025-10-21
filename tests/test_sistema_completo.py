#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Testing y Análisis del Sistema Web
Analiza rutas, templates, enlaces y funcionalidades para detectar elementos obsoletos
"""

import os
import re
from pathlib import Path
import json

# =====================================================================
# CONFIGURACIÓN
# =====================================================================
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'
WEB_APP_FILE = BASE_DIR / 'web_app.py'
STATIC_DIR = BASE_DIR / 'static'

# =====================================================================
# CLASE PRINCIPAL DE ANÁLISIS
# =====================================================================
class SistemaAnalyzer:
    def __init__(self):
        self.routes = []
        self.templates = []
        self.links_found = {}
        self.templates_sin_ruta = []
        self.rutas_sin_template = []
        self.enlaces_rotos = []
        self.funcionalidades_obsoletas = []
        
    def extraer_rutas_flask(self):
        """Extrae todas las rutas @app.route de web_app.py"""
        print("\n📍 Extrayendo rutas de Flask...")
        
        with open(WEB_APP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar @app.route
        pattern = r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)"
        matches = re.finditer(pattern, content)
        
        for match in matches:
            route = match.group(1)
            methods = match.group(2) if match.group(2) else 'GET'
            self.routes.append({
                'path': route,
                'methods': methods.replace("'", "").replace('"', ''),
                'full': match.group(0)
            })
        
        print(f"  ✓ Encontradas {len(self.routes)} rutas")
        return self.routes
    
    def extraer_templates(self):
        """Lista todos los templates HTML"""
        print("\n📄 Extrayendo templates HTML...")
        
        if not TEMPLATES_DIR.exists():
            print("  ✗ Carpeta templates no encontrada")
            return []
        
        for html_file in TEMPLATES_DIR.glob('*.html'):
            self.templates.append(html_file.name)
        
        print(f"  ✓ Encontrados {len(self.templates)} templates")
        return self.templates
    
    def analizar_enlaces_en_templates(self):
        """Analiza todos los enlaces dentro de los templates HTML"""
        print("\n🔗 Analizando enlaces en templates...")
        
        total_enlaces = 0
        
        for template in self.templates:
            template_path = TEMPLATES_DIR / template
            self.links_found[template] = {
                'url_for': [],
                'href': [],
                'src': [],
                'action': []
            }
            
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar url_for en el contenido
                url_for_pattern = r"url_for\(['\"]([^'\"]+)['\"]"
                url_fors = re.findall(url_for_pattern, content)
                self.links_found[template]['url_for'] = list(set(url_fors))
                
                # Buscar hrefs usando regex
                href_pattern = r'href=["\']([^"\']+)["\']'
                hrefs = re.findall(href_pattern, content)
                for href in hrefs:
                    if href and not href.startswith(('http', '#', 'javascript', 'mailto', '{{')):
                        self.links_found[template]['href'].append(href)
                
                # Buscar src de scripts e imágenes
                src_pattern = r'src=["\']([^"\']+)["\']'
                srcs = re.findall(src_pattern, content)
                for src in srcs:
                    if src and not src.startswith(('http', '//', 'data:', '{{')):
                        self.links_found[template]['src'].append(src)
                
                # Buscar forms con action
                action_pattern = r'<form[^>]*action=["\']([^"\']+)["\']'
                actions = re.findall(action_pattern, content, re.IGNORECASE)
                for action in actions:
                    if action and not action.startswith(('http', '{{')):
                        self.links_found[template]['action'].append(action)
                
                total = sum(len(v) for v in self.links_found[template].values())
                total_enlaces += total
                
            except Exception as e:
                print(f"  ✗ Error en {template}: {e}")
        
        print(f"  ✓ Analizados {total_enlaces} enlaces totales")
    
    def validar_rutas_vs_templates(self):
        """Compara rutas definidas con templates usados"""
        print("\n🔍 Validando coherencia rutas ↔ templates...")
        
        # Leer web_app.py para encontrar render_template
        with open(WEB_APP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Templates usados en render_template
        templates_usados = set(re.findall(r"render_template\(['\"]([^'\"]+\.html)['\"]", content))
        
        # Buscar templates usados con {% extends %}
        for template in self.templates:
            template_path = TEMPLATES_DIR / template
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    # Buscar {% extends 'nombre.html' %}
                    extends = re.findall(r"{%\s*extends\s+['\"]([^'\"]+)['\"]", template_content)
                    templates_usados.update(extends)
            except:
                pass
        
        templates_existentes = set(self.templates)
        
        # Templates que existen pero nunca se usan
        self.templates_sin_ruta = list(templates_existentes - templates_usados)
        
        # Templates referenciados pero que no existen
        self.rutas_sin_template = list(templates_usados - templates_existentes)
        
        if self.templates_sin_ruta:
            print(f"  ⚠️  {len(self.templates_sin_ruta)} templates NO usados:")
            for t in sorted(self.templates_sin_ruta):
                print(f"     - {t}")
        
        if self.rutas_sin_template:
            print(f"  ✗ {len(self.rutas_sin_template)} templates referenciados pero NO existen:")
            for t in sorted(self.rutas_sin_template):
                print(f"     - {t}")
        
        if not self.templates_sin_ruta and not self.rutas_sin_template:
            print("  ✅ Todos los templates están correctamente vinculados")
    
    def validar_enlaces_internos(self):
        """Valida que los enlaces internos apunten a rutas existentes"""
        print("\n🔗 Validando enlaces internos...")
        
        rutas_disponibles = [r['path'] for r in self.routes]
        
        # Crear lista de funciones disponibles (nombres de rutas)
        with open(WEB_APP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        funciones = re.findall(r'def (\w+)\(', content)
        
        enlaces_problematicos = []
        
        # Endpoints especiales de Flask que son válidos
        endpoints_especiales = ['static', 'index']
        
        for template, links in self.links_found.items():
            for func in links['url_for']:
                if func not in funciones and func not in endpoints_especiales:
                    enlaces_problematicos.append({
                        'template': template,
                        'tipo': 'url_for',
                        'valor': func,
                        'problema': 'Función no existe'
                    })
        
        self.enlaces_rotos = enlaces_problematicos
        
        if enlaces_problematicos:
            print(f"  ⚠️  {len(enlaces_problematicos)} enlaces con problemas:")
            for link in enlaces_problematicos[:10]:  # Mostrar máximo 10
                print(f"     - {link['template']}: {link['tipo']}('{link['valor']}')")
        else:
            print("  ✅ Todos los enlaces internos son válidos")
    
    def detectar_elementos_obsoletos(self):
        """Detecta elementos obsoletos en los templates"""
        print("\n🗑️  Detectando elementos obsoletos...")
        
        obsoletos_patrones = [
            ('Bootstrap 3', r'bootstrap[/-]3'),
            ('jQuery viejo', r'jquery[/-]1\.[0-9]'),
            ('Font Awesome 4', r'font-awesome[/-]4'),
            ('Comentarios TODO', r'<!--.*TODO:.*-->'),  # Solo comentarios HTML con TODO:
            ('Código comentado', r'<!--.*<script.*-->'),
            ('console.log', r'console\.log\('),  # Llamadas a console.log
        ]
        
        for template in self.templates:
            template_path = TEMPLATES_DIR / template
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for nombre, patron in obsoletos_patrones:
                    if re.search(patron, content, re.IGNORECASE):
                        self.funcionalidades_obsoletas.append({
                            'template': template,
                            'tipo': nombre,
                            'descripcion': f'Contiene {nombre}'
                        })
            except Exception as e:
                pass
        
        if self.funcionalidades_obsoletas:
            print(f"  ⚠️  {len(self.funcionalidades_obsoletas)} elementos obsoletos encontrados")
            # Agrupar por tipo
            tipos = {}
            for item in self.funcionalidades_obsoletas:
                tipo = item['tipo']
                if tipo not in tipos:
                    tipos[tipo] = []
                tipos[tipo].append(item['template'])
            
            for tipo, templates in tipos.items():
                print(f"     - {tipo}: {len(templates)} archivos")
        else:
            print("  ✅ No se encontraron elementos obsoletos comunes")
    
    def verificar_archivos_estaticos(self):
        """Verifica archivos estáticos referenciados"""
        print("\n📦 Verificando archivos estáticos...")
        
        archivos_faltantes = []
        
        for template, links in self.links_found.items():
            for src in links['src']:
                # Ignorar rutas dinámicas con variables JavaScript
                if '${' in src or '{{' in src or src.startswith('/api/'):
                    continue
                
                # Limpiar la ruta
                src_clean = src.strip('/').replace('{{ url_for("static", filename="', '').replace('") }}', '')
                
                if src_clean.startswith('static/'):
                    file_path = BASE_DIR / src_clean
                else:
                    file_path = STATIC_DIR / src_clean
                
                if not file_path.exists():
                    archivos_faltantes.append({
                        'template': template,
                        'archivo': src
                    })
        
        if archivos_faltantes:
            print(f"  ⚠️  {len(archivos_faltantes)} archivos estáticos no encontrados")
            for item in archivos_faltantes[:5]:
                print(f"     - {item['template']}: {item['archivo']}")
        else:
            print("  ✅ Archivos estáticos OK")
    
    def generar_reporte(self):
        """Genera un reporte completo en formato Markdown"""
        print("\n📊 Generando reporte completo...")
        
        reporte = f"""# 📋 Reporte de Análisis del Sistema Web

**Fecha:** {Path(__file__).stat().st_mtime}  
**Sistema:** Centro Minero SENA - Gestión de Laboratorios

---

## 📊 Estadísticas Generales

- **Rutas Flask:** {len(self.routes)}
- **Templates HTML:** {len(self.templates)}
- **Enlaces totales:** {sum(sum(len(v) for v in links.values()) for links in self.links_found.values())}

---

## ⚠️  Problemas Encontrados

### 1. Templates sin usar ({len(self.templates_sin_ruta)})
"""
        
        if self.templates_sin_ruta:
            reporte += "\n**Estos templates existen pero NO se usan en ninguna ruta:**\n\n"
            for t in sorted(self.templates_sin_ruta):
                reporte += f"- `{t}`\n"
        else:
            reporte += "\n✅ Todos los templates están en uso\n"
        
        reporte += f"\n### 2. Templates referenciados pero inexistentes ({len(self.rutas_sin_template)})\n"
        
        if self.rutas_sin_template:
            reporte += "\n**Estos templates se referencian en el código pero NO existen:**\n\n"
            for t in sorted(self.rutas_sin_template):
                reporte += f"- `{t}` ⚠️\n"
        else:
            reporte += "\n✅ Todas las referencias son válidas\n"
        
        reporte += f"\n### 3. Enlaces con problemas ({len(self.enlaces_rotos)})\n"
        
        if self.enlaces_rotos:
            reporte += "\n"
            for link in self.enlaces_rotos[:20]:
                reporte += f"- **{link['template']}:** `{link['tipo']}('{link['valor']}')` - {link['problema']}\n"
        else:
            reporte += "\n✅ Todos los enlaces son válidos\n"
        
        reporte += f"\n### 4. Elementos obsoletos ({len(self.funcionalidades_obsoletas)})\n"
        
        if self.funcionalidades_obsoletas:
            # Agrupar por tipo
            tipos = {}
            for item in self.funcionalidades_obsoletas:
                tipo = item['tipo']
                if tipo not in tipos:
                    tipos[tipo] = []
                tipos[tipo].append(item['template'])
            
            for tipo, templates in tipos.items():
                reporte += f"\n**{tipo}:**\n"
                for t in templates[:10]:
                    reporte += f"- `{t}`\n"
        else:
            reporte += "\n✅ No se encontraron elementos obsoletos\n"
        
        reporte += "\n---\n\n## 📁 Lista Completa de Rutas\n\n"
        
        # Agrupar rutas por prefijo
        rutas_por_prefijo = {}
        for route in sorted(self.routes, key=lambda x: x['path']):
            prefix = route['path'].split('/')[1] if '/' in route['path'] and len(route['path']) > 1 else 'root'
            if prefix not in rutas_por_prefijo:
                rutas_por_prefijo[prefix] = []
            rutas_por_prefijo[prefix].append(route)
        
        for prefix, routes in sorted(rutas_por_prefijo.items()):
            reporte += f"\n### /{prefix}\n\n"
            for route in routes:
                reporte += f"- `{route['path']}` - [{route['methods']}]\n"
        
        reporte += "\n---\n\n## 🎯 Recomendaciones\n\n"
        
        if self.templates_sin_ruta:
            reporte += "1. **Eliminar templates no usados** para reducir confusión\n"
        
        if self.rutas_sin_template:
            reporte += "2. **Crear o corregir referencias** a templates faltantes\n"
        
        if self.enlaces_rotos:
            reporte += "3. **Corregir enlaces rotos** en los templates\n"
        
        if self.funcionalidades_obsoletas:
            reporte += "4. **Actualizar dependencias obsoletas** (Bootstrap, jQuery, etc.)\n"
        
        if not any([self.templates_sin_ruta, self.rutas_sin_template, self.enlaces_rotos, self.funcionalidades_obsoletas]):
            reporte += "✅ **El sistema está bien estructurado y no requiere limpieza urgente**\n"
        
        reporte += "\n---\n\n*Reporte generado automáticamente por test_sistema_completo.py*\n"
        
        # Guardar reporte
        reporte_path = BASE_DIR / 'REPORTE_ANALISIS_SISTEMA.md'
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print(f"  ✓ Reporte guardado en: {reporte_path.name}")
        
        return reporte
    
    def ejecutar_analisis_completo(self):
        """Ejecuta todos los análisis"""
        print("=" * 80)
        print(" ANÁLISIS COMPLETO DEL SISTEMA WEB")
        print("=" * 80)
        
        self.extraer_rutas_flask()
        self.extraer_templates()
        self.analizar_enlaces_en_templates()
        self.validar_rutas_vs_templates()
        self.validar_enlaces_internos()
        self.detectar_elementos_obsoletos()
        self.verificar_archivos_estaticos()
        self.generar_reporte()
        
        print("\n" + "=" * 80)
        print(" ✅ ANÁLISIS COMPLETADO")
        print("=" * 80)
        print(f"\n📄 Revisa el archivo: REPORTE_ANALISIS_SISTEMA.md\n")

# =====================================================================
# EJECUCIÓN PRINCIPAL
# =====================================================================
if __name__ == '__main__':
    analyzer = SistemaAnalyzer()
    analyzer.ejecutar_analisis_completo()

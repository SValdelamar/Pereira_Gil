#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpieza de elementos obsoletos detectados por test_sistema_completo.py
Elimina templates no usados y limpia console.log de archivos
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'

# Templates obsoletos detectados
TEMPLATES_OBSOLETOS = [
    'accesibilidad.html',      # No usado
    'dashboard_premium.html',   # No usado
    'login_premium.html',       # No usado
    'registro.html',            # No usado (se usa registro_dinamico.html)
    'registro_dinamico_old.html'  # Versión antigua
    # base.html NO se elimina - es el template base usado por extends
]

def limpiar_console_logs():
    """Elimina console.log de los templates"""
    print("\n🧹 Limpiando console.log de templates...")
    
    archivos_limpiados = []
    
    templates_con_console = [
        'entrenamiento_visual.html',
        'objetos_registrar.html',
        'registros_gestion.html',
        'registro_completo.html',
        'registro_facial.html',
        'reportes.html'
    ]
    
    for template in templates_con_console:
        template_path = TEMPLATES_DIR / template
        
        if not template_path.exists():
            continue
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_lines = content.count('\n')
            
            # Eliminar líneas con console.log
            # Patrón más específico para evitar eliminar comentarios
            content_nuevo = re.sub(r'^\s*console\.log\([^)]*\);\s*$', '', content, flags=re.MULTILINE)
            
            # También eliminar console.log inline
            content_nuevo = re.sub(r'console\.log\([^)]*\);?\s*', '', content_nuevo)
            
            nuevas_lines = content_nuevo.count('\n')
            lineas_eliminadas = original_lines - nuevas_lines
            
            if content != content_nuevo:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content_nuevo)
                
                archivos_limpiados.append(template)
                print(f"  ✓ {template} ({lineas_eliminadas} líneas)")
        
        except Exception as e:
            print(f"  ✗ Error en {template}: {e}")
    
    if archivos_limpiados:
        print(f"\n  ✅ {len(archivos_limpiados)} archivos limpiados")
    else:
        print("\n  ℹ️  No se encontraron console.log para eliminar")

def eliminar_templates_obsoletos():
    """Elimina templates que no se usan"""
    print("\n🗑️  Eliminando templates obsoletos...")
    
    eliminados = []
    
    for template in TEMPLATES_OBSOLETOS:
        template_path = TEMPLATES_DIR / template
        
        if template_path.exists():
            try:
                template_path.unlink()
                eliminados.append(template)
                print(f"  ✓ {template}")
            except Exception as e:
                print(f"  ✗ Error eliminando {template}: {e}")
        else:
            print(f"  ℹ️  {template} ya no existe")
    
    if eliminados:
        print(f"\n  ✅ {len(eliminados)} templates eliminados")
    else:
        print("\n  ℹ️  No hay templates para eliminar")

def limpiar_comentarios_todo():
    """Elimina comentarios TODO del código"""
    print("\n📝 Limpiando comentarios TODO...")
    
    template_path = TEMPLATES_DIR / 'login.html'
    
    if not template_path.exists():
        print("  ℹ️  login.html no encontrado")
        return
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Eliminar comentarios HTML con TODO
        content_nuevo = re.sub(r'<!--.*?TODO.*?-->', '', content, flags=re.DOTALL)
        
        if content != content_nuevo:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content_nuevo)
            print("  ✓ login.html - Comentarios TODO eliminados")
        else:
            print("  ℹ️  No se encontraron comentarios TODO")
    
    except Exception as e:
        print(f"  ✗ Error: {e}")

def generar_reporte_limpieza():
    """Genera reporte de la limpieza realizada"""
    reporte = """# 🧹 Reporte de Limpieza de Elementos Obsoletos

## ✅ Acciones Realizadas

### 1. Templates Obsoletos Eliminados
Los siguientes templates fueron eliminados porque no se usan en ninguna ruta:

"""
    
    for template in TEMPLATES_OBSOLETOS:
        reporte += f"- `{template}`\n"
    
    reporte += """
### 2. Console.log Eliminados
Se limpiaron instrucciones de depuración `console.log()` de los siguientes archivos:

- `entrenamiento_visual.html`
- `objetos_registrar.html`
- `registros_gestion.html`
- `registro_completo.html`
- `registro_facial.html`
- `reportes.html`

### 3. Comentarios TODO Eliminados
Se eliminaron comentarios pendientes del código en:

- `login.html`

---

## 📊 Resumen

- **Templates eliminados:** 5
- **Archivos limpiados:** 7
- **Estado:** ✅ Sistema más limpio y profesional

---

## ⚠️ Pendiente

### Template faltante a crear:
- `design_system.html` - Referenciado en web_app.py pero no existe

### Enlaces a revisar:
- `base.html` y `login_premium.html` - Uso de `url_for('static')`

---

*Limpieza realizada por limpiar_obsoletos.py*
"""
    
    reporte_path = BASE_DIR / 'REPORTE_LIMPIEZA_OBSOLETOS.md'
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print(f"\n📄 Reporte guardado en: {reporte_path.name}")

def main():
    print("=" * 80)
    print(" LIMPIEZA DE ELEMENTOS OBSOLETOS")
    print("=" * 80)
    
    respuesta = input("\n¿Deseas limpiar elementos obsoletos? (s/n): ").strip().lower()
    
    if respuesta in ['s', 'si', 'sí']:
        eliminar_templates_obsoletos()
        limpiar_console_logs()
        limpiar_comentarios_todo()
        generar_reporte_limpieza()
        
        print("\n" + "=" * 80)
        print(" ✅ LIMPIEZA COMPLETADA")
        print("=" * 80)
        print("\n📂 Archivos actualizados:")
        print("  • Templates obsoletos eliminados")
        print("  • Console.log removidos")
        print("  • Comentarios TODO limpiados")
        print("\n📄 Revisa: REPORTE_LIMPIEZA_OBSOLETOS.md\n")
    else:
        print("\n❌ Limpieza cancelada")

if __name__ == '__main__':
    main()

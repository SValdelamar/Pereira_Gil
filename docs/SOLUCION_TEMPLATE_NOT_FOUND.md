# 🔧 Guía Rápida - Solución Error TemplateNotFound

## 🚨 Problema
```
jinja2.exceptions.TemplateNotFound: app.utils.modulos_config
```

## ✅ Solución Aplicada

### **Causa del Error:**
Jinja2 estaba tratando de importar `app.utils.modulos_config` como si fuera un template, pero es un módulo Python.

### **Solución Implementada:**

1. **Eliminada importación incorrecta en template:**
```html
<!-- ❌ ANTES (incorrecto) -->
{% from 'app.utils.modulos_config' import get_modulos_disponibles, get_acciones_rapidas_disponibles, get_estadisticas_disponibles %}
```

2. **Movida la lógica al backend (web_app.py):**
```python
# ✅ AHORA (correcto)
@app.route('/dashboard')
@require_login
def dashboard():
    stats = get_dashboard_stats()
    user_level = session.get('user_level', 1)
    
    try:
        from app.utils.modulos_config import (
            get_modulos_disponibles, 
            get_acciones_rapidas_disponibles, 
            get_estadisticas_disponibles
        )
        
        modulos_disponibles = get_modulos_disponibles(user_level)
        acciones_rapidas = get_acciones_rapidas_disponibles(user_level)
        estadisticas_visibles = get_estadisticas_disponibles(user_level)
        
    except Exception as e:
        print(f"[ERROR] Error cargando configuración de módulos: {e}")
        # Fallback: mostrar módulos básicos
        modulos_disponibles = []
        acciones_rapidas = []
        estadisticas_visibles = ['equipos_activos', 'total_laboratorios']
    
    return render_template('dashboard/dashboard.html', 
                         stats=stats, 
                         user=session,
                         modulos_disponibles=modulos_disponibles,
                         acciones_rapidas=acciones_rapidas,
                         estadisticas_visibles=estadisticas_visibles)
```

3. **Actualizado el template para usar variables del backend:**
```html
<!-- ✅ Template actualizado -->
{% set user_level = user.get('user_level', 1) %}
{% set estadisticas_visibles = estadisticas_visibles %}
{% set acciones_rapidas = acciones_rapidas %}
{% set modulos_disponibles = modulos_disponibles %}
```

## 🧪 Verificación

### **1. Probar el sistema de módulos:**
```bash
python test_modulos_dashboard.py
```

### **2. Probar integración del dashboard:**
```bash
python test_dashboard_integration.py
```

### **3. Iniciar la aplicación:**
```bash
python web_app.py
```

## 🎯 Resultado Esperado

- ✅ **Dashboard carga sin errores**
- ✅ **Módulos según nivel de usuario**
- ✅ **Estadísticas contextuales**
- ✅ **Acciones rápidas personalizadas**

## 📁 Archivos Modificados

1. **`web_app.py`** - Función dashboard actualizada
2. **`app/templates/dashboard/dashboard.html`** - Template corregido
3. **`test_dashboard_integration.py`** - Pruebas de integración

## 🔍 Si el Error Persiste

1. **Verificar que el archivo exista:**
```bash
ls -la app/utils/modulos_config.py
```

2. **Verificar importación:**
```python
python -c "from app.utils.modulos_config import get_modulos_disponibles; print('✅ OK')"
```

3. **Reiniciar el servidor Flask:**
```bash
# Detener (Ctrl+C) y reiniciar
python web_app.py
```

## 🎉 Solución Completa

El sistema ahora:
- ✅ **Funciona sin errores** de Jinja2
- ✅ **Muestra módulos** según nivel de usuario
- ✅ **Aplica buenas prácticas** de separación de responsabilidades
- ✅ **Tiene fallbacks** por si hay errores

**El dashboard está listo para usar con el sistema de módulos controlado por nivel de acceso.** 🚀

# 📁 Estructura CSS Modular - Centro Minero SENA

## 🎨 Arquitectura de Estilos

Esta es la estructura modular de CSS implementada siguiendo **buenas prácticas de desarrollo**:

```
app/static/css/
├── common.css      → Variables CSS, componentes reutilizables, estilos globales
├── auth.css        → Estilos compartidos para todas las páginas de autenticación
├── login.css       → Estilos específicos del login (actualmente vacío)
├── dashboard.css   → Estilos para dashboard y módulos internos
└── errors.css      → Estilos para páginas de error (404, 500)
```

---

## 📋 Descripción de Archivos

### `common.css` (Base)
**Propósito:** Contiene todo lo que se comparte entre módulos.

**Incluye:**
- ✅ Variables CSS (colores, espaciados, fuentes)
- ✅ Reset y estilos globales
- ✅ Componentes reutilizables (botones, formularios, alertas, cards, modales)
- ✅ Clases utilitarias (márgenes, padding, alineación)
- ✅ Animaciones comunes

**Uso:**
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
```

---

### `auth.css` (Autenticación)
**Propósito:** Estilos compartidos para todas las páginas de autenticación.

**Incluye:**
- ✅ Layout de autenticación (fondo animado, cards)
- ✅ Brand side (logo, features)
- ✅ Form side (formularios)
- ✅ Botones específicos de auth
- ✅ Responsive para móviles

**Páginas que lo usan:**
- `login.html`
- `registro_dinamico.html`
- `recuperar_contrasena.html`
- `verificar_codigo.html`
- `restablecer_contrasena.html`

**Uso:**
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/auth.css') }}" rel="stylesheet">
```

---

### `dashboard.css` (Dashboard y Módulos)
**Propósito:** Estilos para el dashboard y módulos internos del sistema.

**Incluye:**
- ✅ Sidebar de navegación
- ✅ Tarjetas de estadísticas
- ✅ Tablas de datos
- ✅ Badges y etiquetas
- ✅ Filtros y búsqueda
- ✅ Perfil de usuario
- ✅ Contenedores de gráficas

**Páginas que lo usan:**
- `dashboard.html`
- `usuarios.html`
- `laboratorios.html`
- `equipos.html`
- `inventario.html`
- `reservas.html`
- `reportes.html`
- etc.

**Uso:**
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/dashboard.css') }}" rel="stylesheet">
```

---

### `errors.css` (Páginas de Error)
**Propósito:** Estilos para páginas de error.

**Incluye:**
- ✅ Layout centrado
- ✅ Iconos animados
- ✅ Mensajes de error
- ✅ Botones de acción

**Páginas que lo usan:**
- `404.html`
- `500.html`

**Uso:**
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/errors.css') }}" rel="stylesheet">
```

---

## 🎨 Variables CSS Disponibles

### Colores SENA
```css
--color-sena-dark: #1e4d3b;
--color-sena-medium: #2d5a4a;
--color-sena-light: #3d6d5c;
--color-sena-accent: #6ee7b7;
--color-sena-success: #10b981;
```

### Espaciado
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
--spacing-3xl: 64px;
```

### Bordes
```css
--border-radius-sm: 8px;
--border-radius-md: 12px;
--border-radius-lg: 16px;
--border-radius-xl: 24px;
```

### Sombras
```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
--shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.25);
```

---

## ✨ Beneficios de esta Arquitectura

### 1. **Mantenibilidad**
- Un solo lugar para cambiar variables globales
- Código organizado por módulos
- Fácil localizar y modificar estilos

### 2. **Reutilización**
- Componentes compartidos en `common.css`
- No repetir código
- Consistencia visual en todo el sistema

### 3. **Rendimiento**
- Archivos más pequeños y específicos
- Mejor cacheo del navegador
- Carga solo lo necesario por página

### 4. **Escalabilidad**
- Fácil agregar nuevos módulos
- Estructura clara y organizada
- Documentación integrada

### 5. **Colaboración**
- Convenciones claras
- Código predecible
- Fácil para múltiples desarrolladores

---

## 📝 Guía de Uso

### Para una nueva página de autenticación:
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/auth.css') }}" rel="stylesheet">
<!-- Si necesitas estilos específicos, agrégalos inline o crea un nuevo archivo -->
```

### Para un nuevo módulo del dashboard:
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/dashboard.css') }}" rel="stylesheet">
```

### Para una página de error:
```html
<link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/errors.css') }}" rel="stylesheet">
```

---

## 🔧 Cómo Agregar Nuevos Estilos

### 1. Estilos Globales (todos los módulos)
➡️ Agregar en `common.css`

### 2. Estilos de Autenticación (login, registro, etc.)
➡️ Agregar en `auth.css`

### 3. Estilos del Dashboard (módulos internos)
➡️ Agregar en `dashboard.css`

### 4. Estilos Específicos de una Página
➡️ Crear un nuevo archivo CSS específico (ej: `inventario.css`)

---

## 🚀 Próximos Pasos

- [ ] Migrar todos los templates de `auth/` a usar CSS modular
- [ ] Migrar todos los templates de `modules/` a usar CSS modular
- [ ] Crear `components.css` si hay componentes muy específicos
- [ ] Implementar sistema de temas (modo claro/oscuro)
- [ ] Optimizar con minificación en producción

---

## 📚 Referencias

- [CSS Variables (Custom Properties)](https://developer.mozilla.org/es/docs/Web/CSS/Using_CSS_custom_properties)
- [BEM Methodology](http://getbem.com/)
- [CSS Architecture](https://www.smashingmagazine.com/2016/05/real-life-responsive-web-design/)
- [Atomic Design](https://bradfrost.com/blog/post/atomic-web-design/)

---

**Desarrollado por:** Steven Valdelamar, Karen Quintero, Zharick Camargo  
**Fecha:** Octubre 2025  
**Versión:** 1.0

# 📁 JavaScript - Módulos del Sistema

## 🎯 Archivos

### **`modal-fix.js`** - Solución Centralizada para Modales Bootstrap

**Propósito:** Resolver el problema de backdrops bloqueando la interacción con modales.

#### **Problema que Resuelve:**
- ❌ Backdrop de Bootstrap aparece encima del modal
- ❌ No se puede hacer click en botones del modal
- ❌ Usuario ve pantalla opaca sin poder interactuar

#### **Solución:**
1. ✅ Desactiva el backdrop automático de Bootstrap
2. ✅ Crea un backdrop personalizado 100% controlable
3. ✅ Se aplica automáticamente a TODOS los modales
4. ✅ No requiere código duplicado en cada archivo

#### **Características:**
- **Automático**: Se inicializa solo al cargar la página
- **Universal**: Funciona con cualquier modal de Bootstrap
- **Configurable**: Opciones de debug y personalización
- **Limpio**: Sin código duplicado
- **Eficiente**: Solo un backdrop para todos los modales

#### **Configuración:**

```javascript
const CONFIG = {
    backdropId: 'customModalBackdrop',  // ID del backdrop
    modalZIndex: 9999,                   // Z-index del modal
    backdropZIndex: 1040,                // Z-index del backdrop
    backdropColor: 'rgba(0, 0, 0, 0.5)', // Color del backdrop
    debug: false                         // Logs en consola
};
```

#### **Modo Debug:**

Para activar logs en consola (útil para desarrollo):

```javascript
// En modal-fix.js, cambiar:
debug: true
```

Verás logs como:
```
ℹ️ [ModalFix] Inicializando Modal Fix...
ℹ️ [ModalFix] Encontrados 3 modal(es)
✅ [ModalFix] Modal modalRestore configurado correctamente
✅ [ModalFix] Modal Fix inicializado correctamente
```

#### **Uso:**

No requiere código adicional. Solo incluir en `base.html`:

```html
<script src="{{ url_for('static', filename='js/modal-fix.js') }}"></script>
```

El módulo detecta automáticamente todos los modales con clase `.modal` y les aplica el fix.

#### **Requisitos:**
- Bootstrap 5.3+
- Modales con clase `.modal`

#### **API Global (solo en modo debug):**

```javascript
// Acceder al backdrop
window.ModalFix.backdrop.show();
window.ModalFix.backdrop.hide();

// Limpiar backdrops residuales
window.ModalFix.cleanBootstrapBackdrops();

// Limpiar estilos del body
window.ModalFix.cleanBodyStyles();

// Versión
console.log(window.ModalFix.version); // "1.0.0"
```

---

### **`main.js`** - Funciones Generales del Sistema

Funciones comunes compartidas por toda la aplicación.

---

## 🎨 Buenas Prácticas Implementadas

### **1. DRY (Don't Repeat Yourself)**
- ✅ Una sola implementación del fix
- ✅ Se reutiliza en toda la aplicación
- ✅ Sin código duplicado

### **2. Separation of Concerns**
- ✅ Lógica de modales separada
- ✅ Cada módulo tiene responsabilidad única
- ✅ Fácil de mantener

### **3. Code Documentation**
- ✅ JSDoc comments
- ✅ README explicativo
- ✅ Comentarios inline

### **4. Defensive Programming**
- ✅ Validaciones de existencia
- ✅ Manejo de errores
- ✅ Configuración segura

### **5. Performance**
- ✅ Event listeners eficientes
- ✅ Solo un backdrop en DOM
- ✅ Limpieza de recursos

---

## 📝 Mantenimiento

### **Agregar Nuevo Modal:**

1. Crear modal con clase `.modal`
2. ✅ **¡Listo!** El fix se aplica automáticamente

No se requiere código adicional.

### **Modificar Configuración:**

Editar constante `CONFIG` en `modal-fix.js`:

```javascript
const CONFIG = {
    // ... opciones
};
```

### **Debugging:**

1. Activar `debug: true` en CONFIG
2. Abrir DevTools → Console
3. Ver logs detallados de cada operación

---

## 🐛 Troubleshooting

### **Modal sigue bloqueado:**

1. Verificar que `modal-fix.js` esté cargado:
   ```javascript
   console.log('ModalFix:', window.ModalFix);
   ```

2. Activar modo debug y revisar logs

3. Verificar que el modal tenga clase `.modal`

4. Limpiar caché del navegador (Ctrl+F5)

### **Backdrop no aparece:**

1. Verificar z-index en CONFIG
2. Revisar CSS que pueda estar interfiriendo
3. Verificar que backdrop se haya creado en DOM

### **Conflictos con otros scripts:**

1. Asegurar que `modal-fix.js` se carga DESPUÉS de Bootstrap
2. Verificar orden de scripts en `base.html`
3. Revisar consola por errores

---

## 📊 Changelog

### **v1.0.0** (Oct 2025)
- ✅ Implementación inicial
- ✅ Soporte para todos los modales Bootstrap
- ✅ Backdrop personalizado
- ✅ Modo debug
- ✅ Documentación completa

---

## 👨‍💻 Autor

Sistema de Gestión de Laboratorios - Centro Minero SENA

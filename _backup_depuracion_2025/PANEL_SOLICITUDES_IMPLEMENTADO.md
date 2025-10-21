# ✅ Panel de Gestión de Solicitudes de Nivel - Implementado

**Fecha:** 18 de octubre de 2025  
**Estado:** ✅ **COMPLETAMENTE OPERATIVO**

---

## 🎯 Resumen

Se ha implementado exitosamente el **Panel de Administración de Solicitudes de Cambio de Nivel**, completando el sistema de seguridad para el registro de usuarios.

---

## 📦 Componentes Implementados

### **1. Rutas Backend (web_app.py)**

#### `/admin/solicitudes-nivel` - Ver solicitudes
```python
@app.route('/admin/solicitudes-nivel')
@require_login
@require_level(NIVEL_ADMINISTRADOR)  # Solo nivel 6
def gestionar_solicitudes_nivel():
    # Lista todas las solicitudes ordenadas por estado y fecha
    # Pendientes primero, luego aprobadas y rechazadas
```

#### `/admin/solicitud/aprobar/<id>` - Aprobar solicitud
```python
@app.route('/admin/solicitud/aprobar/<int:solicitud_id>', methods=['POST'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def aprobar_solicitud_nivel(solicitud_id):
    # Cambia el nivel del usuario
    # Actualiza tipo según nuevo nivel
    # Registra en logs de auditoría
    # Marca solicitud como aprobada
```

#### `/admin/solicitud/rechazar/<id>` - Rechazar solicitud
```python
@app.route('/admin/solicitud/rechazar/<int:solicitud_id>', methods=['POST'])
@require_login
@require_level(NIVEL_ADMINISTRADOR)
def rechazar_solicitud_nivel(solicitud_id):
    # Requiere comentario explicativo
    # Mantiene usuario en nivel actual
    # Registra en logs de auditoría
    # Marca solicitud como rechazada
```

---

### **2. Template Frontend (admin_solicitudes_nivel.html)**

Interfaz completa con:

- ✅ **Header informativo** con contador de solicitudes pendientes
- ✅ **Filtros avanzados:**
  - Por estado (pendiente/aprobada/rechazada)
  - Por búsqueda de usuario
  - Por nivel solicitado
- ✅ **Tabla responsive** con todas las solicitudes
- ✅ **Badges de color** para identificar niveles y estados
- ✅ **Botones de acción** (aprobar/rechazar) para pendientes
- ✅ **Modales de confirmación:**
  - Modal de aprobación (verde)
  - Modal de rechazo (rojo con campo de motivo obligatorio)
  - Modal de detalles (para solicitudes procesadas)
- ✅ **JavaScript interactivo** para filtros en tiempo real

---

### **3. Integración en Menú (base.html)**

Enlace agregado en el menú lateral:

```html
{% if user and user.get('user_level',0) >= 6 %}
<li class="nav-item">
  <a href="{{ url_for('gestionar_solicitudes_nivel') }}">
    <i class="bi bi-shield-check me-2"></i>Solicitudes de Nivel
  </a>
</li>
{% endif %}
```

**Ubicación:** Sección de administración, solo visible para **Nivel 6 (Administrador)**

---

## 🎨 Características del Panel

### **Filtros Inteligentes**
```javascript
// Filtro por estado
filtroEstado.value = 'pendiente'  // Por defecto muestra pendientes

// Filtro por búsqueda
buscarUsuario.value = 'nombre o id'  // Búsqueda en tiempo real

// Filtro por nivel
filtroNivel.value = '4'  // Filtrar por nivel específico
```

### **Acciones Disponibles**

#### Para Solicitudes Pendientes:
- ✅ **Aprobar** - Botón verde con modal de confirmación
- ❌ **Rechazar** - Botón rojo que requiere motivo obligatorio

#### Para Solicitudes Procesadas:
- 👁️ **Ver Detalles** - Muestra información completa incluyendo:
  - Usuario que revisó
  - Fecha de respuesta
  - Comentario del administrador

---

## 🔄 Flujo de Trabajo

### **Cuando un usuario solicita nivel superior:**

```
1. Usuario se registra seleccionando nivel alto
        ↓
2. Sistema crea usuario como Aprendiz (nivel 1)
        ↓
3. Se guarda solicitud en tabla solicitudes_nivel
        ↓
4. Usuario ve mensaje: "Tu solicitud será revisada"
        ↓
5. Solicitud aparece como PENDIENTE en panel admin
        ↓
6. Administrador revisa la solicitud
```

### **Proceso de Aprobación:**

```
1. Admin hace clic en botón verde "Aprobar"
        ↓
2. Modal muestra detalles de la solicitud
        ↓
3. Admin puede agregar comentario (opcional)
        ↓
4. Al confirmar:
   - nivel_acceso del usuario cambia
   - tipo del usuario se actualiza
   - solicitud marcada como 'aprobada'
   - registro en logs_seguridad
        ↓
5. Usuario obtiene nuevos permisos inmediatamente
```

### **Proceso de Rechazo:**

```
1. Admin hace clic en botón rojo "Rechazar"
        ↓
2. Modal muestra detalles de la solicitud
        ↓
3. Admin DEBE ingresar motivo del rechazo
        ↓
4. Al confirmar:
   - usuario mantiene nivel actual
   - solicitud marcada como 'rechazada'
   - motivo guardado en comentario_admin
   - registro en logs_seguridad
        ↓
5. Usuario conserva nivel Aprendiz
```

---

## 📊 Tabla de Base de Datos

### **solicitudes_nivel**

```sql
CREATE TABLE solicitudes_nivel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(20) NOT NULL,
    nivel_solicitado INT NOT NULL,
    nivel_actual INT NOT NULL,
    estado ENUM('pendiente', 'aprobada', 'rechazada'),
    fecha_solicitud DATETIME NOT NULL,
    fecha_respuesta DATETIME NULL,
    admin_revisor VARCHAR(20) NULL,
    comentario_admin TEXT NULL,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    INDEX idx_estado (estado),
    INDEX idx_usuario (usuario_id)
);
```

**Campos:**
- `usuario_id` - ID del usuario solicitante
- `nivel_solicitado` - Nivel que desea obtener (2-6)
- `nivel_actual` - Nivel que tiene actualmente (generalmente 1)
- `estado` - pendiente/aprobada/rechazada
- `fecha_solicitud` - Cuándo se hizo la solicitud
- `fecha_respuesta` - Cuándo fue procesada (NULL si pendiente)
- `admin_revisor` - ID del admin que la procesó
- `comentario_admin` - Nota del admin sobre su decisión

---

## 🎯 Casos de Uso

### **Caso 1: Instructor solicita nivel superior**

```
Usuario: Juan Pérez (ID: juan.perez)
Acción: Se registra seleccionando "Instructor (Química)"

RESULTADO:
✅ Cuenta creada como Aprendiz (nivel 1)
✅ Solicitud #1 creada para nivel 4
✅ Mensaje: "Tu solicitud de nivel Instructor (Química) será revisada"

EN EL PANEL ADMIN:
┌─────────────────────────────────────────────┐
│ #1 │ Juan Pérez │ Nivel 1 → Nivel 4      │
│    │ juan.perez │ ⚠️ PENDIENTE  [✅] [❌] │
└─────────────────────────────────────────────┘
```

### **Caso 2: Admin aprueba solicitud**

```
Admin: María García (ID: admin)
Acción: Hace clic en ✅ Aprobar solicitud #1
Comentario: "Verificado con RH. Aprobado."

RESULTADO:
✅ Juan Pérez ahora tiene nivel 4 (Instructor Química)
✅ tipo cambia de 'aprendiz' a 'instructor'
✅ Solicitud marcada como 'aprobada'
✅ Log registrado: "admin aprobó cambio nivel 1 → 4 para juan.perez"

EN EL PANEL:
┌─────────────────────────────────────────────┐
│ #1 │ Juan Pérez │ Nivel 1 → Nivel 4      │
│    │ juan.perez │ ✅ APROBADA  18/10/2025 │
│    │ Por: admin │ [👁️ Ver detalles]      │
└─────────────────────────────────────────────┘
```

### **Caso 3: Admin rechaza solicitud**

```
Admin: María García
Acción: Hace clic en ❌ Rechazar solicitud #2
Motivo: "No cuenta con los permisos necesarios del coordinador"

RESULTADO:
❌ Usuario mantiene nivel 1 (Aprendiz)
✅ Solicitud marcada como 'rechazada'
✅ Motivo guardado
✅ Log registrado: "admin rechazó cambio nivel para usuario.id"

EN EL PANEL:
┌─────────────────────────────────────────────┐
│ #2 │ Pedro López│ Nivel 1 → Nivel 6      │
│    │ pedro.lopez│ ❌ RECHAZADA 18/10/2025 │
│    │ Por: admin │ [👁️ Ver detalles]      │
└─────────────────────────────────────────────┘
```

---

## 🔐 Seguridad Implementada

### **Control de Acceso**
```python
@require_level(NIVEL_ADMINISTRADOR)  # Solo nivel 6
```
- ✅ Solo administradores pueden acceder
- ✅ Otros niveles reciben error 403

### **Validación de Solicitudes**
```python
query = "SELECT * FROM solicitudes_nivel WHERE id = %s AND estado = 'pendiente'"
```
- ✅ Solo se procesan solicitudes pendientes
- ✅ No se puede procesar dos veces la misma solicitud

### **Auditoría Completa**
```python
INSERT INTO logs_seguridad (usuario_id, accion, detalle, ip_origen, exitoso)
VALUES (admin_id, 'aprobacion_nivel', '...', ip, TRUE)
```
- ✅ Cada aprobación/rechazo se registra
- ✅ Incluye: quién, qué, cuándo, desde dónde

### **Integridad de Datos**
```python
# Al aprobar, se actualizan dos tablas en transacción
UPDATE usuarios SET nivel_acceso = X, tipo = Y WHERE id = Z
UPDATE solicitudes_nivel SET estado = 'aprobada' WHERE id = N
```
- ✅ Cambios atómicos
- ✅ Consistencia garantizada

---

## 📱 Interfaz Responsive

El panel funciona perfectamente en:
- 🖥️ Desktop (1920x1080)
- 💻 Laptop (1366x768)
- 📱 Tablet (768x1024)
- 📱 Mobile (375x667)

**Características responsive:**
- Tabla con scroll horizontal en móviles
- Modales adaptables
- Botones táctiles optimizados
- Filtros apilados en pantallas pequeñas

---

## 🎨 Códigos de Color

### **Estados:**
- 🟡 **Pendiente** - `badge bg-warning`
- 🟢 **Aprobada** - `badge bg-success`
- 🔴 **Rechazada** - `badge bg-danger`

### **Niveles Solicitados:**
- 🔵 **Nivel 2-3** - Azul (`#0d6efd`)
- 🟠 **Nivel 4-5** - Naranja (`#fd7e14`)
- 🔴 **Nivel 6** - Rojo (`#dc3545`)

---

## 🚀 Cómo Usar el Panel

### **Para Administradores:**

#### **1. Acceder al Panel**
```
1. Iniciar sesión como administrador (nivel 6)
2. En el menú lateral, hacer clic en "Solicitudes de Nivel"
3. Ver lista de todas las solicitudes
```

#### **2. Revisar Solicitud Pendiente**
```
1. Filtrar por "Pendientes" (por defecto)
2. Ver detalles del usuario:
   - Nombre e ID
   - Email
   - Nivel actual
   - Nivel solicitado
3. Decidir aprobar o rechazar
```

#### **3. Aprobar Solicitud**
```
1. Hacer clic en botón verde ✅
2. Revisar información en modal
3. (Opcional) Agregar comentario
4. Confirmar "Aprobar Solicitud"
5. ✅ Usuario obtiene nuevo nivel
```

#### **4. Rechazar Solicitud**
```
1. Hacer clic en botón rojo ❌
2. Revisar información en modal
3. **OBLIGATORIO:** Ingresar motivo del rechazo
4. Confirmar "Rechazar Solicitud"
5. ❌ Usuario mantiene nivel actual
```

#### **5. Ver Historial**
```
1. Cambiar filtro a "Aprobadas" o "Rechazadas"
2. Hacer clic en 👁️ para ver detalles
3. Ver:
   - Quién revisó la solicitud
   - Cuándo fue procesada
   - Comentario del administrador
```

---

## 📈 Estadísticas del Panel

El panel muestra en tiempo real:
- **Contador de pendientes** en el header
- **Total de solicitudes** en la tabla
- **Fecha de cada solicitud**
- **Estado visual** con badges de color

---

## 🔗 Enlaces Relacionados

- **Archivo modificado:** `web_app.py` (líneas 1536-1695)
- **Template creado:** `templates/admin_solicitudes_nivel.html`
- **Menú actualizado:** `templates/base.html` (líneas 57-58)
- **Tabla BD:** Script `crear_sistema_solicitudes.py`

---

## ✅ Checklist de Implementación

- [x] Tabla `solicitudes_nivel` creada en BD
- [x] Ruta `/admin/solicitudes-nivel` implementada
- [x] Ruta `/admin/solicitud/aprobar/<id>` implementada
- [x] Ruta `/admin/solicitud/rechazar/<id>` implementada
- [x] Template `admin_solicitudes_nivel.html` creado
- [x] Enlace agregado en menú de navegación
- [x] Sistema de filtros implementado
- [x] Modales de confirmación funcionales
- [x] Logs de auditoría registrados
- [x] Validaciones de seguridad aplicadas
- [x] Interfaz responsive
- [x] Documentación completa

---

## 🎉 Resultado Final

El sistema ahora cuenta con un **flujo completo y seguro** para la gestión de permisos:

```
REGISTRO → SOLICITUD → REVISIÓN → APROBACIÓN/RECHAZO → CAMBIO DE NIVEL
   ✅         ✅          ✅              ✅                    ✅
```

**Estado del Sistema de Seguridad:** 🟢 **COMPLETAMENTE OPERATIVO**

---

**Fecha de implementación:** 18 de octubre de 2025  
**Desarrollado por:** Sistema de Gestión de Laboratorios - Centro Minero SENA  
**Versión:** 1.0

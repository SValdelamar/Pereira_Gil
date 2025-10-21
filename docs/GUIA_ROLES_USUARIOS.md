# 👥 Sistema de Roles y Permisos - Guía Completa

## 📋 Índice
1. [Estructura de Roles](#estructura-de-roles)
2. [Niveles de Acceso](#niveles-de-acceso)
3. [Sistema de Permisos](#sistema-de-permisos)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Campos Específicos por Rol](#campos-específicos-por-rol)

---

## 🎯 Estructura de Roles

El sistema utiliza **6 niveles de acceso jerárquicos**, donde cada nivel tiene permisos específicos:

```
Nivel 6: Administrador                    [Acceso Total]
    ↓
Nivel 5: Instructor a cargo de Inventario [Gestión Completa de su Lab]
    ↓
Nivel 4: Instructor (Química)             [Gestión Avanzada]
    ↓
Nivel 3: Instructor (No Química)          [Gestión Básica]
    ↓
Nivel 2: Funcionario                      [Permisos Limitados]
    ↓
Nivel 1: Aprendiz                         [Solo Lectura]
```

---

## 🔑 Niveles de Acceso Detallados

### **Nivel 1: Aprendiz** 👨‍🎓
**Constante:** `NIVEL_APRENDIZ = 1`

**Perfil:**
- Estudiantes del SENA en formación
- Solo pueden ver información, no modificar

**Permisos:**
- ✅ Ver laboratorios e inventario
- ✅ Ver sus propias reservas
- ✅ Consultar equipos disponibles
- ❌ No puede crear, editar ni eliminar

**Campos requeridos en registro:**
```python
- programa          # Ej: "Técnico en Química"
- ficha            # Número de ficha
```

**Uso en código:**
```python
@require_level(NIVEL_APRENDIZ)  # Nivel mínimo 1
def ver_equipos():
    ...
```

---

### **Nivel 2: Funcionario** 👔
**Constante:** `NIVEL_FUNCIONARIO = 2`

**Perfil:**
- Personal administrativo del centro
- Puede gestionar algunos recursos básicos

**Permisos:**
- ✅ Todo lo de Aprendiz
- ✅ Crear reservas
- ✅ Ver reportes básicos
- ✅ Editar su perfil
- ❌ No puede gestionar usuarios

**Campos requeridos:**
```python
- cargo            # Ej: "Secretario Académico"
- dependencia      # Ej: "Coordinación Académica"
```

**Uso en código:**
```python
@require_level(NIVEL_FUNCIONARIO)  # Nivel mínimo 2
def generar_reporte():
    ...
```

---

### **Nivel 3: Instructor (No Química)** 👨‍🏫
**Constante:** `NIVEL_INSTRUCTOR_NO_QUIMICA = 3`

**Perfil:**
- Instructores de áreas no relacionadas con química
- Pueden gestionar equipos de sus áreas

**Permisos:**
- ✅ Todo lo de Funcionario
- ✅ Crear y editar equipos
- ✅ Gestionar inventario de su área
- ✅ Ver usuarios
- ✅ Aprobar reservas básicas
- ❌ No puede gestionar químicos

**Campos requeridos:**
```python
- programa_formacion    # Ej: "Mecánica Industrial"
- especialidad         # Ej: "Sistemas Hidráulicos"
```

**Uso en código:**
```python
@require_level(NIVEL_INSTRUCTOR_NO_QUIMICA)  # Nivel mínimo 3
def gestionar_equipos():
    ...
```

---

### **Nivel 4: Instructor (Química)** 🧪
**Constante:** `NIVEL_INSTRUCTOR_QUIMICA = 4`

**Perfil:**
- Instructores del área de química
- Acceso a laboratorios químicos y reactivos

**Permisos:**
- ✅ Todo lo de Instructor No Química
- ✅ Gestionar reactivos químicos
- ✅ Gestionar laboratorios de química
- ✅ Acceso a equipos especializados
- ✅ Crear y editar items de inventario químico
- ✅ Entrenar IA visual
- ❌ No puede gestionar backups

**Campos requeridos:**
```python
- especialidad    # Ej: "Química Analítica", "Química Orgánica"
```

**Especialidades de química disponibles:**
```python
ESPECIALIDADES_QUIMICA = [
    'Química Analítica',
    'Química Orgánica',
    'Química Inorgánica',
    'Química Industrial',
    'Análisis Instrumental',
    'Control de Calidad',
    'Química Ambiental'
]
```

**Uso en código:**
```python
@require_level(NIVEL_INSTRUCTOR_QUIMICA)  # Nivel mínimo 4
def gestionar_reactivos():
    ...
```

---

### **Nivel 5: Instructor a cargo de Inventario** 📦
**Constante:** `NIVEL_INSTRUCTOR_INVENTARIO = 5`

**Perfil:**
- Instructor responsable del inventario de un laboratorio específico
- Control total sobre su laboratorio asignado

**Permisos:**
- ✅ Todo lo de Instructor Química
- ✅ Gestión completa de su laboratorio asignado
- ✅ Aprobar/rechazar todas las reservas de su lab
- ✅ Control de entrada/salida de equipos
- ✅ Auditoría de inventario
- ❌ Solo su laboratorio (no otros)

**Campos requeridos:**
```python
- especialidad        # Especialidad química
- a_cargo_inventario = True
- laboratorio_id     # Laboratorio asignado
```

**Verificación especial:**
```python
@require_instructor_inventario
def aprobar_reserva_lab():
    # Solo puede aprobar reservas de su laboratorio
    ...
```

**Uso en código:**
```python
# Verificar si es instructor a cargo
es_instructor, lab_id = permissions_manager.es_instructor_con_inventario(user_id)

if es_instructor:
    # Solo puede gestionar su laboratorio
    if laboratorio_id == lab_id:
        # Permitir acción
```

---

### **Nivel 6: Administrador** 👑
**Constante:** `NIVEL_ADMINISTRADOR = 6`

**Perfil:**
- Administradores del sistema
- Control total sobre todo el sistema

**Permisos:**
- ✅ **ACCESO TOTAL** a todas las funcionalidades
- ✅ Gestionar usuarios (crear, editar, eliminar)
- ✅ Gestionar todos los laboratorios
- ✅ Configuración del sistema
- ✅ Backups y restauración de BD
- ✅ Ver logs de auditoría
- ✅ Acceder a panel de configuración
- ✅ Entrenar IA y gestión de objetos

**Uso en código:**
```python
@require_level(NIVEL_ADMINISTRADOR)  # Solo nivel 6
def panel_administrador():
    ...
```

---

## 🛡️ Sistema de Permisos

### **Arquitectura del Sistema**

El sistema utiliza dos métodos de control de acceso:

#### 1. **Por Nivel** (Jerárquico)
```python
# Requiere un nivel mínimo
@require_level(nivel_minimo)
```

#### 2. **Por Módulo y Acción** (Granular)
```python
# Requiere permiso específico en un módulo
@require_permission(modulo='equipos', accion='crear')
```

### **Tipos de Acciones**

Cada módulo del sistema tiene 4 tipos de acciones:

| Acción | Descripción | Ejemplo |
|--------|-------------|---------|
| `ver` | Solo lectura | Ver lista de equipos |
| `crear` | Crear nuevos registros | Agregar nuevo equipo |
| `editar` | Modificar existentes | Actualizar datos de equipo |
| `eliminar` | Borrar registros | Eliminar equipo del sistema |

### **Módulos del Sistema**

```python
MODULOS = [
    'dashboard',           # Panel principal
    'laboratorios',        # Gestión de laboratorios
    'equipos',            # Gestión de equipos
    'inventario',         # Control de inventario
    'reservas',           # Sistema de reservas
    'usuarios',           # Administración de usuarios
    'reportes',           # Generación de informes
    'backup',             # Backup de BD
    'configuracion',      # Configuración del sistema
    'notificaciones',     # Centro de notificaciones
    'ia_visual',          # IA de reconocimiento
    'registro_facial'     # Reconocimiento facial
]
```

---

## 💻 Ejemplos de Uso en Código

### **Ejemplo 1: Proteger una ruta con nivel mínimo**

```python
from utils.permissions import require_level, NIVEL_INSTRUCTOR_QUIMICA

@app.route('/laboratorio-quimica')
@require_login
@require_level(NIVEL_INSTRUCTOR_QUIMICA)  # Solo nivel 4 o superior
def laboratorio_quimica():
    return render_template('laboratorio_quimica.html')
```

### **Ejemplo 2: Proteger con permiso específico**

```python
from utils.permissions import require_permission

@app.route('/usuarios')
@require_login
@require_permission('usuarios', 'ver')  # Necesita permiso de ver usuarios
def listar_usuarios():
    return render_template('usuarios.html')
```

### **Ejemplo 3: API con verificación de permisos**

```python
from utils.permissions import api_require_permission

@app.route('/api/equipos', methods=['POST'])
@api_require_permission('equipos', 'crear')  # Retorna JSON con error
def crear_equipo_api():
    # Solo si tiene permiso de crear equipos
    return jsonify({'success': True})
```

### **Ejemplo 4: Verificar en plantilla Jinja2**

```html
{% if tiene_permiso('equipos', 'crear') %}
    <button>Agregar Equipo</button>
{% endif %}

{% if user.user_level >= 4 %}
    <a href="/laboratorio-quimica">Laboratorio Química</a>
{% endif %}
```

### **Ejemplo 5: Lógica condicional por rol**

```python
# En web_app.py
if session.get('user_level', 0) >= NIVEL_ADMINISTRADOR:
    # Mostrar todas las opciones
    laboratorios = obtener_todos_laboratorios()
elif session.get('user_level', 0) == NIVEL_INSTRUCTOR_INVENTARIO:
    # Solo su laboratorio
    es_instructor, lab_id = permissions_manager.es_instructor_con_inventario(user_id)
    if es_instructor:
        laboratorios = obtener_laboratorio(lab_id)
else:
    # Solo lectura
    laboratorios = obtener_laboratorios_activos()
```

### **Ejemplo 6: Instructor a cargo de inventario**

```python
from utils.permissions import require_instructor_inventario

@app.route('/aprobar-reserva/<int:reserva_id>')
@require_login
@require_instructor_inventario
def aprobar_reserva(reserva_id, laboratorio_asignado=None):
    # laboratorio_asignado se pasa automáticamente por el decorador
    reserva = obtener_reserva(reserva_id)
    
    # Verificar que la reserva es de su laboratorio
    if reserva.laboratorio_id != laboratorio_asignado:
        flash('Solo puedes aprobar reservas de tu laboratorio', 'error')
        return redirect(url_for('reservas'))
    
    # Aprobar reserva
    aprobar_reserva_db(reserva_id)
    return redirect(url_for('reservas'))
```

---

## 📝 Campos Específicos por Rol

### **Tabla usuarios - Estructura**

```sql
CREATE TABLE usuarios (
    id VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255),
    tipo VARCHAR(50),
    nivel_acceso INT,              -- 1 a 6
    
    -- Campos de Aprendiz (nivel 1)
    programa VARCHAR(100),          
    ficha VARCHAR(20),
    
    -- Campos de Funcionario (nivel 2)
    cargo VARCHAR(100),
    dependencia VARCHAR(100),
    
    -- Campos de Instructor (nivel 3-5)
    programa_formacion VARCHAR(100),
    especialidad VARCHAR(100),
    
    -- Campos de Instructor Inventario (nivel 5)
    a_cargo_inventario BOOLEAN,
    laboratorio_id INT,
    
    foto_frontal TEXT,
    foto_perfil TEXT,
    estado VARCHAR(20),
    fecha_registro DATETIME
);
```

### **Validación de Campos**

```python
from utils.permissions import validar_campos_requeridos

# En registro de usuario
es_valido, mensaje = validar_campos_requeridos(nivel, datos)

if not es_valido:
    flash(mensaje, 'error')
    return redirect(url_for('registro'))
```

---

## 🔄 Flujo de Autenticación

```
1. Usuario ingresa credenciales
        ↓
2. Sistema verifica en BD
        ↓
3. Si es válido:
   - Se obtiene nivel_acceso
   - Se carga en session
   - Se generan permisos
        ↓
4. Usuario accede al sistema
        ↓
5. Cada ruta verifica:
   - @require_login (sesión activa)
   - @require_level (nivel suficiente)
   - @require_permission (permiso específico)
        ↓
6. Si pasa todas las validaciones:
   ✅ Acceso permitido
   
   Si falla alguna:
   ❌ Redirige a dashboard o login
```

---

## 📊 Matriz de Permisos (Referencia Rápida)

| Módulo | Nivel 1 | Nivel 2 | Nivel 3 | Nivel 4 | Nivel 5 | Nivel 6 |
|--------|---------|---------|---------|---------|---------|---------|
| **Dashboard** | Ver | Ver | Ver | Ver | Ver | Ver |
| **Laboratorios** | Ver | Ver | Ver | Ver | Gestionar (su lab) | Gestionar todo |
| **Equipos** | Ver | Ver | CRUD básico | CRUD completo | CRUD (su lab) | CRUD todo |
| **Inventario** | Ver | Ver | Editar | CRUD | CRUD (su lab) | CRUD todo |
| **Reservas** | Ver propias | Crear | Aprobar básicas | Aprobar | Aprobar (su lab) | Aprobar todas |
| **Usuarios** | ❌ | ❌ | Ver | Ver | Ver | CRUD |
| **Reportes** | ❌ | Ver básicos | Generar | Generar | Generar | Generar todos |
| **Backup** | ❌ | ❌ | ❌ | ❌ | ❌ | CRUD |
| **Configuración** | ❌ | ❌ | ❌ | ❌ | ❌ | CRUD |
| **IA Visual** | ❌ | ❌ | ❌ | Entrenar | Entrenar | Entrenar |

**Leyenda:**
- ✅ Ver = Solo lectura
- CRUD = Crear, Ver, Editar, Eliminar
- ❌ = Sin acceso

---

## 🎓 Casos de Uso Prácticos

### **Caso 1: Aprendiz consulta equipos**
```python
# Usuario nivel 1
- Puede ver lista de equipos ✅
- NO puede agregar equipo nuevo ❌
- NO puede editar equipo ❌
- NO puede eliminar equipo ❌
```

### **Caso 2: Instructor de Química registra reactivo**
```python
# Usuario nivel 4
- Puede ver reactivos ✅
- Puede agregar nuevo reactivo ✅
- Puede editar reactivo ✅
- Puede eliminar reactivo (si no está en uso) ✅
- NO puede hacer backup de BD ❌
```

### **Caso 3: Instructor a cargo aprueba reserva**
```python
# Usuario nivel 5, asignado a Laboratorio 3
- Puede ver todas las reservas del Lab 3 ✅
- Puede aprobar reservas del Lab 3 ✅
- NO puede aprobar reservas del Lab 1 ❌
- NO puede gestionar inventario del Lab 1 ❌
```

### **Caso 4: Administrador gestiona todo**
```python
# Usuario nivel 6
- Acceso completo a TODO ✅
- Puede crear/editar/eliminar usuarios ✅
- Puede hacer backup de BD ✅
- Puede cambiar configuración del sistema ✅
- Puede acceder a todos los laboratorios ✅
```

---

## 🔐 Seguridad

### **Protecciones Implementadas**

1. **Autenticación obligatoria**
   ```python
   @require_login  # Toda ruta protegida
   ```

2. **Verificación de nivel**
   ```python
   if nivel < nivel_minimo:
       return redirect('dashboard')
   ```

3. **Tokens JWT para API**
   ```python
   token = create_access_token(identity=user_id)
   ```

4. **Permisos granulares**
   ```python
   if not puede_acceder(user_id, 'modulo', 'accion'):
       return error_403
   ```

5. **Logs de auditoría**
   ```sql
   INSERT INTO logs_seguridad (user_id, accion, timestamp)
   ```

---

## 📚 Referencia de Constantes

```python
# En utils/permissions.py

NIVEL_APRENDIZ = 1
NIVEL_FUNCIONARIO = 2
NIVEL_INSTRUCTOR_NO_QUIMICA = 3
NIVEL_INSTRUCTOR_QUIMICA = 4
NIVEL_INSTRUCTOR_INVENTARIO = 5
NIVEL_ADMINISTRADOR = 6

ROLES_NOMBRES = {
    1: 'Aprendiz',
    2: 'Funcionario',
    3: 'Instructor (No Química)',
    4: 'Instructor (Química)',
    5: 'Instructor a cargo de Inventario',
    6: 'Administrador'
}
```

---

**Fecha de actualización:** 18 de octubre de 2025  
**Sistema:** Centro Minero SENA - Gestión de Laboratorios  
**Versión:** 1.0

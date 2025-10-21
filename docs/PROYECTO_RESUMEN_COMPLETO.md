# 📋 Proyecto: Sistema de Gestión de Laboratorios
## Centro Minero SENA - Sogamoso, Boyacá

---

## 📖 Índice

1. [Descripción General](#-descripción-general)
2. [Objetivos del Proyecto](#-objetivos-del-proyecto)
3. [Alcance y Funcionalidades](#-alcance-y-funcionalidades)
4. [Arquitectura del Sistema](#-arquitectura-del-sistema)
5. [Módulos Implementados](#-módulos-implementados)
6. [Stack Tecnológico](#-stack-tecnológico)
7. [Sistema de Seguridad](#-sistema-de-seguridad)
8. [Base de Datos](#-base-de-datos)
9. [Diseño y Experiencia de Usuario](#-diseño-y-experiencia-de-usuario)
10. [Configuración y Despliegue](#-configuración-y-despliegue)
11. [Mantenimiento y Soporte](#-mantenimiento-y-soporte)

---

## 🎯 Descripción General

El **Sistema de Gestión de Laboratorios** es una aplicación web completa diseñada específicamente para el Centro Minero SENA de Sogamoso, Boyacá. El sistema centraliza y automatiza la gestión integral de espacios educativos, equipos, inventario, reservas y usuarios.

### **Problema que Resuelve**

Antes de la implementación de este sistema, el Centro Minero enfrentaba:
- ❌ Gestión manual de reservas de equipos y espacios
- ❌ Falta de control centralizado del inventario
- ❌ Dificultad para generar reportes y estadísticas
- ❌ Procesos lentos para aprobación de solicitudes
- ❌ No había trazabilidad de movimientos de equipos
- ❌ Sistema de permisos inexistente o básico

### **Solución Propuesta**

✅ **Digitalización completa** de procesos administrativos  
✅ **Automatización** de aprobaciones y notificaciones  
✅ **Centralización** de información en una sola plataforma  
✅ **Trazabilidad** completa de todas las operaciones  
✅ **Seguridad** multinivel con roles y permisos  
✅ **Inteligencia Artificial** para reconocimiento facial (opcional)  

---

## 🎯 Objetivos del Proyecto

### **Objetivos Principales**

1. **Optimizar la gestión de recursos educativos**
   - Centralizar información de laboratorios, aulas y talleres
   - Facilitar el control de equipos y su estado
   - Automatizar el proceso de reservas

2. **Mejorar la eficiencia administrativa**
   - Reducir tiempo de procesamiento de solicitudes
   - Automatizar generación de reportes
   - Facilitar auditorías y seguimiento

3. **Garantizar la seguridad y trazabilidad**
   - Sistema de permisos multinivel
   - Registro completo de operaciones
   - Autenticación segura con JWT

4. **Modernizar la experiencia del usuario**
   - Interfaz intuitiva y moderna
   - Diseño responsive para cualquier dispositivo
   - Reconocimiento facial opcional para login

### **Objetivos Específicos**

- ✅ Reducir en 70% el tiempo de gestión manual de reservas
- ✅ Eliminar 100% de errores en inventario por control manual
- ✅ Generar reportes automáticos en menos de 5 segundos
- ✅ Permitir acceso remoto desde cualquier dispositivo
- ✅ Implementar backups automáticos diarios
- ✅ Integrar reconocimiento facial con 95%+ de precisión

---

## 🎯 Alcance y Funcionalidades

### **Módulos Implementados**

#### **1. Dashboard Principal** 📊
- Estadísticas en tiempo real
- Gráficos interactivos de uso
- Indicadores clave (KPIs)
- Alertas y notificaciones
- Vista general del sistema

#### **2. Gestión de Espacios** 🏢
- Registro de laboratorios, aulas y talleres
- Galería de imágenes por espacio
- Capacidad y características
- Estado de disponibilidad
- Historial de uso

#### **3. Control de Equipos** 🔧
- Inventario completo de equipos
- Estados: Disponible, En uso, Mantenimiento, Dañado
- Asignación a espacios
- Historial de mantenimiento
- Alertas de revisión

#### **4. Inventario Inteligente** 📦
- Control de consumibles y materiales
- Alertas de stock mínimo
- Proyección de consumo
- Historial de movimientos
- Reportes de consumo

#### **5. Sistema de Reservas** 📅
- Solicitud de equipos/espacios
- Calendario de disponibilidad
- Aprobación multinivel
- Notificaciones automáticas
- Historial de reservas

#### **6. Gestión de Usuarios** 👥
- Registro y perfiles completos
- 6 niveles de permisos
- Asignación de roles
- Reconocimiento facial opcional
- Recuperación de contraseña

#### **7. Reportes Profesionales** 📄
- Exportación a PDF con diseño SENA
- Exportación a Excel
- Gráficos estadísticos
- Reportes personalizables
- Programación de reportes

#### **8. Backup y Restauración** 💾
- Backups automáticos programables
- Compresión de archivos
- Restauración con confirmación
- Historial de backups
- Descarga de respaldos

#### **9. Sistema de Ayuda** ❓
- Tutoriales interactivos
- Guías paso a paso
- FAQs por módulo
- Contacto integrado
- Documentación completa

#### **10. Registro de Actividades** 📝
- Auditoría completa del sistema
- Tracking de todas las operaciones
- Filtros avanzados
- Exportación de logs
- Análisis de uso

---

## 🏗️ Arquitectura del Sistema

### **Patrón Arquitectónico: MVC (Model-View-Controller)**

```
┌─────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN              │
│    (Templates HTML + CSS + JavaScript)      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          CAPA DE CONTROLADOR                │
│         (Flask Routes & Logic)              │
│  - web_app.py (Router principal)            │
│  - app/utils/ (Lógica de negocio)           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           CAPA DE MODELO                    │
│       (Database Operations)                 │
│  - MySQL Queries                            │
│  - Data Validation                          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          BASE DE DATOS MySQL                │
│  - Usuarios, Espacios, Equipos              │
│  - Inventario, Reservas, Logs               │
└─────────────────────────────────────────────┘
```

### **Estructura de Directorios**

```
Sistema_Laboratorio-v2/
│
├── app/                              # Aplicación principal
│   ├── utils/                        # Utilidades y helpers
│   │   ├── permisos.py              # Sistema de permisos
│   │   ├── reportes.py              # Generación de reportes
│   │   ├── notificaciones.py        # Sistema de notificaciones
│   │   ├── backup.py                # Gestión de backups
│   │   └── facial_recognition.py   # IA reconocimiento facial
│   │
│   ├── static/                       # Archivos estáticos
│   │   ├── css/                     # Hojas de estilo
│   │   │   ├── common.css           # Estilos base
│   │   │   ├── auth.css             # Autenticación
│   │   │   ├── dashboard.css        # Dashboard
│   │   │   └── modules.css          # Módulos
│   │   ├── js/                      # JavaScript
│   │   ├── img/                     # Imágenes
│   │   └── uploads/                 # Uploads usuarios
│   │
│   └── templates/                    # Templates HTML
│       ├── base.html                # Template base
│       ├── auth/                    # Autenticación
│       │   ├── login.html
│       │   ├── registro_completo.html
│       │   └── recuperar_contrasena.html
│       ├── dashboard/               # Dashboard
│       │   └── index.html
│       └── modules/                 # Módulos funcionales
│           ├── espacios.html
│           ├── equipos.html
│           ├── inventario.html
│           ├── reservas.html
│           ├── usuarios.html
│           ├── reportes.html
│           ├── backup.html
│           ├── ayuda.html
│           └── registros_gestion.html
│
├── docs/                             # Documentación
│   ├── PROYECTO_RESUMEN_COMPLETO.md
│   ├── GUIA_ROLES_USUARIOS.md
│   └── reportes/
│
├── scripts/                          # Scripts de utilidad
│   ├── setup_database.py            # Inicializar BD
│   └── seed_data.py                 # Datos de prueba
│
├── backups/                          # Backups automáticos
│
├── web_app.py                        # 🚀 Punto de entrada
├── requirements.txt                  # Dependencias Python
├── .env.example                      # Variables de entorno
├── .gitignore                        # Git ignore
└── README.md                         # Documentación principal
```

---

## 🛠️ Stack Tecnológico

### **Backend - Python**

#### **Framework Principal**
- **Flask 3.1.1** - Microframework web ligero y flexible
- **Werkzeug 3.1.3** - Librería WSGI para Flask

#### **Base de Datos**
- **MySQL 8.0+** - Sistema de gestión de base de datos relacional
- **mysql-connector-python 9.4.0** - Conector oficial MySQL

#### **Autenticación y Seguridad**
- **Flask-JWT-Extended 4.7.1** - JSON Web Tokens
- **bcrypt** - Hash de contraseñas seguro
- **python-decouple 3.8** - Gestión de variables de entorno

#### **APIs y Comunicación**
- **Flask-RESTful 0.3.10** - Extensión para crear APIs REST
- **Flask-CORS 6.0.1** - Cross-Origin Resource Sharing
- **requests 2.32.5** - Cliente HTTP

---

### **Inteligencia Artificial**

#### **Visión Computacional**
- **OpenCV 4.12.0.88** - Librería de visión por computadora
- **face_recognition** - Reconocimiento facial basado en dlib
- **dlib** - Machine learning y reconocimiento facial

#### **Procesamiento de Datos**
- **NumPy 2.2.6** - Computación científica y arrays
- **Pillow 11.3.0** - Procesamiento de imágenes

---

### **Reportes y Exportación**

#### **PDF**
- **ReportLab 4.2.5** - Generación de PDFs profesionales
- Diseño personalizado con logo SENA
- Gráficos y tablas

#### **Excel**
- **openpyxl 3.1.5** - Lectura y escritura de archivos Excel
- **xlsxwriter 3.2.0** - Creación de Excel con formato avanzado

---

### **Frontend**

#### **Framework CSS**
- **Bootstrap 5.3** - Framework CSS responsive
- **Bootstrap Icons 1.11** - Librería de iconos

#### **CSS Personalizado**
- Variables CSS para temas
- Animaciones CSS3
- Gradientes y sombras
- Efectos hover profesionales

#### **JavaScript**
- **Vanilla JavaScript** - Sin frameworks pesados
- **AJAX** - Para comunicación asíncrona
- **DOM Manipulation** - Interactividad dinámica

---

### **Utilidades del Sistema**

#### **Audio**
- **pyttsx3 2.90** - Text-to-speech (síntesis de voz)
- **SpeechRecognition 3.10** - Reconocimiento de voz
- **pywin32 311** - Interacción con Windows

#### **Fechas y Tiempo**
- **python-dateutil 2.9.0** - Manipulación avanzada de fechas
- **pytz 2025.2** - Zonas horarias

#### **Sistema y Monitoreo**
- **psutil 7.1.0** - Información del sistema
- **python-dotenv 1.0.0** - Variables de entorno

#### **Generación de Datos**
- **Faker 34.0.0** - Datos de prueba realistas

---

## 🔐 Sistema de Seguridad

### **Niveles de Usuario y Permisos**

El sistema implementa **6 niveles jerárquicos** de permisos:

#### **Nivel 1: Aprendiz** 👨‍🎓
**Permisos:**
- ✅ Ver dashboard (vista limitada)
- ✅ Ver espacios disponibles
- ✅ Solicitar reservas de equipos
- ✅ Ver su perfil
- ❌ No puede aprobar ni modificar

**Casos de uso:**
- Estudiantes del SENA
- Aprendices en formación

---

#### **Nivel 2: Funcionario** 👔
**Permisos:**
- ✅ Todo lo de Nivel 1, más:
- ✅ Ver inventario completo
- ✅ Ver todas las reservas
- ✅ Consultas avanzadas
- ❌ No puede modificar

**Casos de uso:**
- Personal administrativo
- Secretarias
- Personal de apoyo

---

#### **Nivel 3-4: Instructor** 👨‍🏫
**Permisos:**
- ✅ Todo lo de Nivel 2, más:
- ✅ Gestionar sus espacios asignados
- ✅ Modificar equipos de su área
- ✅ Aprobar reservas de su área
- ✅ Generar reportes de su área
- ❌ No puede gestionar inventario general

**Casos de uso:**
- Instructores SENA
- Coordinadores de área
- Docentes especializados

---

#### **Nivel 5: Instructor Inventario** 📋
**Permisos:**
- ✅ Todo lo de Nivel 3-4, más:
- ✅ Gestión completa de inventario
- ✅ Aprobar/rechazar todas las reservas
- ✅ Gestión de consumibles
- ✅ Alertas de stock
- ✅ Reportes globales
- ❌ No puede gestionar usuarios

**Casos de uso:**
- Coordinador de laboratorios
- Responsable de inventario
- Administrador de recursos

---

#### **Nivel 6: Administrador** 👑
**Permisos:**
- ✅ **CONTROL TOTAL DEL SISTEMA**
- ✅ Gestión de usuarios
- ✅ Asignación de permisos
- ✅ Backups y restauración
- ✅ Configuración del sistema
- ✅ Acceso a todos los módulos
- ✅ Auditoría completa

**Casos de uso:**
- Director del Centro
- Administrador TI
- Personal autorizado

---

### **Seguridad Implementada**

#### **Autenticación**
```python
- JWT (JSON Web Tokens) con expiración
- Tokens de refresh
- Hash bcrypt para contraseñas
- Recuperación segura por email
- Reconocimiento facial opcional (2FA)
```

#### **Autorización**
```python
- Decoradores de permisos @requiere_nivel()
- Validación en cada endpoint
- Control a nivel de base de datos
- Logs de intentos no autorizados
```

#### **Protección de Datos**
```python
- Variables sensibles en .env
- Contraseñas nunca en texto plano
- SQL injection prevention
- XSS protection
- CSRF tokens
```

#### **Auditoría**
```python
- Registro completo de operaciones
- Timestamp de cada acción
- IP y usuario registrados
- Trazabilidad completa
- Exportación de logs
```

---

## 💾 Base de Datos

### **Diagrama Entidad-Relación (Simplificado)**

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Usuarios   │──────│  Reservas    │──────│  Equipos    │
│             │      │              │      │             │
│ - id        │      │ - id         │      │ - id        │
│ - nombre    │      │ - usuario_id │      │ - nombre    │
│ - email     │      │ - equipo_id  │      │ - estado    │
│ - nivel     │      │ - estado     │      │ - espacio_id│
│ - password  │      │ - fecha      │      │ - tipo      │
└─────────────┘      └──────────────┘      └─────────────┘
       │                                           │
       │                                           │
       │             ┌──────────────┐              │
       └─────────────│  Espacios    │──────────────┘
                     │              │
                     │ - id         │
                     │ - nombre     │
                     │ - tipo       │
                     │ - capacidad  │
                     └──────────────┘
```

### **Tablas Principales**

1. **usuarios** - Información de usuarios del sistema
2. **espacios** - Laboratorios, aulas y talleres
3. **equipos** - Inventario de equipos y herramientas
4. **inventario** - Consumibles y materiales
5. **reservas** - Solicitudes y aprobaciones
6. **logs** - Registro de actividades
7. **backups_registro** - Historial de backups
8. **notificaciones** - Sistema de alertas

---

## 🎨 Diseño y Experiencia de Usuario

### **Paleta de Colores SENA**

```css
--color-sena-primary: #2D6A4F;      /* Verde SENA principal */
--color-sena-light: #52B788;        /* Verde claro */
--color-sena-dark: #1B4332;         /* Verde oscuro */
--color-sena-accent: #74C69D;       /* Acento verde */
```

### **Principios de Diseño**

#### **1. Consistencia Visual**
- Mismo estilo en todos los módulos
- Componentes reutilizables
- Tipografía uniforme
- Espaciado coherente

#### **2. Accesibilidad**
- Contraste de colores adecuado
- Texto legible (mínimo 16px)
- Iconos descriptivos
- Navegación por teclado

#### **3. Responsive Design**
- Mobile-first approach
- Breakpoints: 768px, 992px, 1200px
- Imágenes adaptativas
- Menú hamburguesa en móvil

#### **4. Interactividad**
- Feedback visual inmediato
- Animaciones suaves (0.3s)
- Estados hover claramente definidos
- Transiciones CSS3

### **Componentes UI Principales**

#### **Tarjetas (Cards)**
```css
- Border radius: 16px
- Box shadow suave
- Hover effect con elevación
- Gradientes sutiles
```

#### **Botones**
```css
- Primarios: Verde SENA con gradiente
- Secundarios: Gris neutro
- Destructivos: Rojo para eliminar
- Estados: hover, active, disabled
```

#### **Modales**
```css
- Backdrop oscuro (85% opacidad)
- Animación fade in
- Z-index: 9999
- Botones bien posicionados
```

#### **Formularios**
```css
- Labels flotantes
- Validación en tiempo real
- Mensajes de error claros
- Iconos en inputs
```

---

## ⚙️ Configuración y Despliegue

### **Requisitos del Sistema**

#### **Hardware Mínimo**
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4 GB (8 GB recomendado)
- **Disco:** 2 GB libres
- **Red:** Conexión a internet

#### **Software Requerido**
- **Python:** 3.11 o superior
- **MySQL:** 8.0 o superior
- **Sistema Operativo:** Windows 10/11, Linux, macOS

### **Instalación Paso a Paso**

```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/Sistema_Laboratorio-v2.git
cd Sistema_Laboratorio-v2

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales

# 5. Inicializar base de datos
python scripts/setup_database.py

# 6. (Opcional) Cargar datos de prueba
python scripts/seed_data.py

# 7. Ejecutar aplicación
python web_app.py

# Abrir navegador en: http://localhost:5000
```

### **Configuración de .env**

```env
# Base de Datos
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=laboratorio_sena
DB_PORT=3306

# Aplicación
SECRET_KEY=tu_clave_secreta_aqui
FLASK_ENV=development  # production en servidor
DEBUG=True  # False en producción

# JWT
JWT_SECRET_KEY=otra_clave_secreta
JWT_ACCESS_TOKEN_EXPIRES=3600

# Email (para notificaciones)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_email

# Rutas
UPLOAD_FOLDER=app/static/uploads
BACKUP_FOLDER=backups
```

---

## 🔧 Mantenimiento y Soporte

### **Backups Automáticos**

El sistema incluye un módulo completo de backups:

- ✅ **Programación automática:** Diaria, semanal o mensual
- ✅ **Compresión:** Archivos .sql comprimidos
- ✅ **Historial:** Lista de todos los backups realizados
- ✅ **Restauración:** Con confirmación y loading visual
- ✅ **Descarga:** Descargar backups al dispositivo
- ✅ **Eliminación:** Gestión de backups antiguos

### **Monitoreo del Sistema**

```python
# Estado del sistema en tiempo real
- Uso de CPU y RAM
- Espacio en disco
- Conexiones MySQL activas
- Número de usuarios conectados
- Operaciones por minuto
```

### **Logs y Auditoría**

Todos los logs se guardan en la tabla `logs` con:
- Timestamp exacto
- Usuario que realizó la acción
- Módulo afectado
- Descripción de la operación
- IP del usuario
- Resultado (éxito/error)

### **Actualización del Sistema**

```bash
# 1. Hacer backup completo
python scripts/backup.py

# 2. Actualizar código
git pull origin main

# 3. Actualizar dependencias
pip install -r requirements.txt --upgrade

# 4. Migrar base de datos (si hay cambios)
python scripts/migrate_database.py

# 5. Reiniciar servidor
python web_app.py
```

### **Solución de Problemas Comunes**

#### **Error: No module named 'flask'**
```bash
# Solución: Activar entorno virtual
.venv\Scripts\activate
pip install -r requirements.txt
```

#### **Error: Can't connect to MySQL**
```bash
# Verificar:
1. MySQL está corriendo
2. Credenciales en .env son correctas
3. Puerto 3306 está abierto
4. Usuario tiene permisos
```

#### **Error: Modal bloqueado**
```bash
# Solución: Limpiar caché del navegador
Ctrl + Shift + Delete (Chrome)
Ctrl + F5 (Recarga forzada)
```

---

## 📞 Contacto y Soporte

### **Información de Contacto**

- **Email:** gilcentrominero@gmail.com
- **Ubicación:** Centro Minero SENA - Sogamoso, Boyacá
- **Teléfono:** [Número del centro]
- **Sitio web:** [URL del SENA]

### **Recursos Adicionales**

- 📚 **Documentación:** Carpeta `docs/`
- 🎥 **Video tutoriales:** [Enlace]
- ❓ **FAQs:** Módulo de ayuda en el sistema
- 🐛 **Reportar bugs:** [Email o sistema de tickets]

---

## 📄 Licencia

Este sistema ha sido desarrollado para uso exclusivo del **Centro Minero SENA - Sogamoso, Boyacá**.

### **Derechos de Uso**
- ✅ Uso interno en el Centro Minero SENA
- ✅ Modificación según necesidades del centro
- ✅ Adaptación a otros centros SENA (con autorización)
- ❌ Uso comercial no autorizado
- ❌ Distribución sin permiso

---

## 👨‍💻 Créditos

**Desarrollado para:** Centro Minero SENA - Sogamoso, Boyacá  
**Año:** 2024-2025  
**Versión:** 2.0  
**Estado:** ✅ Producción  

---

## 📊 Estadísticas del Proyecto

- **Líneas de código:** ~15,000+
- **Archivos Python:** 45+
- **Templates HTML:** 30+
- **Archivos CSS:** 8
- **Módulos funcionales:** 10
- **Endpoints API:** 100+
- **Tablas BD:** 15+
- **Tiempo de desarrollo:** 6+ meses

---

**Última actualización:** Octubre 2025  
**Documento creado por:** Sistema de Gestión de Laboratorios - SENA

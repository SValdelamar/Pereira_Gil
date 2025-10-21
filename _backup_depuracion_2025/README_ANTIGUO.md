# 🏭 Sistema de Gestión de Laboratorios
## Centro Minero SENA - Sogamoso, Boyacá

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-SENA-2D6A4F?style=flat)](LICENSE)

Sistema web completo de gestión para laboratorios educativos con **reconocimiento facial**, **control de inventario**, **sistema de reservas** y **reportes profesionales**. Desarrollado específicamente para el Centro Minero SENA.

### **🎯 Características Destacadas**
✨ Reconocimiento facial con IA | 📊 Dashboard con estadísticas en tiempo real | 🔐 6 niveles de permisos | 📱 100% Responsive | 🎨 Diseño SENA institucional

---

## 📖 **GUÍA RÁPIDA - 10 MINUTOS**

### **💻 Requisitos del Sistema**

#### **Software Requerido:**
1. **Python 3.11+** → [Descargar aquí](https://www.python.org/downloads/)
2. **MySQL 8.0+** → [Descargar aquí](https://dev.mysql.com/downloads/mysql/)
3. **Git** → [Descargar aquí](https://git-scm.com/downloads)

#### **Especificaciones Mínimas:**
- **RAM:** 4 GB (8 GB recomendado)
- **Disco:** 2 GB de espacio libre
- **Procesador:** Dual-core 2.0 GHz o superior
- **SO:** Windows 10/11, Linux, macOS

#### **Navegadores Compatibles:**
- ✅ Chrome 90+ (recomendado)
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

### **📥 Instalación en 5 Pasos**

```bash
# 1. Descargar el proyecto
git clone https://github.com/TU_USUARIO/Sistema_Laboratorio-v2.git
cd Sistema_Laboratorio-v2

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
copy .env.example .env
# Edita .env con tus credenciales MySQL

# 5. Inicializar y ejecutar
python scripts/setup_database.py
python web_app.py
```

**✅ Listo! Abre:** http://localhost:5000  
**Usuario:** `admin` | **Contraseña:** `admin123`

---

## 🎯 **Funcionalidades**

### **Módulos Principales**
- ✅ **Dashboard** con estadísticas en tiempo real y gráficos interactivos
- ✅ **Gestión de Espacios** (laboratorios, aulas, talleres) con galería de imágenes
- ✅ **Control de Equipos** con estados, mantenimiento y tracking completo
- ✅ **Inventario Inteligente** con alertas de stock y proyección de consumo
- ✅ **Sistema de Reservas** con aprobación multinivel y calendario
- ✅ **Gestión de Usuarios** con 6 niveles de permisos y roles personalizados
- ✅ **Reconocimiento Facial** con IA para login y registro biométrico

### **Características Avanzadas**
- ✅ **Reportes Profesionales** en PDF y Excel con gráficos
- ✅ **Backup y Restauración** automática de base de datos con confirmación
- ✅ **Sistema de Ayuda** integrado con tutoriales interactivos
- ✅ **Registro Completo** de actividades y auditoría
- ✅ **Notificaciones** en tiempo real por email y en sistema
- ✅ **Interfaz Responsive** optimizada para móviles y tablets
- ✅ **Tema Personalizado** con paleta de colores SENA institucional
- ✅ **Animaciones Suaves** y efectos hover profesionales

## 🐛 **¿Problemas? Soluciones Rápidas**

| Error | Solución |
|---|---|
| `No module named 'flask'` | El entorno virtual no está activado. Ejecuta: `.venv\Scripts\Activate.ps1` y luego `pip install -r requirements.txt` |
| `No module named 'reportlab'` | `pip install reportlab openpyxl xlsxwriter` |
| `Can't connect to MySQL` | 1. Verifica que MySQL esté corriendo<br>2. Revisa credenciales en `.env`<br>3. Verifica el puerto (default: 3306) |
| `Access denied for user` | Usuario o contraseña incorrectos en `.env` |
| `Database doesn't exist` | Ejecuta `python scripts/setup_database.py` para crear la BD |
| Modal de backup bloqueado | Recarga la página (Ctrl+F5) para limpiar backdrops |
| Reconocimiento facial no funciona | Instala: `pip install opencv-python face-recognition dlib` |

---

## 📚 **Documentación Completa**

- **Guía Detallada:** [INSTALACION_RAPIDA.md](INSTALACION_RAPIDA.md)
- **Resumen del Proyecto:** [PROYECTO_RESUMEN_COMPLETO.md](docs/PROYECTO_RESUMEN_COMPLETO.md)
- **Roles y Permisos:** [GUIA_ROLES_USUARIOS.md](docs/GUIA_ROLES_USUARIOS.md)

---

## 🔐 **Niveles de Usuario**

| Nivel | Rol | Permisos |
|---|---|---|
| 1 | Aprendiz | Solo consulta |
| 2 | Funcionario | Consulta extendida |
| 3-4 | Instructor | Gestión de módulos |
| 5 | Instructor Inventario | Aprobación de reservas |
| 6 | Administrador | Control total |

---

## 🗂️ **Estructura del Proyecto**

```
Sistema_Laboratorio-v2/
├── app/                    # Aplicación organizada
│   ├── utils/             # Utilidades (permisos, reportes, notificaciones)
│   ├── static/            # CSS, JS
│   └── templates/         # HTML (auth, dashboard, modules)
├── docs/                  # Documentación completa
├── scripts/               # Setup y seed database
├── web_app.py            # 🚀 Ejecutar el proyecto
├── requirements.txt      # Dependencias
└── .env.example          # Configuración ejemplo
```

## 🛠️ **Tecnologías**

### **Backend**
- **Framework:** Flask 3.1.1 (Python)
- **Base de Datos:** MySQL 8.0+ con MySQL Connector
- **Autenticación:** Flask-JWT-Extended + bcrypt
- **APIs:** Flask-RESTful + Flask-CORS

### **Frontend**
- **Framework CSS:** Bootstrap 5.3
- **Diseño:** CSS3 custom con variables y animaciones
- **JavaScript:** Vanilla JS con DOM manipulation
- **Iconos:** Bootstrap Icons 1.11

### **Inteligencia Artificial**
- **Visión Computacional:** OpenCV 4.12
- **Reconocimiento Facial:** face_recognition + dlib
- **Procesamiento:** NumPy 2.2 + Pillow 11.3

### **Reportes y Exportación**
- **PDF:** ReportLab 4.2 con gráficos personalizados
- **Excel:** openpyxl 3.1 + xlsxwriter 3.2
- **Generación de datos:** Faker 34.0

### **Utilidades**
- **Síntesis de voz:** pyttsx3 2.90
- **Reconocimiento de voz:** SpeechRecognition 3.10
- **Fechas:** python-dateutil 2.9 + pytz 2025.2
- **Sistema:** psutil 7.1 para monitoreo

---

## 🆕 **Últimas Actualizaciones (Oct 2025)**

### **Módulo de Backup Mejorado**
- ✅ Modal de confirmación con z-index optimizado para evitar bloqueos
- ✅ Loading overlay dinámico que se crea solo cuando se necesita
- ✅ Timer visual del tiempo de procesamiento de backup
- ✅ Botón de emergencia para cerrar operaciones largas
- ✅ Limpieza automática de backdrops residuales de Bootstrap
- ✅ Estilos profesionales con gradientes y sombras

### **Mejoras de UI/UX**
- ✅ Tarjetas de backup con hover effects profesionales
- ✅ Iconos circulares con gradiente verde SENA
- ✅ Cajas de advertencia con diseño mejorado
- ✅ Responsive design optimizado para móviles
- ✅ Animaciones suaves en todos los elementos interactivos

### **Correcciones Técnicas**
- ✅ Fix crítico de z-index en modales de Bootstrap
- ✅ Eliminación de múltiples backdrops simultáneos
- ✅ Manejo correcto de eventos `show.bs.modal` y `shown.bs.modal`
- ✅ Pointer-events optimizados para elementos clickeables
- ✅ Console logs para debugging en desarrollo

### **Optimizaciones de Código**
- ✅ Modularización de funciones JavaScript
- ✅ CSS con !important para forzar jerarquía de capas
- ✅ Limpieza de DOM al cargar página
- ✅ Gestión de timers y intervalos optimizada

---

## 📞 **Contacto y Soporte**

- **Email:** gilcentrominero@gmail.com
- **Ubicación:** Centro Minero SENA - Sogamoso, Boyacá
- **Documentación completa:** Carpeta `docs/`

---

## 🎨 **Características del Sistema**

### **Diseño y UX**
- 🎨 Paleta de colores corporativa SENA (verde #2D6A4F)
- 🌓 Diseño consistente en todos los módulos
- 📱 100% responsive (desktop, tablet, móvil)
- ⚡ Animaciones CSS3 suaves y profesionales
- 🖱️ Efectos hover en tarjetas y botones
- 🔔 Notificaciones toast elegantes

### **Seguridad**
- 🔐 Autenticación JWT con tokens seguros
- 🔒 Contraseñas hasheadas con bcrypt
- 👤 Sistema de permisos multinivel (6 roles)
- 📝 Registro completo de auditoría
- 🔑 Recuperación de contraseña por email
- 🎭 Reconocimiento facial opcional

### **Performance**
- ⚡ Carga rápida con CSS optimizado
- 🗄️ Queries MySQL optimizadas
- 📦 Caching de datos estáticos
- 🔄 Actualización en tiempo real con AJAX
- 💾 Gestión eficiente de memoria

### **Mantenimiento**
- 🔧 Backup automático programable
- 📊 Monitoreo de estado del sistema
- 📝 Logs detallados para debugging
- 🧪 Código modular y mantenible
- 📚 Documentación completa en español

---

## ⚠️ **Notas Importantes**

1. **Seguridad:** Cambia las credenciales por defecto (`admin`/`admin123`) después del primer login
2. **Backups:** Se guardan automáticamente en carpeta `backups/` con timestamp
3. **Configuración:** Edita `.env` con tus credenciales de MySQL antes de ejecutar
4. **Reconocimiento Facial:** Es opcional - el sistema funciona perfectamente sin IA
5. **Actualizaciones:** Revisa la sección "Últimas Actualizaciones" para nuevas features
6. **Soporte:** Consulta la carpeta `docs/` para guías detalladas

## 📄 Licencia

Centro Minero SENA - Sogamoso, Boyacá

## 👨‍💻 Autor

Sistema desarrollado para el Centro Minero SENA

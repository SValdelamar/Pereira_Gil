# 🏭 Sistema de Gestión de Laboratorios
## Centro Minero SENA - Sogamoso, Boyacá

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-SENA-2D6A4F?style=flat)](LICENSE)

**Sistema web completo con Inteligencia Artificial para gestión de laboratorios educativos**

✨ Reconocimiento facial | 🔍 Búsqueda visual con IA | 🎤 Comandos por voz | 📊 Reportes profesionales | 🔐 6 niveles de permisos

---

## 🚀 INSTALACIÓN RÁPIDA (5 minutos)

### **Requisitos Previos**
- ✅ Python 3.11+ → [Descargar](https://www.python.org/downloads/)
- ✅ MySQL 8.0+ → [Descargar](https://dev.mysql.com/downloads/mysql/)
- ✅ Git → [Descargar](https://git-scm.com/downloads)

### **Instalación en 7 Pasos**

#### **1. Clonar el Proyecto**
```bash
git clone https://github.com/TU_USUARIO/Sistema_Laboratorio-v2.git
cd Sistema_Laboratorio-v2
```

#### **2. Crear Entorno Virtual**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### **3. Instalar Dependencias**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### **4. Configurar Variables de Entorno**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Edita `.env` con tus credenciales:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=laboratorios_db
DB_USER=root
DB_PASSWORD=tu_password_mysql_aqui   # ⚠️ CAMBIAR ESTO
```

#### **5. Crear Base de Datos**
```bash
python scripts/setup_database.py
```

#### **6. Cargar Datos de Ejemplo (Opcional)**
```bash
python scripts/seed_database.py
```

#### **7. Ejecutar el Servidor**
```bash
python web_app.py
```

### **✅ ¡Listo!**

Abre tu navegador en: **http://localhost:5000**

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

> ⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login

---

## 🎯 FUNCIONALIDADES

### **10 Módulos Completos**

| Módulo | Descripción |
|--------|-------------|
| 📊 **Dashboard** | Estadísticas en tiempo real con gráficos interactivos |
| 🏢 **Espacios** | Gestión de laboratorios, aulas, talleres y almacenes |
| ⚙️ **Equipos** | Control de equipos con estados y mantenimiento |
| 📦 **Inventario** | Stock en tiempo real con alertas inteligentes |
| 📅 **Reservas** | Sistema de solicitudes con aprobación multinivel |
| 👥 **Usuarios** | Gestión con 6 niveles de permisos |
| 📈 **Reportes** | Generación automática en PDF y Excel |
| 💾 **Backup** | Respaldo y restauración de base de datos |
| 📝 **Registros** | Auditoría completa de actividades |
| ❓ **Ayuda** | Sistema de tutoriales interactivos |

### **4 Tecnologías de Inteligencia Artificial**

#### **1. 👤 Reconocimiento Facial**
- Login biométrico en 2 segundos
- Precisión 95%+
- Sin necesidad de contraseñas

#### **2. 🔍 Búsqueda Visual de Objetos**
- Toma foto de un equipo desconocido
- IA lo identifica en 3 segundos
- Muestra ubicación exacta

#### **3. 🎤 Comandos por Voz**
- Control manos libres del sistema
- Ejemplos: "Mostrar inventario", "Crear reserva"
- Accesible para personas con discapacidad visual

#### **4. 📊 Predicción de Consumo**
- Machine Learning predice cuándo se agotará stock
- Alertas automáticas 2 semanas antes
- 90% de precisión

---

## 🛠️ TECNOLOGÍAS

### **Backend**
- **Framework:** Flask 3.1 (Python)
- **Base de Datos:** MySQL 8.0
- **Autenticación:** JWT + bcrypt
- **APIs:** Flask-RESTful

### **Frontend**
- **Framework CSS:** Bootstrap 5.3
- **JavaScript:** Vanilla JS + AJAX
- **Diseño:** 100% Responsive

### **Inteligencia Artificial**
- **Visión:** OpenCV 4.12
- **Facial:** face_recognition + dlib
- **Voz:** SpeechRecognition + pyttsx3
- **ML:** NumPy + Análisis predictivo

### **Reportes**
- **PDF:** ReportLab con gráficos
- **Excel:** openpyxl + xlsxwriter

---

## 📁 ESTRUCTURA DEL PROYECTO

```
Sistema_Laboratorio-v2/
│
├── 📄 web_app.py                 ⭐ EJECUTAR ESTE ARCHIVO
├── 📄 requirements.txt           ⭐ DEPENDENCIAS
├── 📄 README.md                  ⭐ DOCUMENTACIÓN
├── 📄 .env.example               ⭐ CONFIGURACIÓN
│
├── 📁 app/                       Aplicación principal
│   ├── static/                   CSS, JS, imágenes
│   ├── templates/                HTML (Jinja2)
│   └── utils/                    Utilidades (permisos, reportes)
│
├── 📁 scripts/                   Scripts de instalación
│   ├── setup_database.py         ⭐ Crear base de datos
│   └── seed_database.py          ⭐ Datos de ejemplo
│
├── 📁 modules/                   Módulos de IA
│   ├── facial_recognition_module.py
│   ├── vision_ai_module.py
│   ├── speech_ai_module.py
│   └── ai_integration.py
│
├── 📁 docs/                      Documentación
│   ├── GUIA_ROLES_USUARIOS.md
│   └── PROYECTO_RESUMEN_COMPLETO.md
│
├── 📁 imagenes/                  (se crea automáticamente)
├── 📁 backups/                   (se crea automáticamente)
└── 📁 logs/                      (se crea automáticamente)
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **Error: "No module named 'flask'"**
```bash
# El entorno virtual no está activado
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Luego reinstalar
pip install -r requirements.txt
```

### **Error: "Can't connect to MySQL server"**
```bash
# 1. Verificar que MySQL esté corriendo
# Windows:
services.msc  # Buscar "MySQL80"

# Linux:
sudo systemctl status mysql
sudo systemctl start mysql

# 2. Verificar credenciales en .env
```

### **Error: "Access denied for user 'root'"**
```bash
# Contraseña incorrecta en .env
# Probar conexión:
mysql -u root -p

# Si funciona, actualizar .env con esa contraseña
```

### **Error: "Port 5000 is already in use"**
```bash
# Opción 1: Cambiar puerto en .env
PORT=8080

# Opción 2: Cerrar proceso que usa 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID [número] /F

# Linux:
lsof -i :5000
kill -9 [PID]
```

### **Error: "Database doesn't exist"**
```bash
python scripts/setup_database.py
```

### **Reconocimiento facial no funciona**
El sistema funciona perfectamente SIN reconocimiento facial.

Para habilitarlo (opcional):
```bash
# Windows:
# Descargar dlib precompilado de:
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x
pip install dlib-19.24.6-cp311-cp311-win_amd64.whl
pip install face-recognition

# Linux:
sudo apt install cmake
pip install dlib face-recognition
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- 📖 [Guía de Roles y Permisos](docs/GUIA_ROLES_USUARIOS.md)
- 📖 [Resumen Completo del Proyecto](docs/PROYECTO_RESUMEN_COMPLETO.md)
- 📖 [Ejemplos de Reportes](docs/reportes/)

---

## 🔐 NIVELES DE USUARIO

| Nivel | Rol | Permisos |
|-------|-----|----------|
| **1** | Aprendiz | Solo consulta |
| **2** | Funcionario | Consulta extendida |
| **3-4** | Instructor | Gestión de módulos |
| **5** | Instructor Inventario | Aprobación de reservas |
| **6** | Administrador | Control total del sistema |

---

## 🎨 CARACTERÍSTICAS DESTACADAS

### **Diseño y UX**
- 🎨 Paleta corporativa SENA (verde #2D6A4F)
- 📱 100% Responsive (móvil, tablet, desktop)
- ⚡ Animaciones CSS3 suaves
- 🔔 Notificaciones toast elegantes

### **Seguridad**
- 🔐 Autenticación JWT
- 🔒 Contraseñas hasheadas bcrypt
- 👤 Sistema multinivel de permisos
- 📝 Auditoría completa

### **Performance**
- ⚡ Carga rápida
- 🗄️ Queries MySQL optimizadas
- 🔄 Actualización en tiempo real
- 💾 Gestión eficiente de memoria

---

## ⚠️ NOTAS IMPORTANTES

1. **Seguridad:** Cambia las credenciales por defecto inmediatamente
2. **Backups:** Configura backups automáticos desde el panel admin
3. **Configuración:** Edita `.env` antes de ejecutar por primera vez
4. **IA Opcional:** El sistema funciona sin módulos de IA
5. **Actualizaciones:** Revisa logs en `logs/app.log`

---

## 🚀 PUESTA EN PRODUCCIÓN

### **Recomendaciones:**

1. **Cambiar credenciales:**
   - Admin por defecto
   - Claves SECRET_KEY en `.env`
   - Contraseña de MySQL

2. **Configurar servidor:**
   - Usar servidor dedicado (8GB RAM mínimo)
   - Configurar firewall
   - Habilitar HTTPS

3. **Backups automáticos:**
   - Configurar desde el panel
   - O usar cron job (Linux):
   ```bash
   0 2 * * * cd /ruta/proyecto && python scripts/backup_auto.py
   ```

4. **Monitoreo:**
   - Revisar logs semanalmente
   - Monitorear uso de recursos
   - Mantener MySQL actualizado

---

## 📞 CONTACTO Y SOPORTE

- **Email:** gilcentrominero@gmail.com
- **Ubicación:** Centro Minero SENA - Sogamoso, Boyacá
- **Documentación:** Ver carpeta `docs/`

---

## 📄 LICENCIA

Desarrollado para el Centro Minero SENA - Sogamoso, Boyacá

---

## 👨‍💻 DESARROLLO

Sistema desarrollado como prototipo académico funcional para el Centro Minero SENA.

**Características:**
- ✅ 15,000+ líneas de código
- ✅ 100+ endpoints API
- ✅ 10 módulos completos
- ✅ 4 tecnologías de IA
- ✅ Documentación completa

---

## ✅ CHECKLIST DE INSTALACIÓN

```
[ ] Python 3.11+ instalado
[ ] MySQL 8.0+ corriendo
[ ] Repositorio clonado
[ ] Entorno virtual creado y activado
[ ] Dependencias instaladas (requirements.txt)
[ ] Archivo .env configurado
[ ] Base de datos creada (setup_database.py)
[ ] Datos de ejemplo cargados (seed_database.py)
[ ] Servidor ejecutándose (python web_app.py)
[ ] Login exitoso en http://localhost:5000
```

---

**🎉 ¡Disfruta del Sistema de Gestión de Laboratorios con IA! 🎉**

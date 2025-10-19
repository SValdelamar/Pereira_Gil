# Sistema de Gestión de Laboratorios - Centro Minero SENA

Sistema web completo para la gestión de laboratorios, equipos, inventario y reservas con integración de IA.

## 🚀 Características Principales

### Gestión Completa
- **Laboratorios y Aulas**: Administración de espacios físicos
- **Equipos**: Control de equipos con estados y mantenimiento
- **Inventario**: Gestión de stock con alertas de nivel bajo
- **Reservas**: Sistema de reservas de equipos
- **Usuarios**: Control de acceso con niveles de permisos

### Inteligencia Artificial
- **Reconocimiento Facial**: Login y registro con OpenCV
- **IA Visual**: Reconocimiento de equipos por imagen
- **Entrenamiento Visual**: Sistema para entrenar modelos de reconocimiento

### Seguridad y Backup
- **Autenticación JWT**: API REST segura
- **Niveles de Usuario**: Control granular de permisos
- **Backups Automáticos**: Sistema de respaldo de base de datos
- **Auditoría**: Logs completos de seguridad

## 📋 Requisitos

- Python 3.8+ (Recomendado: 3.11+)
- MySQL 8.0+ (o MariaDB 10.5+)
- Navegador web moderno

## ⚡ Instalación Rápida (5 pasos)

### 1. Clonar el repositorio
```bash
git clone <url-repositorio>
cd Sistema_Laboratorio-v2
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
# Copiar archivo de configuración
copy .env.example .env_produccion

# Editar .env_produccion con tus credenciales de MySQL
```

### 5. Instalar base de datos y ejecutar
```bash
# Crear todas las tablas y datos iniciales automáticamente
python setup_database.py

# Iniciar el servidor
python web_app.py
```

Acceder a: http://localhost:5000

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

> ⚠️ **Importante:** Cambia la contraseña después del primer inicio de sesión

## 👥 Niveles de Usuario

1. **Nivel 1**: Estudiante (solo lectura)
2. **Nivel 2**: Instructor (gestión básica)
3. **Nivel 3**: Coordinador (gestión avanzada)
4. **Nivel 4**: Administrador (acceso completo)

## 🗂️ Estructura del Proyecto

```
Sistema_Laboratorio-v2/
├── web_app.py              # Aplicación principal (Flask)
├── setup_database.py       # Configuración inicial de BD
├── seed_database.py        # Datos iniciales
├── requirements.txt        # Dependencias Python
├── .env_produccion         # Configuración del sistema
├── .gitignore
├── modules/                # Módulos de IA
│   ├── ai_integration.py
│   ├── facial_recognition_module.py
│   └── visual_recognition_module.py
├── utils/                  # Utilidades y permisos
├── templates/              # Plantillas HTML (33 vistas)
├── static/                 # CSS, JS, imágenes
├── scripts/                # Scripts de inicio
│   ├── iniciar_servidor.bat
│   ├── iniciar_servidor.ps1
│   └── activar_entorno.bat
├── backups/                # Backups automáticos de BD
├── imagenes/               # Imágenes del sistema
└── logs/                   # Logs del sistema
```

## 🔑 Funcionalidades por Módulo

### Dashboard
- Estadísticas generales
- Gráficos de uso
- Alertas de stock bajo

### Equipos
- Registro con imágenes
- Control de estados
- Historial de mantenimiento

### Inventario
- Control de stock
- Alertas de vencimiento
- Gestión de proveedores

### Reservas
- Calendario de reservas
- Validación de disponibilidad
- Historial de uso

### IA Visual
- Reconocimiento de equipos
- Entrenamiento de modelos
- Estadísticas de precisión

### Backup
- Creación de backups
- Restauración
- Descarga de copias

## 🛠️ Tecnologías

- **Backend**: Flask, Flask-RESTful, Flask-JWT-Extended
- **Base de Datos**: MySQL
- **IA**: OpenCV, NumPy, Pillow
- **Frontend**: Bootstrap 5, JavaScript
- **Autenticación**: JWT, bcrypt

## 📝 Notas Importantes

- El sistema funciona sin dependencias opcionales de IA usando OpenCV
- Los backups se almacenan en la carpeta `backups/`
- Las imágenes de entrenamiento en `imagenes/entrenamiento/`
- Configurar `MYSQLDUMP_PATH` y `MYSQL_PATH` en `.env` si es necesario

## 🐛 Solución de Problemas

### Error de conexión a MySQL
Verificar credenciales en `.env_produccion`

### Error de importación de módulos
```bash
pip install -r requirements.txt --upgrade
```

### Error en reconocimiento facial
El sistema usa OpenCV como respaldo si face-recognition no está disponible

## 📄 Licencia

Centro Minero SENA - Sogamoso, Boyacá

## 👨‍💻 Autor

Sistema desarrollado para el Centro Minero SENA

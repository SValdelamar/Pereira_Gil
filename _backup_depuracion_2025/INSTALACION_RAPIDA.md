# 🚀 GUÍA DE INSTALACIÓN RÁPIDA
## Sistema de Gestión de Laboratorios - Centro Minero SENA

**Tiempo estimado:** 5-10 minutos

---

## ✅ Requisitos Previos

Antes de empezar, asegúrate de tener instalado:

- ✅ **Python 3.11+** - [Descargar](https://www.python.org/downloads/)
- ✅ **MySQL 8.0+** - [Descargar](https://dev.mysql.com/downloads/mysql/)
- ✅ **Git** - [Descargar](https://git-scm.com/downloads)

---

## 📦 INSTALACIÓN PASO A PASO

### **Paso 1: Clonar el Repositorio**

```bash
git clone <URL_DEL_REPOSITORIO>
cd Sistema_Laboratorio-v2
```

---

### **Paso 2: Crear Entorno Virtual**

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### **Paso 3: Instalar Dependencias**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ Esto tomará 2-3 minutos

---

### **Paso 4: Configurar Variables de Entorno**

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

**Edita el archivo `.env` con tus credenciales:**

```env
# Base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=laboratorios_db
DB_USER=root
DB_PASSWORD=tu_password_mysql_aqui

# Claves secretas (genera nuevas para producción)
SECRET_KEY=tu_clave_secreta_aqui
JWT_SECRET_KEY=tu_jwt_secret_aqui
```

---

### **Paso 5: Crear Base de Datos**

**Opción A - Automática (Recomendada):**
```bash
python scripts/setup_database.py
```

**Opción B - Manual:**
```sql
CREATE DATABASE laboratorios_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Luego ejecuta: `python scripts/setup_database.py`

---

### **Paso 6: Cargar Datos Iniciales (Opcional)**

```bash
python scripts/seed_database.py
```

Esto crea:
- ✅ Usuario administrador
- ✅ Datos de ejemplo
- ✅ Laboratorios de prueba

---

### **Paso 7: Ejecutar el Servidor**

```bash
python web_app.py
```

**Verás algo como:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

---

## 🎉 ¡LISTO!

Abre tu navegador en: **http://localhost:5000**

### 🔐 Credenciales por Defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> ⚠️ **IMPORTANTE:** Cambia estas credenciales después del primer login

---

## 🐛 Solución de Problemas Comunes

### ❌ Error: "No module named 'reportlab'"

```bash
pip install reportlab openpyxl xlsxwriter
```

### ❌ Error: "Can't connect to MySQL server"

1. Verifica que MySQL esté corriendo
2. Revisa credenciales en `.env`
3. Asegúrate que el puerto 3306 esté disponible

### ❌ Error: "Access denied for user"

Verifica el password en `.env`:
```bash
# Prueba la conexión:
mysql -u root -p
```

### ❌ Error de imports: "No module named 'utils'"

El proyecto usa la nueva estructura. Los imports deben ser:
```python
from app.utils.xxx import xxx
```

---

## 📁 Estructura del Proyecto

```
Sistema_Laboratorio-v2/
├── app/                      # Aplicación principal
│   ├── routes/              # Rutas web
│   ├── api/                 # API REST
│   ├── models/              # Modelos
│   ├── utils/               # Utilidades
│   ├── static/              # CSS, JS
│   └── templates/           # HTML
├── scripts/                 # Setup y seed
├── docs/                    # Documentación
├── tests/                   # Tests
├── web_app.py              # 🚀 Ejecutar el proyecto
├── requirements.txt        # Dependencias
├── .env.example            # Configuración ejemplo
└── README.md               # Documentación
```

---

## 🚀 Comandos Útiles

```bash
# Iniciar servidor
python web_app.py

# Ejecutar tests
python -m pytest tests/

# Crear backup de BD
# (desde el panel de admin en la web)

# Ver logs
tail -f logs/app.log  # Linux/Mac
Get-Content logs/app.log -Wait  # Windows PowerShell
```

---

## 📚 Documentación Adicional

- **Guía Completa:** `docs/PROYECTO_RESUMEN_COMPLETO.md`
- **Roles y Permisos:** `docs/GUIA_ROLES_USUARIOS.md`
- **API Documentation:** http://localhost:5000/api/docs (cuando esté corriendo)

---

## 💡 Próximos Pasos

1. ✅ Cambiar credenciales por defecto
2. ✅ Configurar backup automático
3. ✅ Revisar configuración de seguridad
4. ✅ Personalizar para tu institución

---

## 🆘 ¿Necesitas Ayuda?

- **Email:** gilcentrominero@gmail.com
- **Documentación:** Ver carpeta `docs/`
- **Issues:** [GitHub Issues](tu-repo/issues)

---

## ✅ Checklist de Instalación

- [ ] Python 3.11+ instalado
- [ ] MySQL 8.0+ corriendo
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Archivo .env configurado
- [ ] Base de datos creada
- [ ] Datos iniciales cargados
- [ ] Servidor ejecutándose
- [ ] Login exitoso en http://localhost:5000

---

**🎊 ¡Disfruta del Sistema de Gestión de Laboratorios!** 🎊

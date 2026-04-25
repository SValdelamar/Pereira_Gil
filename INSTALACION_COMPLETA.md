# 🚀 Guía de Instalación Completa - Sistema Laboratorios SENA

## 📋 **Tabla de Contenido**

1. [Requisitos Previos](#requisitos-previos)
2. [Archivos de Configuración](#archivos-de-configuración)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Configuración de Base de Datos](#configuración-de-base-de-datos)
5. [Dependencias Opcionales](#dependencias-opcionales)
6. [Verificación de Instalación](#verificación-de-instalación)
7. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
8. [Configuración de Producción](#configuración-de-producción)

---

## 🔧 **Requisitos Previos**

### **Sistema Operativo**
- ✅ **Windows 10/11** (64-bit)
- ✅ **Linux Ubuntu 20.04+**
- ✅ **macOS 10.15+**

### **Python**
- ✅ **Python 3.11+** (recomendado 3.11.9)
- ✅ **pip** (gestor de paquetes)
- ✅ **venv** (entornos virtuales)

### **Base de Datos**
- ✅ **MySQL 8.0+** o **MariaDB 10.5+**
- ✅ Acceso como administrador para crear BD

### **Hardware Mínimo**
- 💾 **RAM:** 4GB (8GB recomendado)
- 💾 **Disco:** 10GB libres
- 🖥️ **Procesador:** 2 núcleos (4 recomendados)

---

## 📁 **Archivos de Configuración**

### **1. Requirements**
```
📄 requirements.txt
```
- ✅ **Dependencias esenciales** para producción
- ✅ **Opcionales comentadas** (IA, reconocimiento facial)
- ✅ **Versiones verificadas** y compatibles
- ✅ **Notas de instalación** para cada caso

### **2. Variables de Entorno**
```
📄 .env.example          # Plantilla de configuración
📄 .env_produccion       # Configuración de producción (crear)
📄 .env                   # Configuración local (no subir a Git)
```

### **3. Scripts de Instalación**
```
📄 migrate.py             # Sistema de migraciones
📄 check_setup.py         # Verificación automática
📄 scripts/check_server.py # Verificación de servidor
```

---

## 🚀 **Instalación Paso a Paso**

### **Paso 1: Clonar el Repositorio**
```bash
# Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd Sistema_Laboratorio-v2

# Verificar estructura
ls -la
```

### **Paso 2: Crear Entorno Virtual**
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

# Verificar Python
python --version  # Debe ser 3.11+
```

### **Paso 3: Instalar Dependencias**
```bash
# Instalar dependencias básicas
pip install -r requirements.txt

# Verificar instalación
pip list
```

### **Paso 4: Configurar Variables de Entorno**
```bash
# Copiar plantilla de configuración
cp .env.example .env_produccion

# Editar archivo de configuración
notepad .env_produccion  # Windows
nano .env_produccion     # Linux/macOS
```

**Configuración mínima requerida:**
```bash
# Base de datos
DB_HOST=localhost
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_segura
DB_NAME=laboratorio_sistema

# Aplicación
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=tu_clave_secreta_generada

# URL base
APP_URL=http://localhost:5000
```

### **Paso 5: Configurar Base de Datos**
```bash
# Conectar a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE laboratorio_sistema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Crear usuario (opcional, recomendado)
CREATE USER 'laboratorio_user'@'localhost' IDENTIFIED BY 'contraseña_segura';
GRANT ALL PRIVILEGES ON laboratorio_sistema.* TO 'laboratorio_user'@'localhost';
FLUSH PRIVILEGES;

# Salir de MySQL
EXIT;
```

### **Paso 6: Ejecutar Migraciones**
```bash
# Ejecutar migraciones automáticas
python migrate.py

# Verificar estado
python migrate.py --status
```

### **Paso 7: Verificar Instalación**
```bash
# Verificar configuración completa
python check_setup.py

# Iniciar aplicación
python web_app.py
```

**Acceder al sistema:**
```
🌐 http://localhost:5000
👤 Usuario: admin
🔑 Contraseña: admin123
```

---

## 🗄️ **Configuración de Base de Datos**

### **Opción A: MySQL Local**
```bash
# Instalar MySQL
# Windows: Descargar desde mysql.com
# Ubuntu: sudo apt install mysql-server
# macOS: brew install mysql

# Iniciar servicio
# Windows: net start mysql
# Ubuntu: sudo systemctl start mysql
# macOS: brew services start mysql
```

### **Opción B: MySQL en Docker**
```bash
# Ejecutar MySQL en Docker
docker run --name mysql-lab \
  -e MYSQL_ROOT_PASSWORD=contraseña_segura \
  -e MYSQL_DATABASE=laboratorio_sistema \
  -p 3306:3306 \
  -d mysql:8.0

# Conectar a la BD
mysql -h localhost -P 3306 -u root -p
```

### **Opción C: MariaDB**
```bash
# Instalar MariaDB
# Ubuntu: sudo apt install mariadb-server
# CentOS: sudo yum install mariadb-server

# Configurar
sudo mysql_secure_installation

# Crear BD
mysql -u root -p
CREATE DATABASE laboratorio_sistema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🤖 **Dependencias Opcionales**

### **Reconocimiento Facial**
```bash
# Paso 1: Descargar dlib wheel
# Visitar: https://github.com/z-mahmud22/Dlib_Windows_Python3.x
# Descargar: dlib-19.24.6-cp311-cp311-win_amd64.whl

# Paso 2: Instalar dlib
pip install dlib-19.24.6-cp311-win_amd64.whl

# Paso 3: Instalar face-recognition
pip install face-recognition

# Paso 4: Actualizar .env_produccion
FACE_RECOGNITION_ENABLED=True
```

### **Captura de Audio**
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### **IA Avanzada (TensorFlow)**
```bash
# Opción ligera (recomendada)
pip install tflite-runtime

# Opción completa (pesada)
pip install tensorflow

# Utilidades adicionales
pip install librosa matplotlib seaborn
```

---

## ✅ **Verificación de Instalación**

### **Script Automático**
```bash
# Verificación completa
python check_setup.py

# Debe mostrar:
✅ Python 3.11+ detectado
✅ Entorno virtual activado
✅ Dependencias instaladas
✅ Base de datos accesible
✅ Migraciones ejecutadas
✅ Configuración válida
```

### **Verificación Manual**
```bash
# 1. Verificar Python
python --version

# 2. Verificar dependencias
pip list | grep Flask

# 3. Verificar BD
mysql -u tu_usuario -p -e "SHOW DATABASES;"

# 4. Verificar migraciones
python migrate.py --status

# 5. Iniciar aplicación
python web_app.py
```

### **Testing Funcional**
Acceder a los módulos principales:
- ✅ **Dashboard:** http://localhost:5000/dashboard
- ✅ **Login:** http://localhost:5000/login
- ✅ **Laboratorios:** http://localhost:5000/laboratorios
- ✅ **Usuarios:** http://localhost:5000/usuarios

---

## 🔧 **Solución de Problemas Comunes**

### **Problema: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Solución: Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Reinstalar dependencias
pip install -r requirements.txt
```

### **Problema: "Access denied for user"**
```bash
# Solución: Verificar credenciales MySQL
mysql -u root -p
SHOW GRANTS FOR 'tu_usuario'@'localhost';

# Crear usuario si no existe
CREATE USER 'laboratorio_user'@'localhost' IDENTIFIED BY 'contraseña';
GRANT ALL PRIVILEGES ON laboratorio_sistema.* TO 'laboratorio_user'@'localhost';
```

### **Problema: "Can't connect to MySQL server"**
```bash
# Solución: Verificar que MySQL esté corriendo
# Windows
net start mysql

# Linux
sudo systemctl status mysql
sudo systemctl start mysql

# Verificar puerto
netstat -an | grep 3306
```

### **Problema: "Error loading shared library: libmysqlclient"**
```bash
# Solución: Reinstalar mysql-connector
pip uninstall mysql-connector-python
pip install mysql-connector-python==8.0.33
```

### **Problema: "dlib installation failed"**
```bash
# Solución: Usar wheel precompilado
# Descargar desde: https://github.com/z-mahmud22/Dlib_Windows_Python3.x
pip install dlib-19.24.6-cp311-cp311-win_amd64.whl
```

---

## 🚀 **Configuración de Producción**

### **Variables de Entorno Críticas**
```bash
# .env_produccion
FLASK_ENV=production
FLASK_DEBUG=False
FORCE_HTTPS=True

# Base de datos segura
DB_HOST=tu_ip_servidor
DB_USER=laboratorio_prod
DB_PASSWORD=contraseña_muy_segura_123!
DB_NAME=laboratorio_sistema

# Seguridad
SECRET_KEY=generar_con_secrets_token_hex_32
SESSION_TIMEOUT=30
MAX_LOGIN_ATTEMPTS=3

# Logs
LOG_LEVEL=INFO
LOG_ROTATION=True
```

### **Servidor Web (Gunicorn)**
```bash
# Instalar Gunicorn
pip install gunicorn

# Iniciar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web_app:app

# Configuración de producción
gunicorn -w 4 -b 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 2 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  web_app:app
```

### **Nginx (Opcional)**
```nginx
# /etc/nginx/sites-available/laboratorio_sistema
server {
    listen 80;
    server_name tu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **SSL/TLS (Let's Encrypt)**
```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu_dominio.com

# Renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **Monitoreo y Mantenimiento**

### **Logs del Sistema**
```bash
# Ver logs de aplicación
tail -f logs/app.log

# Ver logs de errores
tail -f logs/error.log

# Logs de MySQL
tail -f /var/log/mysql/error.log
```

### **Backups Automáticos**
```bash
# Configurar en .env_produccion
BACKUP_AUTOMATIC=True
BACKUP_TIME=02:00
BACKUP_RETENTION_DAYS=30

# Ejecutar backup manual
python scripts/backup_database.py
```

### **Actualizaciones**
```bash
# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Actualizar sistema
git pull origin main
python migrate.py
python check_setup.py
```

---

## 🎯 **Resumen de Instalación**

### **Comandos Esenciales**
```bash
# 1. Clonar y configurar
git clone <URL> && cd Sistema_Laboratorio-v2
python -m venv .venv && source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar entorno
cp .env.example .env_produccion
# Editar .env_produccion con tus datos

# 4. Configurar BD
mysql -u root -p
CREATE DATABASE laboratorio_sistema CHARACTER SET utf8mb4;

# 5. Migraciones
python migrate.py

# 6. Verificar
python check_setup.py

# 7. Iniciar
python web_app.py
```

### **Tiempo Estimado**
- ⏱️ **Instalación básica:** 15-20 minutos
- ⏱️ **Con dependencias opcionales:** 30-45 minutos
- ⏱️ **Configuración de producción:** 45-60 minutos

### **Soporte**
- 📖 **Documentación:** `PRODUCCION_READY.md`
- 🔧 **Verificación:** `check_setup.py`
- 🗄️ **Migraciones:** `migrate.py --help`
- 📧 **Issues:** GitHub Issues del proyecto

---

## ✅ **Verificación Final**

Después de la instalación, verifica:

- [ ] **Aplicación inicia** sin errores
- [ ] **Base de datos conecta** correctamente
- [ ] **Login funciona** con admin/admin123
- [ ] **Módulos principales** operativos
- [ ] **Logs se generan** en `logs/`
- [ ] **Migraciones ejecutadas** (`migrate.py --status`)
- [ ] **Configuración válida** (`check_setup.py`)

**¡Sistema listo para uso!** 🎉

---

*Última actualización: 25 de Abril de 2026*
*Versión: 2.0.0 - Production Ready*

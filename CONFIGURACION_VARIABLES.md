# 📋 Guía de Variables de Entorno - Sistema Laboratorios SENA

## 🎯 **Propósito de este Documento**

Explicación detallada de todas las variables de entorno configurables en el sistema, su propósito, valores recomendados y consideraciones de seguridad.

---

## 📁 **Archivos de Configuración**

```
📄 .env.example          # Plantilla completa (NO modificar)
📄 .env_produccion       # Configuración de producción (crear)
📄 .env                  # Configuración local/desarrollo (opcional)
```

---

## 🔐 **Variables Críticas de Seguridad**

### **SECRET_KEY**
```bash
# Propósito: Clave para sesiones y tokens JWT
SECRET_KEY=generar_con_secrets_token_hex_32
```
- **✅ Generación:** `python -c "import secrets; print(secrets.token_hex(32))"`
- **⚠️ Seguridad:** Usar clave única por instalación
- **🔄 Rotación:** Cambiar cada 6 meses en producción

### **DB_PASSWORD**
```bash
# Propósito: Contraseña de base de datos
DB_PASSWORD=contraseña_segura_123!
```
- **✅ Requisitos:** Mínimo 12 caracteres, símbolos incluidos
- **⚠️ Seguridad:** Nunca usar "1234", "password", "root"
- **🔄 Rotación:** Cambiar cada 3 meses

### **FORCE_HTTPS**
```bash
# Propósito: Forzar HTTPS en producción
FORCE_HTTPS=True
```
- **✅ Producción:** Siempre `True`
- **❌ Desarrollo:** `False` (localhost sin SSL)
- **⚠️ Requiere:** Certificado SSL configurado

---

## 🗄️ **Configuración de Base de Datos**

### **Conexión Básica**
```bash
DB_HOST=localhost              # Servidor MySQL
DB_USER=laboratorio_user      # Usuario MySQL
DB_PASSWORD=contraseña_segura # Contraseña MySQL
DB_NAME=laboratorio_sistema   # Nombre de BD
# DB_PORT=3306                # Puerto (opcional, por defecto 3306)
```

### **Consideraciones de Seguridad**
- **✅ Usuario dedicado:** No usar `root` en producción
- **✅ Privilegios mínimos:** Solo permisos necesarios
- **✅ IP específica:** `DB_HOST=192.168.1.100` (no localhost)
- **✅ SSL:** Forzar conexión SSL en MySQL

---

## 🌐 **Configuración de Aplicación**

### **Entorno y Debug**
```bash
FLASK_ENV=production         # development | production | testing
FLASK_DEBUG=False            # Siempre False en producción
APP_URL=http://localhost:5000 # URL base del sistema
```

### **Sesiones y Autenticación**
```bash
SESSION_TIMEOUT=30           # Tiempo de sesión (minutos)
MAX_LOGIN_ATTEMPTS=3          # Intentos fallidos permitidos
LOGIN_LOCKOUT_TIME=15         # Bloqueo tras intentos (minutos)
JWT_EXPIRATION=60             # Expiración token JWT (minutos)
```

### **API y Rate Limiting**
```bash
API_RATE_LIMIT=100            # Solicitudes por minuto por IP
```

---

## 📧 **Configuración de Correo Electrónico**

### **SMTP para Notificaciones**
```bash
SMTP_SERVER=smtp.gmail.com      # Servidor SMTP
SMTP_PORT=587                  # Puerto (587 TLS, 465 SSL)
SMTP_EMAIL=tu_correo@sena.edu.co # Usuario correo
SMTP_PASSWORD=tu_app_password   # Contraseña aplicación
EMAIL_FROM=Sistema <correo@sena.edu.co> # Remitente
SMTP_USE_TLS=True              # Usar TLS
```

### **Configuración Gmail (Recomendado)**
1. **Activar 2FA** en cuenta Gmail
2. **Generar App Password:**
   - Cuenta Google → Seguridad → Contraseñas de aplicaciones
   - Crear nueva contraseña para "Sistema Laboratorios"
3. **Usar App Password** en `SMTP_PASSWORD`

### **Limites de Correo**
```bash
EMAIL_MAX_POR_HORA=100        # Máximo correos por hora
EMAIL_MAX_DESTINATARIOS=50    # Máximo destinatarios por correo
```

---

## 💾 **Configuración de Archivos y Backups**

### **Almacenamiento**
```bash
UPLOAD_DIR=imagenes            # Directorio uploads
MAX_FILE_SIZE=10              # Tamaño máximo archivo (MB)
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx
```

### **Backups Automáticos**
```bash
BACKUP_DIR=backups             # Directorio backups
BACKUP_AUTOMATIC=True          # Habilitar backups
BACKUP_TIME=02:00              # Hora backup (24h)
BACKUP_RETENTION_DAYS=30        # Días retención
```

---

## 🤖 **Configuración de IA y Reconocimiento**

### **Reconocimiento Facial**
```bash
FACE_RECOGNITION_MODEL=models/face_recognition.pkl
FACE_RECOGNITION_THRESHOLD=0.70    # Umbral similitud (0.0-1.0)
```
- **🎯 Rango recomendado:** 0.65-0.75
- **📈 Más alto:** Más seguro, más falsos negativos
- **📉 Más bajo:** Más permissivo, más falsos positivos

### **IA Visual**
```bash
VISION_MODEL=models/vision_model.pkl
VISION_CONFIDENCE_THRESHOLD=0.75    # Umbral confianza (0.0-1.0)
```

---

## 📊 **Configuración de Logging**

### **Niveles y Archivos**
```bash
LOG_LEVEL=INFO                   # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_DIR=logs                     # Directorio logs
LOG_ROTATION=True                # Rotación automática
LOG_MAX_SIZE=10                  # Tamaño máximo log (MB)
LOG_MAX_FILES=5                  # Cantidad máxima archivos
```

### **Niveles Recomendados**
- **🔧 Desarrollo:** `DEBUG`
- **🚀 Producción:** `INFO`
- **📊 Monitoreo:** `WARNING` o `ERROR`

---

## 🔔 **Configuración de Notificaciones (Mantenimiento Predictivo)**

### **Canales Habilitados**
```bash
HABILITAR_EMAIL=false            # Notificaciones por email
HABILITAR_DASHBOARD=true         # Notificaciones en dashboard
HABILITAR_SMS=false              # Notificaciones SMS
HABILITAR_WEBHOOK=false          # Webhook externo
```

### **Configuración Email**
```bash
EMAIL_SERVIDOR=smtp.gmail.com
EMAIL_PUERTO=587
EMAIL_USUARIO=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
EMAIL_REMITENTE=sistema@sena.edu.co
EMAIL_NOMBRE_REMITENTE=Sistema de Laboratorios SENA
EMAIL_USAR_TLS=true
EMAIL_USAR_SSL=false
```

### **Mantenimiento Predictivo**
```bash
DIAS_ANTICIPACION_MANTENIMIENTO=30    # Días antes para alertar
DIAS_ANTICIPACION_CALIBRACION=15     # Días antes para calibración
DIAS_ANTICIPACION_CRITICO=7          # Días antes para crítico
UMBRAL_RIESGO_ALTO=0.7                # Umbral riesgo alto
UMBRAL_RIESGO_MEDIO=0.4               # Umbral riesgo medio
UMBRAL_USO_EXCESIVO=20                # Horas uso excesivo
```

### **Dashboard de Alertas**
```bash
DASHBOARD_CRITICAS_PRIMERO=true        # Mostrar críticas primero
DASHBOARD_MAX_ALERTAS=50               # Máximo alertas mostradas
DASHBOARD_AUTO_ACTUALIZAR=300          # Auto actualizar (segundos)
DASHBOARD_SOLO_NO_LEIDAS=false         # Solo alertas no leídas
DASHBOARD_AGRUPAR_TIPO=true           # Agrupar por tipo
```

---

## 📱 **Configuración SMS (Opcional)**

### **Twilio**
```bash
SMS_PROVEEDOR=twilio
SMS_API_KEY=tu_api_key
SMS_API_SECRET=tu_api_secret
SMS_REMITENTE=+1234567890
SMS_MAX_POR_DIA=100
SMS_SOLO_CRITICAS=true
```

---

## 🌐 **Configuración Webhook (Opcional)**

### **Endpoint Externo**
```bash
WEBHOOK_URLS=https://webhook.ejemplo.com/alertas
WEBHOOK_HEADERS={"Authorization": "Bearer token"}
WEBHOOK_TIMEOUT=30
WEBHOOK_REINTENTOS=3
WEBHOOK_SOLO_CRITICAS=false
```

---

## 🕐 **Configuración de Horarios Laborales**

### **Restricciones de Notificaciones**
```bash
ENVIAR_SOLO_LABORAL=false          # Solo enviar en horario laboral
HORARIO_LABORAL_INICIO=08:00      # Inicio horario laboral
HORARIO_LABORAL_FIN=18:00          # Fin horario laboral
DIAS_LABORALES=lunes,martes,miércoles,jueves,viernes
```

### **Personal de Contacto**
```bash
ADMINISTRADORES=admin@sena.edu.co,coordinador@sena.edu.co
INSTRUCTORES=instructor1@sena.edu.co,instructor2@sena.edu.co
```

---

## 🔧 **Configuración de Monitoreo**

### **Monitoreo de Rendimiento**
```bash
ENABLE_MONITORING=False            # Habilitar monitoreo
MONITORING_URL=                   # URL servicio monitoreo
```

---

## 📋 **Variables por Entorno**

### **Desarrollo (.env)**
```bash
FLASK_ENV=development
FLASK_DEBUG=True
DB_HOST=localhost
LOG_LEVEL=DEBUG
FORCE_HTTPS=False
```

### **Producción (.env_produccion)**
```bash
FLASK_ENV=production
FLASK_DEBUG=False
DB_HOST=tu_ip_servidor
LOG_LEVEL=INFO
FORCE_HTTPS=True
BACKUP_AUTOMATIC=True
```

### **Testing (.env_testing)**
```bash
FLASK_ENV=testing
DB_NAME=laboratorio_test
LOG_LEVEL=DEBUG
SESSION_TIMEOUT=5
```

---

## 🔒 **Mejores Prácticas de Seguridad**

### **1. Generación de Claves**
```bash
# Clave secreta
python -c "import secrets; print(secrets.token_hex(32))"

# Contraseña BD
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

### **2. Permisos de Archivos**
```bash
# Linux/macOS
chmod 600 .env_produccion
chown tu_usuario:tu_grupo .env_produccion

# Windows
# Propiedades → Seguridad → Solo tu usuario
```

### **3. Variables Sensibles**
```bash
# Nunca incluir en Git
.env
.env_produccion
.env_local

# Siempre en .gitignore
*.env
!.env.example
```

### **4. Rotación de Credenciales**
- **🔑 SECRET_KEY:** Cada 6 meses
- **🗄️ DB_PASSWORD:** Cada 3 meses
- **📧 SMTP_PASSWORD:** Cada 6 meses
- **🔐 API Keys:** Cada año

---

## 🚀 **Configuración Rápida**

### **Producción Mínima**
```bash
# Copiar plantilla
cp .env.example .env_produccion

# Configurar esencial
DB_HOST=tu_ip_servidor
DB_USER=laboratorio_prod
DB_PASSWORD=contraseña_segura_123!
DB_NAME=laboratorio_sistema

FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generar_clave_secreta_aqui
APP_URL=https://tu_dominio.com
FORCE_HTTPS=True
```

### **Desarrollo Rápido**
```bash
# Usar valores por defecto
cp .env.example .env
# Editar solo DB_PASSWORD
```

---

## 📞 **Soporte y Troubleshooting**

### **Problemas Comunes**
1. **"SECRET_KEY no configurado"**
   - Solución: Generar con `secrets.token_hex(32)`

2. **"No se puede conectar a BD"**
   - Solución: Verificar `DB_HOST`, `DB_USER`, `DB_PASSWORD`

3. **"Email no funciona"**
   - Solución: Verificar `SMTP_PASSWORD` es App Password

4. **"Logs no se generan"**
   - Solución: Crear directorio `logs/` y verificar permisos

### **Verificación**
```bash
# Verificar configuración
python check_setup.py

# Probar conexión BD
mysql -h $DB_HOST -u $DB_USER -p $DB_NAME

# Probar envío email
python scripts/test_email.py
```

---

## ✅ **Checklist de Configuración**

### **Antes de Ir a Producción**
- [ ] **SECRET_KEY** generado y único
- [ ] **DB_PASSWORD** segura (no "1234")
- [ ] **FORCE_HTTPS** en `True`
- [ ] **FLASK_DEBUG** en `False`
- [ ] **LOG_LEVEL** en `INFO`
- [ ] **BACKUP_AUTOMATIC** configurado
- [ ] **EMAIL** funcionando
- [ ] **Permisos** archivos .env correctos

### **Mantenimiento Mensual**
- [ ] **Revisar logs** de errores
- [ ] **Verificar backups** automáticos
- [ ] **Monitorear espacio** en disco
- [ ] **Actualizar dependencias** si es necesario
- [ ] **Revisar intentos fallidos** de login

---

*Última actualización: 25 de Abril de 2026*
*Versión: 2.0.0 - Production Ready*

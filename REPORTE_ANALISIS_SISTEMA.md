# 📋 Reporte de Análisis del Sistema Web

**Fecha:** 1760818278.20073  
**Sistema:** Centro Minero SENA - Gestión de Laboratorios

---

## 📊 Estadísticas Generales

- **Rutas Flask:** 44
- **Templates HTML:** 28
- **Enlaces totales:** 69

---

## ⚠️  Problemas Encontrados

### 1. Templates sin usar (0)

✅ Todos los templates están en uso

### 2. Templates referenciados pero inexistentes (0)

✅ Todas las referencias son válidas

### 3. Enlaces con problemas (0)

✅ Todos los enlaces son válidos

### 4. Elementos obsoletos (0)

✅ No se encontraron elementos obsoletos

---

## 📁 Lista Completa de Rutas


### /api

- `/api/accesibilidad/toggle` - [POST]
- `/api/get-token` - [GET]
- `/api/reemplazar-imagen` - [POST]
- `/api/registro-actualizar/<tipo>/<id>` - [PUT]
- `/api/registro-completo` - [POST]
- `/api/registro-detalle/<tipo>/<id>` - [GET]
- `/api/registro-editar/<tipo>/<id>` - [GET]
- `/api/registro-eliminar/<tipo>/<id>` - [DELETE]
- `/api/registros-completos` - [GET]

### /ayuda

- `/ayuda` - [GET]

### /backup

- `/backup` - [GET, POST]
- `/backup/download/<filename>` - [GET]

### /configuracion

- `/configuracion` - [GET]

### /dashboard

- `/dashboard` - [GET]

### /entrenamiento-visual

- `/entrenamiento-visual` - [GET]

### /equipos

- `/equipos` - [GET]
- `/equipos/crear` - [POST]

### /imagenes_objeto

- `/imagenes_objeto/<int:imagen_id>` - [GET]

### /inventario

- `/inventario` - [GET]
- `/inventario/crear` - [POST]

### /laboratorio

- `/laboratorio/<int:laboratorio_id>` - [GET]

### /laboratorios

- `/laboratorios` - [GET]

### /login

- `/login` - [GET, POST]

### /login_facial

- `/login_facial` - [POST]

### /logout

- `/logout` - [GET]

### /modulos

- `/modulos` - [GET]

### /notificaciones

- `/notificaciones` - [GET]

### /objetos

- `/objetos/gestion` - [GET]
- `/objetos/registrar` - [GET]

### /perfil

- `/perfil` - [GET, POST]

### /recuperar-contrasena

- `/recuperar-contrasena` - [GET, POST]

### /registro

- `/registro` - [GET, POST]

### /registro-completo

- `/registro-completo` - [GET]

### /registro-facial

- `/registro-facial` - [GET]

### /registros-gestion

- `/registros-gestion` - [GET]

### /reportes

- `/reportes` - [GET]
- `/reportes/descargar/excel` - [GET]
- `/reportes/descargar/pdf` - [GET]

### /reservas

- `/reservas` - [GET]
- `/reservas/crear` - [POST]

### /restablecer-contrasena

- `/restablecer-contrasena/<user_id>` - [GET, POST]

### /root

- `/` - [GET]

### /usuarios

- `/usuarios` - [GET]

### /verificar-codigo

- `/verificar-codigo/<user_id>` - [GET, POST]

---

## 🎯 Recomendaciones

✅ **El sistema está bien estructurado y no requiere limpieza urgente**

---

*Reporte generado automáticamente por test_sistema_completo.py*

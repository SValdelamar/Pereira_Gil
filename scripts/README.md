# 📁 Scripts de Instalación y Configuración

Scripts para configurar y mantener la base de datos del sistema.

## 📄 Archivos

### `setup_database.py` ⭐ Principal

**Propósito:** Instalación inicial completa de la base de datos.

**Uso:**
```bash
python scripts/setup_database.py
```

**Qué hace:**
- Crea la base de datos `laboratorio_sistema`
- Crea todas las tablas con sus relaciones
- Inserta usuario administrador por defecto
- Configura índices y foreign keys

**Cuándo ejecutar:**
- Después de clonar el repositorio (primera vez)
- Para resetear la base de datos completamente

---

### `seed_database.py` 

**Propósito:** Poblar la base de datos con datos de ejemplo para desarrollo.

**Uso:**
```bash
python scripts/seed_database.py
```

**Qué hace:**
- Inserta laboratorios de ejemplo
- Inserta usuarios de prueba
- Inserta equipos de prueba
- Inserta items de inventario
- Inserta reservas de ejemplo

**Cuándo ejecutar:**
- Después de `setup_database.py` (opcional)
- Para tener datos de prueba en desarrollo

---

### `fix_laboratorios.sql`

**Propósito:** Corrección para bases de datos existentes que no tienen todos los campos.

**Uso:**
```bash
mysql -u root -p laboratorio_sistema < scripts/fix_laboratorios.sql
```

**Qué hace:**
- Agrega campos faltantes a la tabla `laboratorios`:
  - `area_m2`
  - `equipamiento_especializado`
  - `normas_seguridad`
  - `fecha_modificacion`

**Cuándo ejecutar:**
- Si ves el error "Unknown column 'fecha_modificacion'"
- Para actualizar bases de datos antiguas

---

## 🔄 Flujo de Instalación Recomendado

### Primera instalación:
```bash
# 1. Crear base de datos
python scripts/setup_database.py

# 2. (Opcional) Agregar datos de ejemplo
python scripts/seed_database.py

# 3. Iniciar servidor
python web_app.py
```

### Actualizar base de datos existente:
```bash
# Si ya tienes datos y solo necesitas los campos nuevos
mysql -u root -p laboratorio_sistema < scripts/fix_laboratorios.sql
```

---

## ⚠️ Notas Importantes

- **`setup_database.py`** usa `CREATE TABLE IF NOT EXISTS`, es seguro ejecutarlo múltiples veces
- **`seed_database.py`** puede duplicar datos si se ejecuta varias veces
- Haz backup antes de ejecutar `fix_laboratorios.sql` en producción:
  ```bash
  mysqldump -u root -p laboratorio_sistema > backup.sql
  ```

---

## 🔐 Credenciales por Defecto

Después de ejecutar `setup_database.py`:
- **Usuario:** admin
- **Contraseña:** admin123

⚠️ **IMPORTANTE:** Cambiar estas credenciales inmediatamente en producción.

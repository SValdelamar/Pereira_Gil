-- =============================================================================
-- MIGRACIÓN 001: Schema Inicial Completo - Sistema de Laboratorios SENA
-- =============================================================================
-- 
-- Descripción: Crea todas las tablas necesarias para el sistema de gestión
--              de laboratorios del Centro Minero SENA.
-- 
-- Buenas Práticas:
-- - IF NOT EXISTS para permitir ejecución múltiple
-- - CHARSET utf8mb4 para soporte completo de Unicode
-- - Índices optimizados para consultas frecuentes
-- - Relaciones con claves foráneas donde aplica
-- 
-- ROLLBACK: DROP TABLE IF EXISTS schema_migrations;
--           DROP TABLE IF EXISTS solicitudes_nivel;
--           DROP TABLE IF EXISTS objetos_imagenes;
--           DROP TABLE IF EXISTS objetos;
--           DROP TABLE IF EXISTS configuracion_sistema;
--           DROP TABLE IF EXISTS logs_seguridad;
--           DROP TABLE IF EXISTS comandos_voz;
--           DROP TABLE IF EXISTS mantenimientos;
--           DROP TABLE IF EXISTS movimientos_inventario;
--           DROP TABLE IF EXISTS historial_uso;
--           DROP TABLE IF EXISTS reservas;
--           DROP TABLE IF EXISTS inventario;
--           DROP TABLE IF EXISTS equipos;
--           DROP TABLE IF EXISTS usuarios;
--           DROP TABLE IF EXISTS laboratorios;
-- =============================================================================

-- Iniciar transacción para asegurar atomicidad
START TRANSACTION;

-- Tabla de control de migraciones (si no existe)
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(255) NOT NULL,
    ejecutada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tiempo_ejecucion_ms INT,
    exito BOOLEAN DEFAULT TRUE,
    checksum VARCHAR(64),
    INDEX idx_version (version),
    INDEX idx_ejecutada_en (ejecutada_en)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA PRINCIPAL: Laboratorios
-- =============================================================================
CREATE TABLE IF NOT EXISTS laboratorios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    tipo ENUM('laboratorio', 'aula', 'taller', 'almacen') NOT NULL DEFAULT 'laboratorio',
    ubicacion VARCHAR(200),
    capacidad INT DEFAULT 0,
    responsable_id VARCHAR(50),
    estado ENUM('activo', 'mantenimiento', 'inactivo') NOT NULL DEFAULT 'activo',
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_estado (estado),
    INDEX idx_responsable (responsable_id),
    INDEX idx_ubicacion (ubicacion(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA PRINCIPAL: Usuarios
-- =============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    password_hash VARCHAR(255),
    tipo ENUM('aprendiz', 'instructor', 'funcionario', 'administrador') NOT NULL DEFAULT 'aprendiz',
    nivel_acceso INT NOT NULL DEFAULT 1,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Campos adicionales para diferentes roles
    a_cargo_inventario BOOLEAN DEFAULT FALSE,
    laboratorio_id INT,
    ficha VARCHAR(50),
    cargo VARCHAR(100),
    dependencia VARCHAR(100),
    programa_formacion VARCHAR(150),
    especialidad VARCHAR(100),
    
    -- Campos para solicitudes de nivel
    nivel_solicitado INT,
    estado_solicitud ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT NULL,
    
    -- Campos para reconocimiento facial
    rostro_data LONGTEXT,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_acceso TIMESTAMP NULL,
    ip_ultimo_acceso VARCHAR(45),
    
    INDEX idx_email (email),
    INDEX idx_tipo (tipo),
    INDEX idx_nivel_acceso (nivel_acceso),
    INDEX idx_activo (activo),
    INDEX idx_laboratorio (laboratorio_id),
    INDEX idx_ficha (ficha),
    INDEX idx_estado_solicitud (estado_solicitud),
    
    FOREIGN KEY (laboratorio_id) REFERENCES laboratorios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Equipos
-- =============================================================================
CREATE TABLE IF NOT EXISTS equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    numero_serie VARCHAR(100),
    estado ENUM('disponible', 'en_uso', 'mantenimiento', 'fuera_servicio') NOT NULL DEFAULT 'disponible',
    ubicacion VARCHAR(200),
    laboratorio_id INT,
    ubicacion_especifica VARCHAR(200),
    
    -- Campos adicionales
    especificaciones JSON,
    fecha_adquisicion DATE,
    ultima_calibracion DATE,
    proxima_calibracion DATE,
    responsable_actual VARCHAR(50),
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_estado (estado),
    INDEX idx_laboratorio (laboratorio_id),
    INDEX idx_responsable (responsable_actual),
    INDEX idx_ubicacion (ubicacion(100)),
    
    FOREIGN KEY (laboratorio_id) REFERENCES laboratorios(id) ON DELETE SET NULL,
    FOREIGN KEY (responsable_actual) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Inventario
-- =============================================================================
CREATE TABLE IF NOT EXISTS inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    cantidad_actual INT NOT NULL DEFAULT 0,
    cantidad_minima INT NOT NULL DEFAULT 1,
    unidad VARCHAR(50) DEFAULT 'unidad',
    ubicacion VARCHAR(200),
    laboratorio_id INT,
    ubicacion_especifica VARCHAR(200),
    
    -- Campos de proveedor
    proveedor VARCHAR(150),
    costo_unitario DECIMAL(10,2),
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_codigo (codigo),
    INDEX idx_categoria (categoria),
    INDEX idx_ubicacion (ubicacion(100)),
    INDEX idx_laboratorio (laboratorio_id),
    INDEX idx_cantidad_actual (cantidad_actual),
    INDEX idx_stock_critico (cantidad_actual, cantidad_minima),
    
    FOREIGN KEY (laboratorio_id) REFERENCES laboratorios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Reservas
-- =============================================================================
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT NOT NULL,
    usuario_id VARCHAR(50) NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    proposito TEXT NOT NULL,
    estado ENUM('pendiente', 'aprobada', 'rechazada', 'completada', 'cancelada') NOT NULL DEFAULT 'pendiente',
    
    -- Campos de aprobación
    aprobada_por VARCHAR(50),
    fecha_aprobacion DATETIME,
    motivo_rechazo TEXT,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_equipo (equipo_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_inicio (fecha_inicio),
    INDEX idx_fecha_fin (fecha_fin),
    INDEX idx_aprobada_por (aprobada_por),
    
    FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (aprobada_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Historial de Uso
-- =============================================================================
CREATE TABLE IF NOT EXISTS historial_uso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT NOT NULL,
    usuario_id VARCHAR(50) NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    estado ENUM('en_curso', 'completado', 'cancelado') NOT NULL DEFAULT 'en_curso',
    observaciones TEXT,
    
    INDEX idx_equipo (equipo_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_fecha_inicio (fecha_inicio),
    INDEX idx_estado (estado),
    
    FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Movimientos de Inventario
-- =============================================================================
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    usuario_id VARCHAR(50) NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste', 'merma') NOT NULL,
    cantidad INT NOT NULL,
    cantidad_anterior INT NOT NULL,
    cantidad_nueva INT NOT NULL,
    motivo VARCHAR(200),
    observaciones TEXT,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_item (item_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_tipo (tipo_movimiento),
    INDEX idx_fecha (fecha_movimiento),
    
    FOREIGN KEY (item_id) REFERENCES inventario(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Mantenimientos
-- =============================================================================
CREATE TABLE IF NOT EXISTS mantenimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT NOT NULL,
    tipo ENUM('preventivo', 'correctivo', 'calibracion') NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_programada DATE NOT NULL,
    fecha_realizada DATE,
    estado ENUM('pendiente', 'en_curso', 'completado', 'cancelado') NOT NULL DEFAULT 'pendiente',
    realizado_por VARCHAR(50),
    costo DECIMAL(10,2),
    observaciones TEXT,
    
    INDEX idx_equipo (equipo_id),
    INDEX idx_tipo (tipo),
    INDEX idx_estado (estado),
    INDEX idx_fecha_programada (fecha_programada),
    INDEX idx_realizado_por (realizado_por),
    
    FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
    FOREIGN KEY (realizado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Comandos de Voz
-- =============================================================================
CREATE TABLE IF NOT EXISTS comandos_voz (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(50) NOT NULL,
    comando VARCHAR(500) NOT NULL,
    respuesta TEXT,
    exito BOOLEAN DEFAULT FALSE,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_origen VARCHAR(45),
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_fecha (fecha_ejecucion),
    INDEX idx_exito (exito),
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Logs de Seguridad
-- =============================================================================
CREATE TABLE IF NOT EXISTS logs_seguridad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(50),
    accion VARCHAR(100) NOT NULL,
    detalle TEXT,
    ip_origen VARCHAR(45),
    user_agent TEXT,
    exito BOOLEAN DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_accion (accion),
    INDEX idx_fecha (fecha_registro),
    INDEX idx_exito (exito),
    INDEX idx_ip (ip_origen),
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Configuración del Sistema
-- =============================================================================
CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT,
    descripcion TEXT,
    tipo ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    editable BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_clave (clave),
    INDEX idx_editable (editable)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Objetos (IA Visual)
-- =============================================================================
CREATE TABLE IF NOT EXISTS objetos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo ENUM('equipo', 'item') NOT NULL,
    equipo_id VARCHAR(50),
    item_id VARCHAR(50),
    descripcion TEXT,
    caracteristicas JSON,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_nombre (nombre),
    INDEX idx_tipo (tipo),
    INDEX idx_equipo_id (equipo_id),
    INDEX idx_item_id (item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Imágenes de Objetos (IA Visual)
-- =============================================================================
CREATE TABLE IF NOT EXISTS objetos_imagenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    objeto_id INT NOT NULL,
    ruta_imagen VARCHAR(500) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tamaño_bytes INT,
    dimensiones VARCHAR(50),
    caracteristicas JSON,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_objeto (objeto_id),
    INDEX idx_fecha_carga (fecha_carga),
    
    FOREIGN KEY (objeto_id) REFERENCES objetos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLA: Solicitudes de Nivel
-- =============================================================================
CREATE TABLE IF NOT EXISTS solicitudes_nivel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(50) NOT NULL,
    nivel_actual INT NOT NULL,
    nivel_solicitado INT NOT NULL,
    motivo TEXT,
    estado ENUM('pendiente', 'aprobada', 'rechazada') NOT NULL DEFAULT 'pendiente',
    revisado_por VARCHAR(50),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_revision TIMESTAMP NULL,
    comentarios_revision TEXT,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_solicitud (fecha_solicitud),
    INDEX idx_revisado_por (revisado_por),
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (revisado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- INSERCIÓN DE DATOS INICIALES
-- =============================================================================

-- Insertar configuración básica del sistema
INSERT IGNORE INTO configuracion_sistema (clave, valor, descripcion, tipo) VALUES
('sistema_nombre', 'Sistema de Gestión de Laboratorios', 'Nombre del sistema', 'string'),
('sistema_version', '1.0.0', 'Versión actual del sistema', 'string'),
('reservas_max_dias', '7', 'Máximo de días para reservar equipos', 'number'),
('reservas_max_horas', '4', 'Máximo de horas por reserva', 'number'),
('inventario_alerta_stock', '1', 'Días antes de vencimiento para alertar stock', 'number'),
('backup_automatico', 'true', 'Activar backup automático diario', 'boolean'),
('login_intentos_max', '3', 'Máximo de intentos fallidos de login', 'number'),
('sesion_timeout', '30', 'Timeout de sesión en minutos', 'number');

-- Insertar usuario administrador por defecto (si no existe)
INSERT IGNORE INTO usuarios (
    id, nombre, email, password_hash, tipo, nivel_acceso, activo, a_cargo_inventario
) VALUES (
    'admin', 
    'Administrador del Sistema', 
    'admin@sena.edu.co', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9w5GS', -- password: admin123
    'administrador', 
    6, 
    TRUE,
    TRUE
);

-- =============================================================================
-- REGISTRO DE MIGRACIÓN
-- =============================================================================

-- Registrar esta migración como ejecutada
INSERT IGNORE INTO schema_migrations (version, nombre, exito) 
VALUES ('001', 'Schema Inicial Completo - Sistema de Laboratorios SENA', TRUE);

-- Confirmar transacción
COMMIT;

-- =============================================================================
-- VERIFICACIÓN POST-MIGRACIÓN
-- =============================================================================

-- Mostrar resumen de tablas creadas
SELECT 
    TABLE_NAME as 'Tabla Creada',
    TABLE_ROWS as 'Filas Iniciales',
    ROUND(DATA_LENGTH/1024/1024, 2) as 'Tamaño (MB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME IN (
        'laboratorios', 'usuarios', 'equipos', 'inventario', 'reservas',
        'historial_uso', 'movimientos_inventario', 'mantenimientos',
        'comandos_voz', 'logs_seguridad', 'configuracion_sistema',
        'objetos', 'objetos_imagenes', 'solicitudes_nivel', 'schema_migrations'
    )
ORDER BY TABLE_NAME;

-- Confirmar que todas las tablas tienen la estructura correcta
SELECT 'MIGRACIÓN 001 COMPLETADA EXITOSAMENTE' as status,
       COUNT(*) as total_tablas_creadas
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME IN (
        'laboratorios', 'usuarios', 'equipos', 'inventario', 'reservas',
        'historial_uso', 'movimientos_inventario', 'mantenimientos',
        'comandos_voz', 'logs_seguridad', 'configuracion_sistema',
        'objetos', 'objetos_imagenes', 'solicitudes_nivel', 'schema_migrations'
    );

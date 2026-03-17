-- =====================================================================
-- CORRECCIÓN DE TABLA laboratorios
-- Agregar campos faltantes que web_app.py usa
-- =====================================================================

USE laboratorio_sistema;

-- Verificar y agregar campos si no existen
-- MySQL no soporta IF NOT EXISTS en ALTER TABLE, por eso usamos este enfoque

-- Agregar campo area_m2
SET @dbname = 'laboratorio_sistema';
SET @tablename = 'laboratorios';
SET @columnname = 'area_m2';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_schema = @dbname AND table_name = @tablename AND column_name = @columnname) > 0,
  'SELECT 1',
  'ALTER TABLE laboratorios ADD COLUMN area_m2 DECIMAL(10,2) AFTER capacidad_estudiantes'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar campo equipamiento_especializado
SET @columnname = 'equipamiento_especializado';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_schema = @dbname AND table_name = @tablename AND column_name = @columnname) > 0,
  'SELECT 1',
  'ALTER TABLE laboratorios ADD COLUMN equipamiento_especializado TEXT AFTER responsable'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar campo normas_seguridad
SET @columnname = 'normas_seguridad';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_schema = @dbname AND table_name = @tablename AND column_name = @columnname) > 0,
  'SELECT 1',
  'ALTER TABLE laboratorios ADD COLUMN normas_seguridad TEXT AFTER equipamiento_especializado'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar campo fecha_modificacion
SET @columnname = 'fecha_modificacion';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_schema = @dbname AND table_name = @tablename AND column_name = @columnname) > 0,
  'SELECT 1',
  'ALTER TABLE laboratorios ADD COLUMN fecha_modificacion DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP AFTER fecha_creacion'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Crear tabla logs_sistema si no existe
CREATE TABLE IF NOT EXISTS logs_sistema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(50),
    accion VARCHAR(100) NOT NULL,
    detalles TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_origen VARCHAR(45),
    
    INDEX idx_fecha (fecha),
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_accion (accion),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Agregar campo fecha a logs_seguridad si no existe
SET @columnname = 'fecha';
SET @tablename = 'logs_seguridad';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_schema = @dbname AND table_name = @tablename AND column_name = @columnname) > 0,
  'SELECT 1',
  'ALTER TABLE logs_seguridad ADD COLUMN fecha DATETIME DEFAULT CURRENT_TIMESTAMP'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Agregar campo timestamp a logs_seguridad si no existe
SET @columnname = 'timestamp';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_schema = @dbname AND table_name = @tablename AND column_name = @columnname) > 0,
  'SELECT 1',
  'ALTER TABLE logs_seguridad ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Crear tabla solicitudes_nivel si no existe
CREATE TABLE IF NOT EXISTS solicitudes_nivel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(50) NOT NULL,
    nivel_solicitado INT NOT NULL,
    nivel_actual INT NOT NULL,
    estado ENUM('pendiente','aprobada','rechazada') DEFAULT 'pendiente',
    fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta DATETIME,
    admin_revisor VARCHAR(50),
    comentario_admin TEXT,
    
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_solicitud (fecha_solicitud),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_revisor) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Todas las correcciones aplicadas correctamente' AS resultado;

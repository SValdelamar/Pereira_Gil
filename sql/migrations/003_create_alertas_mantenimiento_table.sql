-- Migración 003: Crear tabla de alertas de mantenimiento
-- Sistema de Gestión Inteligente - Centro Minero SENA
-- 
-- Esta migración crea la tabla para el sistema de alertas automáticas
-- de mantenimiento predictivo y notificaciones

-- ROLLBACK: DROP TABLE alertas_mantenimiento;

CREATE TABLE IF NOT EXISTS alertas_mantenimiento (
    id VARCHAR(100) PRIMARY KEY,
    tipo ENUM('mantenimiento_proximo', 'mantenimiento_vencido', 'equipo_critico', 
             'calibracion_vencida', 'tendencia_fallas', 'uso_excesivo') NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    equipo_id VARCHAR(50) NOT NULL,
    equipo_nombre VARCHAR(100) NOT NULL,
    laboratorio_id INT NOT NULL,
    laboratorio_nombre VARCHAR(100) NOT NULL,
    fecha_alerta DATETIME NOT NULL,
    fecha_mantenimiento DATETIME NOT NULL,
    riesgo ENUM('bajo', 'medio', 'alto', 'critico') NOT NULL,
    prioridad INT NOT NULL,
    canales JSON NOT NULL,
    destinatarios JSON NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_lectura DATETIME NULL,
    
    -- Índices para optimización de consultas
    INDEX idx_fecha_alerta (fecha_alerta),
    INDEX idx_prioridad (prioridad),
    INDEX idx_laboratorio_id (laboratorio_id),
    INDEX idx_leida (leida),
    INDEX idx_equipo_id (equipo_id),
    INDEX idx_tipo (tipo),
    INDEX idx_riesgo (riesgo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registrar migración
INSERT INTO schema_migrations (version, nombre, ejecutada_en, exito) 
VALUES ('003', 'Crear tabla alertas_mantenimiento', NOW(), TRUE)
ON DUPLICATE KEY UPDATE 
nombre = VALUES(nombre), 
ejecutada_en = VALUES(ejecutada_en), 
exito = VALUES(exito);

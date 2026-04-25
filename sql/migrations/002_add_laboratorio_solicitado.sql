-- Migración: Agregar campo laboratorio_solicitado a solicitudes_nivel
-- Versión: 002
-- Descripción: Permitir que los usuarios soliciten laboratorio específico al registrarse como instructor de inventario

-- Agregar campo laboratorio_solicitado
ALTER TABLE solicitudes_nivel 
ADD COLUMN laboratorio_solicitado INT NULL 
AFTER comentario_admin;

-- Agregar índice para mejor rendimiento
CREATE INDEX idx_solicitudes_laboratorio_solicitado 
ON solicitudes_nivel(laboratorio_solicitado);

-- Agregar comentario descriptivo
ALTER TABLE solicitudes_nivel 
MODIFY COLUMN laboratorio_solicitado INT NULL 
COMMENT 'ID del laboratorio solicitado por el usuario (solo para instructor de inventario)';

-- Registrar migración
INSERT INTO schema_migrations (version, nombre, ejecutada_en, exito) 
VALUES ('002', 'Agregar campo laboratorio_solicitado a solicitudes_nivel', NOW(), TRUE);

-- ROLLBACK: ALTER TABLE solicitudes_nivel DROP COLUMN laboratorio_solicitado;

# -*- coding: utf-8 -*-
"""
Sistema de Alertas Automáticas de Mantenimiento
Sistema de Gestión Inteligente - Centro Minero SENA

Implementación de notificaciones automáticas para mantenimientos predictivos
con múltiples canales de comunicación.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoAlerta(Enum):
    """Tipos de alertas del sistema"""
    MANTENIMIENTO_PROXIMO = "mantenimiento_proximo"
    MANTENIMIENTO_VENCIDO = "mantenimiento_vencido"
    EQUIPO_CRITICO = "equipo_critico"
    CALIBRACION_VENCIDA = "calibracion_vencida"
    TENDENCIA_FALAS = "tendencia_fallas"
    USO_EXCESIVO = "uso_excesivo"

class CanalNotificacion(Enum):
    """Canales de notificación disponibles"""
    EMAIL = "email"
    DASHBOARD = "dashboard"
    SISTEMA = "sistema"
    SMS = "sms"  # Futuro

@dataclass
class Alerta:
    """Estructura de una alerta"""
    id: str
    tipo: TipoAlerta
    titulo: str
    mensaje: str
    equipo_id: str
    equipo_nombre: str
    laboratorio_id: int
    laboratorio_nombre: str
    fecha_alerta: datetime
    fecha_mantenimiento: datetime
    riesgo: str
    prioridad: int  # 1 = máxima, 5 = mínima
    canales: List[CanalNotificacion]
    destinatarios: List[str]
    leida: bool = False
    fecha_lectura: Optional[datetime] = None

@dataclass
class ConfiguracionAlerta:
    """Configuración del sistema de alertas"""
    dias_anticipacion_mantenimiento: int = 30
    dias_anticipacion_calibracion: int = 15
    habilitar_email: bool = True
    habilitar_dashboard: bool = True
    email_remitente: str = "sistema@sena.edu.co"
    email_servidor: str = "smtp.gmail.com"
    email_puerto: int = 587
    email_usuario: str = ""
    email_password: str = ""
    hora_envio_diario: str = "08:00"
    frecuencia_revision: int = 24  # horas

class MaintenanceAlertManager:
    """
    Gestor de alertas automáticas de mantenimiento
    """
    
    def __init__(self, db_manager, maintenance_predictor, configuracion: Optional[ConfiguracionAlerta] = None):
        self.db_manager = db_manager
        self.predictor = maintenance_predictor
        self.config = configuracion or ConfiguracionAlerta()
        self.alertas_cache = {}
        
        logger.info("🔔 Sistema de Alertas de Mantenimiento inicializado")
    
    def generar_alertas_automaticas(self) -> List[Alerta]:
        """
        Generar todas las alertas automáticas del sistema
        
        Returns:
            Lista de alertas generadas
        """
        try:
            alertas = []
            
            # 1. Alertas de mantenimientos próximos
            alertas.extend(self._generar_alertas_mantenimientos_proximos())
            
            # 2. Alertas de mantenimientos vencidos
            alertas.extend(self._generar_alertas_mantenimientos_vencidos())
            
            # 3. Alertas de calibraciones vencidas
            alertas.extend(self._generar_alertas_calibraciones_vencidas())
            
            # 4. Alertas de equipos críticos
            alertas.extend(self._generar_alertas_equipos_criticos())
            
            # 5. Alertas de uso excesivo
            alertas.extend(self._generar_alertas_uso_excesivo())
            
            # 6. Alertas de tendencias de fallas
            alertas.extend(self._generar_alertas_tendencias_fallas())
            
            # Guardar alertas en base de datos
            self._guardar_alertas(alertas)
            
            logger.info(f"🔔 Se generaron {len(alertas)} alertas automáticas")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas automáticas: {e}")
            return []
    
    def obtener_alertas_usuario(self, usuario_id: str, solo_no_leidas: bool = False) -> List[Alerta]:
        """
        Obtener alertas para un usuario específico
        
        Args:
            usuario_id: ID del usuario
            solo_no_leidas: Si solo retornar alertas no leídas
            
        Returns:
            Lista de alertas del usuario
        """
        try:
            # Obtener laboratorios del usuario
            laboratorios = self._obtener_laboratorios_usuario(usuario_id)
            
            if not laboratorios:
                return []
            
            # Construir consulta
            lab_ids = [str(lab['id']) for lab in laboratorios]
            query = """
                SELECT id, tipo, titulo, mensaje, equipo_id, equipo_nombre,
                       laboratorio_id, laboratorio_nombre, fecha_alerta,
                       fecha_mantenimiento, riesgo, prioridad, canales,
                       destinatarios, leida, fecha_lectura
                FROM alertas_mantenimiento
                WHERE laboratorio_id IN ({})
                ORDER BY prioridad ASC, fecha_alerta DESC
            """.format(','.join(['%s'] * len(lab_ids)))
            
            params = lab_ids
            if solo_no_leidas:
                query += " AND leida = FALSE"
            
            result = self.db_manager.execute_query(query, params)
            
            alertas = []
            for row in result or []:
                alerta = Alerta(
                    id=row['id'],
                    tipo=TipoAlerta(row['tipo']),
                    titulo=row['titulo'],
                    mensaje=row['mensaje'],
                    equipo_id=row['equipo_id'],
                    equipo_nombre=row['equipo_nombre'],
                    laboratorio_id=row['laboratorio_id'],
                    laboratorio_nombre=row['laboratorio_nombre'],
                    fecha_alerta=row['fecha_alerta'],
                    fecha_mantenimiento=row['fecha_mantenimiento'],
                    riesgo=row['riesgo'],
                    prioridad=row['prioridad'],
                    canales=[CanalNotificacion(c) for c in json.loads(row['canales'])],
                    destinatarios=json.loads(row['destinatarios']),
                    leida=row['leida'],
                    fecha_lectura=row['fecha_lectura']
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo alertas usuario {usuario_id}: {e}")
            return []
    
    def marcar_alerta_leida(self, alerta_id: str, usuario_id: str) -> bool:
        """
        Marcar una alerta como leída
        
        Args:
            alerta_id: ID de la alerta
            usuario_id: ID del usuario que la marca como leída
            
        Returns:
            True si se marcó correctamente
        """
        try:
            query = """
                UPDATE alertas_mantenimiento 
                SET leida = TRUE, fecha_lectura = NOW()
                WHERE id = %s
            """
            affected = self.db_manager.execute_query(query, (alerta_id,))
            
            if affected:
                logger.info(f"✅ Alerta {alerta_id} marcada como leída por {usuario_id}")
                return True
            else:
                logger.warning(f"⚠️ Alerta {alerta_id} no encontrada")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marcando alerta como leída: {e}")
            return False
    
    def enviar_alertas_email(self, alertas: List[Alerta]) -> Dict[str, bool]:
        """
        Enviar alertas por email
        
        Args:
            alertas: Lista de alertas a enviar
            
        Returns:
            Diccionario con resultados por alerta_id
        """
        if not self.config.habilitar_email:
            logger.warning("⚠️ Envío de email deshabilitado")
            return {}
        
        resultados = {}
        
        for alerta in alertas:
            if CanalNotificacion.EMAIL not in alerta.canales:
                continue
            
            try:
                # Preparar email
                asunto = f"[ALERTA MANTENIMIENTO] {alerta.titulo}"
                cuerpo_html = self._generar_html_alerta(alerta)
                cuerpo_texto = self._generar_texto_alerta(alerta)
                
                # Enviar email
                exito = self._enviar_email(
                    destinatarios=alerta.destinatarios,
                    asunto=asunto,
                    cuerpo_html=cuerpo_html,
                    cuerpo_texto=cuerpo_texto
                )
                
                resultados[alerta.id] = exito
                
                if exito:
                    logger.info(f"✅ Email enviado para alerta {alerta.id}")
                else:
                    logger.error(f"❌ Error enviando email para alerta {alerta.id}")
                    
            except Exception as e:
                logger.error(f"❌ Error procesando email alerta {alerta.id}: {e}")
                resultados[alerta.id] = False
        
        return resultados
    
    def _generar_alertas_mantenimientos_proximos(self) -> List[Alerta]:
        """Generar alertas para mantenimientos próximos"""
        try:
            # Obtener mantenimientos próximos
            mantenimientos = self._obtener_mantenimientos_proximos(
                self.config.dias_anticipacion_mantenimiento
            )
            
            alertas = []
            for mant in mantenimientos:
                dias_restantes = (mant['fecha_mantenimiento'] - datetime.now()).days
                
                # Determinar prioridad según días restantes
                if dias_restantes <= 7:
                    prioridad = 1
                    riesgo = "crítico"
                elif dias_restantes <= 15:
                    prioridad = 2
                    riesgo = "alto"
                elif dias_restantes <= 30:
                    prioridad = 3
                    riesgo = "medio"
                else:
                    prioridad = 4
                    riesgo = "bajo"
                
                alerta = Alerta(
                    id=f"mant_prox_{mant['equipo_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tipo=TipoAlerta.MANTENIMIENTO_PROXIMO,
                    titulo=f"Mantenimiento Próximo - {mant['equipo_nombre']}",
                    mensaje=f"El equipo {mant['equipo_nombre']} requiere mantenimiento en {dias_restantes} días. Fecha programada: {mant['fecha_mantenimiento'].strftime('%d/%m/%Y')}.",
                    equipo_id=mant['equipo_id'],
                    equipo_nombre=mant['equipo_nombre'],
                    laboratorio_id=mant['laboratorio_id'],
                    laboratorio_nombre=mant['laboratorio_nombre'],
                    fecha_alerta=datetime.now(),
                    fecha_mantenimiento=mant['fecha_mantenimiento'],
                    riesgo=riesgo,
                    prioridad=prioridad,
                    canales=[CanalNotificacion.DASHBOARD, CanalNotificacion.EMAIL],
                    destinatarios=self._obtener_destinatarios_laboratorio(mant['laboratorio_id'])
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas mantenimientos próximos: {e}")
            return []
    
    def _generar_alertas_mantenimientos_vencidos(self) -> List[Alerta]:
        """Generar alertas para mantenimientos vencidos"""
        try:
            mantenimientos = self._obtener_mantenimientos_vencidos()
            
            alertas = []
            for mant in mantenimientos:
                dias_vencido = (datetime.now() - mant['fecha_mantenimiento']).days
                
                alerta = Alerta(
                    id=f"mant_ven_{mant['equipo_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tipo=TipoAlerta.MANTENIMIENTO_VENCIDO,
                    titulo=f"MANTENIMIENTO VENCIDO - {mant['equipo_nombre']}",
                    mensaje=f"⚠️ MANTENIMIENTO VENCIDO. El equipo {mant['equipo_nombre']} tenía mantenimiento programado para hace {dias_vencido} días. Fecha programada: {mant['fecha_mantenimiento'].strftime('%d/%m/%Y')}.",
                    equipo_id=mant['equipo_id'],
                    equipo_nombre=mant['equipo_nombre'],
                    laboratorio_id=mant['laboratorio_id'],
                    laboratorio_nombre=mant['laboratorio_nombre'],
                    fecha_alerta=datetime.now(),
                    fecha_mantenimiento=mant['fecha_mantenimiento'],
                    riesgo="crítico",
                    prioridad=1,
                    canales=[CanalNotificacion.DASHBOARD, CanalNotificacion.EMAIL],
                    destinatarios=self._obtener_destinatarios_laboratorio(mant['laboratorio_id'])
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas mantenimientos vencidos: {e}")
            return []
    
    def _generar_alertas_calibraciones_vencidas(self) -> List[Alerta]:
        """Generar alertas para calibraciones vencidas o próximas"""
        try:
            calibraciones = self._obtener_calibraciones_proximas_vencidas()
            
            alertas = []
            for cal in calibraciones:
                if cal['dias_hasta'] < 0:
                    # Vencida
                    tipo = TipoAlerta.CALIBRACION_VENCIDA
                    titulo = f"CALIBRACIÓN VENCIDA - {cal['equipo_nombre']}"
                    mensaje = f"⚠️ CALIBRACIÓN VENCIDA. El equipo {cal['equipo_nombre']} requiere calibración urgente. Última calibración: {cal['ultima_calibracion'].strftime('%d/%m/%Y')}."
                    riesgo = "crítico"
                    prioridad = 1
                else:
                    # Próxima
                    tipo = TipoAlerta.CALIBRACION_VENCIDA
                    titulo = f"Calibración Próxima - {cal['equipo_nombre']}"
                    mensaje = f"El equipo {cal['equipo_nombre']} requiere calibración en {cal['dias_hasta']} días. Última calibración: {cal['ultima_calibracion'].strftime('%d/%m/%Y')}."
                    riesgo = "alto" if cal['dias_hasta'] <= 7 else "medio"
                    prioridad = 2 if cal['dias_hasta'] <= 7 else 3
                
                alerta = Alerta(
                    id=f"cal_{cal['equipo_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tipo=tipo,
                    titulo=titulo,
                    mensaje=mensaje,
                    equipo_id=cal['equipo_id'],
                    equipo_nombre=cal['equipo_nombre'],
                    laboratorio_id=cal['laboratorio_id'],
                    laboratorio_nombre=cal['laboratorio_nombre'],
                    fecha_alerta=datetime.now(),
                    fecha_mantenimiento=cal['ultima_calibracion'],
                    riesgo=riesgo,
                    prioridad=prioridad,
                    canales=[CanalNotificacion.DASHBOARD, CanalNotificacion.EMAIL],
                    destinatarios=self._obtener_destinatarios_laboratorio(cal['laboratorio_id'])
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas calibraciones: {e}")
            return []
    
    def _generar_alertas_equipos_criticos(self) -> List[Alerta]:
        """Generar alertas para equipos en estado crítico"""
        try:
            equipos_criticos = self._obtener_equipos_criticos()
            
            alertas = []
            for equipo in equipos_criticos:
                alerta = Alerta(
                    id=f"crit_{equipo['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tipo=TipoAlerta.EQUIPO_CRITICO,
                    titulo=f"Equipo en Estado Crítico - {equipo['nombre']}",
                    mensaje=f"⚠️ El equipo {equipo['nombre']} se encuentra en estado '{equipo['estado']}' y requiere atención inmediata.",
                    equipo_id=equipo['id'],
                    equipo_nombre=equipo['nombre'],
                    laboratorio_id=equipo['laboratorio_id'],
                    laboratorio_nombre=equipo['laboratorio_nombre'],
                    fecha_alerta=datetime.now(),
                    fecha_mantenimiento=datetime.now(),
                    riesgo="crítico",
                    prioridad=1,
                    canales=[CanalNotificacion.DASHBOARD, CanalNotificacion.EMAIL],
                    destinatarios=self._obtener_destinatarios_laboratorio(equipo['laboratorio_id'])
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas equipos críticos: {e}")
            return []
    
    def _generar_alertas_uso_excesivo(self) -> List[Alerta]:
        """Generar alertas para equipos con uso excesivo"""
        try:
            equipos_uso_excesivo = self._obtener_equipos_uso_excesivo()
            
            alertas = []
            for equipo in equipos_uso_excesivo:
                alerta = Alerta(
                    id=f"uso_{equipo['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tipo=TipoAlerta.USO_EXCESIVO,
                    titulo=f"Uso Excesivo - {equipo['nombre']}",
                    mensaje=f"El equipo {equipo['nombre']} ha registrado {equipo['horas_semana']:.1f} horas de uso en la última semana, lo que puede indicar sobrecarga.",
                    equipo_id=equipo['id'],
                    equipo_nombre=equipo['nombre'],
                    laboratorio_id=equipo['laboratorio_id'],
                    laboratorio_nombre=equipo['laboratorio_nombre'],
                    fecha_alerta=datetime.now(),
                    fecha_mantenimiento=datetime.now(),
                    riesgo="medio",
                    prioridad=3,
                    canales=[CanalNotificacion.DASHBOARD],
                    destinatarios=self._obtener_destinatarios_laboratorio(equipo['laboratorio_id'])
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas uso excesivo: {e}")
            return []
    
    def _generar_alertas_tendencias_fallas(self) -> List[Alerta]:
        """Generar alertas para equipos con tendencias de fallas preocupantes"""
        try:
            equipos_tendencia = self._obtener_equipos_tendencia_fallas()
            
            alertas = []
            for equipo in equipos_tendencia:
                alerta = Alerta(
                    id=f"tend_{equipo['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tipo=TipoAlerta.TENDENCIA_FALAS,
                    titulo=f"Tendencia de Fallas - {equipo['nombre']}",
                    mensaje=f"El equipo {equipo['nombre']} muestra una tendencia de fallas '{equipo['tendencia']}' en los últimos 3 meses. Se recomienda inspección.",
                    equipo_id=equipo['id'],
                    equipo_nombre=equipo['nombre'],
                    laboratorio_id=equipo['laboratorio_id'],
                    laboratorio_nombre=equipo['laboratorio_nombre'],
                    fecha_alerta=datetime.now(),
                    fecha_mantenimiento=datetime.now(),
                    riesgo="alto",
                    prioridad=2,
                    canales=[CanalNotificacion.DASHBOARD],
                    destinatarios=self._obtener_destinatarios_laboratorio(equipo['laboratorio_id'])
                )
                alertas.append(alerta)
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error generando alertas tendencias fallas: {e}")
            return []
    
    def _obtener_mantenimientos_proximos(self, dias: int) -> List[Dict]:
        """Obtener mantenimientos próximos en N días"""
        try:
            query = """
                SELECT e.id as equipo_id, e.nombre as equipo_nombre, 
                       e.laboratorio_id, l.nombre as laboratorio_nombre,
                       m.fecha_mantenimiento
                FROM equipos e
                INNER JOIN laboratorios l ON e.laboratorio_id = l.id
                LEFT JOIN mantenimientos m ON e.id = m.equipo_id 
                    AND m.tipo_mantenimiento = 'preventivo'
                    AND m.estado = 'programado'
                WHERE (e.proximo_mantenimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                       OR m.fecha_mantenimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY))
                ORDER BY m.fecha_mantenimiento ASC
            """
            return self.db_manager.execute_query(query, (dias, dias)) or []
        except Exception as e:
            logger.error(f"Error obteniendo mantenimientos próximos: {e}")
            return []
    
    def _obtener_mantenimientos_vencidos(self) -> List[Dict]:
        """Obtener mantenimientos vencidos"""
        try:
            query = """
                SELECT e.id as equipo_id, e.nombre as equipo_nombre,
                       e.laboratorio_id, l.nombre as laboratorio_nombre,
                       COALESCE(m.fecha_mantenimiento, e.proximo_mantenimiento) as fecha_mantenimiento
                FROM equipos e
                INNER JOIN laboratorios l ON e.laboratorio_id = l.id
                LEFT JOIN mantenimientos m ON e.id = m.equipo_id 
                    AND m.tipo_mantenimiento = 'preventivo'
                    AND m.estado = 'programado'
                WHERE COALESCE(m.fecha_mantenimiento, e.proximo_mantenimiento) < CURDATE()
                ORDER BY fecha_mantenimiento ASC
            """
            return self.db_manager.execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo mantenimientos vencidos: {e}")
            return []
    
    def _obtener_calibraciones_proximas_vencidas(self) -> List[Dict]:
        """Obtener calibraciones próximas a vencer o vencidas"""
        try:
            query = """
                SELECT e.id as equipo_id, e.nombre as equipo_nombre,
                       e.laboratorio_id, l.nombre as laboratorio_nombre,
                       e.ultima_calibracion,
                       DATEDIFF(e.ultima_calibracion, CURDATE()) as dias_hasta
                FROM equipos e
                INNER JOIN laboratorios l ON e.laboratorio_id = l.id
                WHERE e.ultima_calibracion IS NOT NULL
                  AND e.ultima_calibracion <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
                ORDER BY e.ultima_calibracion ASC
            """
            return self.db_manager.execute_query(query, (self.config.dias_anticipacion_calibracion,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo calibraciones: {e}")
            return []
    
    def _obtener_equipos_criticos(self) -> List[Dict]:
        """Obtener equipos en estado crítico"""
        try:
            query = """
                SELECT e.id, e.nombre, e.estado, e.laboratorio_id, l.nombre as laboratorio_nombre
                FROM equipos e
                INNER JOIN laboratorios l ON e.laboratorio_id = l.id
                WHERE e.estado IN ('mantenimiento', 'fuera_servicio')
                ORDER BY e.estado DESC, e.nombre
            """
            return self.db_manager.execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo equipos críticos: {e}")
            return []
    
    def _obtener_equipos_uso_excesivo(self) -> List[Dict]:
        """Obtener equipos con uso excesivo (más de 20 horas/semana)"""
        try:
            query = """
                SELECT e.id, e.nombre, e.laboratorio_id, l.nombre as laboratorio_nombre,
                       SUM(h.duracion_minutos) / 60 as horas_semana
                FROM equipos e
                INNER JOIN laboratorios l ON e.laboratorio_id = l.id
                LEFT JOIN historial_uso h ON e.id = h.equipo_id
                    AND h.fecha_uso >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY e.id, e.nombre, e.laboratorio_id, l.nombre
                HAVING horas_semana > 20
                ORDER BY horas_semana DESC
            """
            return self.db_manager.execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo equipos uso excesivo: {e}")
            return []
    
    def _obtener_equipos_tendencia_fallas(self) -> List[Dict]:
        """Obtener equipos con tendencias de fallas preocupantes"""
        try:
            # Esta es una implementación simplificada
            # En un sistema real, se usaría análisis estadístico más complejo
            query = """
                SELECT e.id, e.nombre, e.laboratorio_id, l.nombre as laboratorio_nombre,
                       CASE 
                           WHEN COUNT(CASE WHEN m.tipo_mantenimiento = 'correctivo' THEN 1 END) > 2 
                           THEN 'empeorando'
                           ELSE 'estable'
                       END as tendencia
                FROM equipos e
                INNER JOIN laboratorios l ON e.laboratorio_id = l.id
                LEFT JOIN mantenimientos m ON e.id = m.equipo_id
                    AND m.fecha_mantenimiento >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
                GROUP BY e.id, e.nombre, e.laboratorio_id, l.nombre
                HAVING tendencia = 'empeorando'
                ORDER BY e.nombre
            """
            return self.db_manager.execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo equipos tendencia fallas: {e}")
            return []
    
    def _obtener_laboratorios_usuario(self, usuario_id: str) -> List[Dict]:
        """Obtener laboratorios asignados a un usuario"""
        try:
            query = """
                SELECT DISTINCT l.id, l.nombre
                FROM laboratorios l
                LEFT JOIN usuarios u ON (l.id = u.laboratorio_id OR u.nivel_acceso = 6)
                WHERE u.id = %s OR u.nivel_acceso = 6
                ORDER BY l.nombre
            """
            return self.db_manager.execute_query(query, (usuario_id,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo laboratorios usuario: {e}")
            return []
    
    def _obtener_destinatarios_laboratorio(self, laboratorio_id: int) -> List[str]:
        """Obtener emails de destinatarios para un laboratorio"""
        try:
            query = """
                SELECT DISTINCT email
                FROM usuarios u
                INNER JOIN laboratorios l ON (u.laboratorio_id = l.id OR u.nivel_acceso = 6)
                WHERE (l.id = %s OR u.nivel_acceso = 6)
                  AND u.email IS NOT NULL
                  AND u.activo = TRUE
                ORDER BY email
            """
            result = self.db_manager.execute_query(query, (laboratorio_id,))
            return [row['email'] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error obteniendo destinatarios: {e}")
            return []
    
    def _guardar_alertas(self, alertas: List[Alerta]) -> bool:
        """Guardar alertas en base de datos"""
        try:
            # Crear tabla si no existe
            self._crear_tabla_alertas()
            
            for alerta in alertas:
                query = """
                    INSERT INTO alertas_mantenimiento 
                    (id, tipo, titulo, mensaje, equipo_id, equipo_nombre,
                     laboratorio_id, laboratorio_nombre, fecha_alerta,
                     fecha_mantenimiento, riesgo, prioridad, canales,
                     destinatarios, leida)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
                    ON DUPLICATE KEY UPDATE
                    titulo = VALUES(titulo),
                    mensaje = VALUES(mensaje),
                    fecha_alerta = VALUES(fecha_alerta),
                    leida = FALSE
                """
                
                self.db_manager.execute_query(query, (
                    alerta.id,
                    alerta.tipo.value,
                    alerta.titulo,
                    alerta.mensaje,
                    alerta.equipo_id,
                    alerta.equipo_nombre,
                    alerta.laboratorio_id,
                    alerta.laboratorio_nombre,
                    alerta.fecha_alerta,
                    alerta.fecha_mantenimiento,
                    alerta.riesgo,
                    alerta.prioridad,
                    json.dumps([c.value for c in alerta.canales]),
                    json.dumps(alerta.destinatarios)
                ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando alertas: {e}")
            return False
    
    def _crear_tabla_alertas(self):
        """Crear tabla de alertas si no existe"""
        try:
            query = """
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
                    
                    INDEX idx_fecha_alerta (fecha_alerta),
                    INDEX idx_prioridad (prioridad),
                    INDEX idx_laboratorio_id (laboratorio_id),
                    INDEX idx_leida (leida),
                    INDEX idx_equipo_id (equipo_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            self.db_manager.execute_query(query)
        except Exception as e:
            logger.error(f"Error creando tabla alertas: {e}")
    
    def _enviar_email(self, destinatarios: List[str], asunto: str, cuerpo_html: str, cuerpo_texto: str) -> bool:
        """Enviar email usando SMTP"""
        try:
            if not self.config.email_usuario or not self.config.email_password:
                logger.warning("⚠️ Configuración de email incompleta")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = asunto
            msg['From'] = self.config.email_remitente
            msg['To'] = ', '.join(destinatarios)
            
            # Adjuntar partes del mensaje
            msg.attach(MIMEText(cuerpo_texto, 'plain', 'utf-8'))
            msg.attach(MIMEText(cuerpo_html, 'html', 'utf-8'))
            
            # Enviar email
            with smtplib.SMTP(self.config.email_servidor, self.config.email_puerto) as server:
                server.starttls()
                server.login(self.config.email_usuario, self.config.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def _generar_html_alerta(self, alerta: Alerta) -> str:
        """Generar HTML para alerta"""
        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{alerta.titulo}</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">🔔 ALERTA DE MANTENIMIENTO</h1>
                </div>
                
                <div style="padding: 20px 0;">
                    <h2 style="color: #dc3545; margin-top: 0;">{alerta.titulo}</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                        <p style="margin: 0; font-size: 16px; line-height: 1.5;">{alerta.mensaje}</p>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold; width: 150px;">Equipo:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{alerta.equipo_nombre}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Laboratorio:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{alerta.laboratorio_nombre}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Fecha Mantenimiento:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{alerta.fecha_mantenimiento.strftime('%d/%m/%Y')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Riesgo:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                                <span style="background-color: {'#dc3545' if alerta.riesgo == 'crítico' else '#ffc107' if alerta.riesgo == 'alto' else '#28a745' if alerta.riesgo == 'medio' else '#6c757d'}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                                    {alerta.riesgo.upper()}
                                </span>
                            </td>
                        </tr>
                    </table>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Ver Detalles en Sistema
                        </a>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; text-align: center; color: #6c757d; font-size: 12px;">
                    <p style="margin: 0;">Este es un mensaje automático del Sistema de Gestión de Laboratorios - Centro Minero SENA</p>
                    <p style="margin: 5px 0 0;">Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generar_texto_alerta(self, alerta: Alerta) -> str:
        """Generar texto plano para alerta"""
        return f"""
ALERTA DE MANTENIMIENTO - SISTEMA DE LABORATORIOS SENA

{alerta.titulo}
{'=' * 50}

{alerta.mensaje}

DETALLES:
- Equipo: {alerta.equipo_nombre}
- Laboratorio: {alerta.laboratorio_nombre}
- Fecha Mantenimiento: {alerta.fecha_mantenimiento.strftime('%d/%m/%Y')}
- Riesgo: {alerta.riesgo.upper()}
- Prioridad: {alerta.prioridad}

Por favor, tome las acciones necesarias para atender esta alerta.

---
Este es un mensaje automático. Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Sistema de Gestión de Laboratorios - Centro Minero SENA
        """

# Función de inicialización
def create_alert_manager(db_manager, maintenance_predictor, configuracion: Optional[ConfiguracionAlerta] = None):
    """
    Crear instancia del gestor de alertas
    
    Args:
        db_manager: Gestor de base de datos
        maintenance_predictor: Predictor de mantenimientos
        configuracion: Configuración de alertas
        
    Returns:
        MaintenanceAlertManager inicializado
    """
    return MaintenanceAlertManager(db_manager, maintenance_predictor, configuracion)

if __name__ == "__main__":
    # Prueba básica del módulo
    print("🔔 Sistema de Alertas Automáticas")
    print("✅ Clases definidas correctamente")
    print("📧 Sistema de notificaciones listo")
    print("🔄 Generación automática implementada")

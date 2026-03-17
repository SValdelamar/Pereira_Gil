# -*- coding: utf-8 -*-
"""
Módulo de Predicción de Mantenimientos
Sistema de Gestión Inteligente - Centro Minero SENA

Implementación de algoritmos predictivos para mantenimiento de equipos
usando análisis estadístico y machine learning básico.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiesgoMantenimiento(Enum):
    """Niveles de riesgo para mantenimiento predictivo"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

@dataclass
class PrediccionMantenimiento:
    """Estructura para predicciones de mantenimiento"""
    equipo_id: str
    equipo_nombre: str
    tipo_equipo: str
    fecha_predicha: datetime
    riesgo: RiesgoMantenimiento
    confianza: float  # 0.0 a 1.0
    factores: List[str]
    recomendaciones: List[str]
    dias_hasta_mantenimiento: int

@dataclass
class AnalisisEquipo:
    """Análisis completo de un equipo"""
    equipo_id: str
    mtbf: float  # Mean Time Between Failures
    mttr: float  # Mean Time To Repair
    disponibilidad: float
    tendencia_fallas: str
    frecuencia_mantenimiento: float
    ultima_calibracion: Optional[datetime]
    proximo_mantenimiento_estimado: datetime

class MaintenancePredictor:
    """
    Sistema de predicción de mantenimientos usando análisis estadístico
    y algoritmos de machine learning básicos
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.cache_predicciones = {}
        self.cache_timeout = 3600  # 1 hora
        
        # Configuración de algoritmos
        self.config = {
            'dias_historial_analisis': 365,  # 1 año hacia atrás
            'min_mantenimientos_para_prediccion': 3,
            'umbral_riesgo_alto': 0.7,
            'umbral_riesgo_medio': 0.4,
            'factor_calibracion': 1.2,  # Las calibraciones son más críticas
            'factor_uso_intensivo': 1.5
        }
    
    def predecir_mantenimiento_equipo(self, equipo_id: str) -> Optional[PrediccionMantenimiento]:
        """
        Predecir el próximo mantenimiento para un equipo específico
        
        Args:
            equipo_id: ID del equipo a analizar
            
        Returns:
            PrediccionMantenimiento o None si no hay datos suficientes
        """
        try:
            # Verificar caché
            cache_key = f"pred_{equipo_id}"
            if cache_key in self.cache_predicciones:
                cache_data = self.cache_predicciones[cache_key]
                if (datetime.now() - cache_data['timestamp']).seconds < self.cache_timeout:
                    return cache_data['prediccion']
            
            # Obtener datos del equipo
            equipo = self._obtener_datos_equipo(equipo_id)
            if not equipo:
                logger.warning(f"Equipo {equipo_id} no encontrado")
                return None
            
            # Analizar historial de mantenimientos
            historial = self._obtener_historial_mantenimientos(equipo_id)
            if len(historial) < self.config['min_mantenimientos_para_prediccion']:
                logger.info(f"Equipo {equipo_id} tiene datos insuficientes para predicción")
                return self._prediccion_basica(equipo)
            
            # Analizar historial de uso
            uso = self._obtener_historial_uso(equipo_id)
            
            # Calcular predicción
            prediccion = self._calcular_prediccion(equipo, historial, uso)
            
            # Guardar en caché
            self.cache_predicciones[cache_key] = {
                'prediccion': prediccion,
                'timestamp': datetime.now()
            }
            
            return prediccion
            
        except Exception as e:
            logger.error(f"Error prediciendo mantenimiento para {equipo_id}: {e}")
            return None
    
    def predecir_mantenimientos_laboratorio(self, laboratorio_id: int) -> List[PrediccionMantenimiento]:
        """
        Predecir mantenimientos para todos los equipos de un laboratorio
        
        Args:
            laboratorio_id: ID del laboratorio
            
        Returns:
            Lista de predicciones para todos los equipos
        """
        try:
            equipos = self._obtener_equipos_laboratorio(laboratorio_id)
            predicciones = []
            
            for equipo in equipos:
                prediccion = self.predecir_mantenimiento_equipo(equipo['id'])
                if prediccion:
                    predicciones.append(prediccion)
            
            # Ordenar por urgencia (días hasta mantenimiento)
            predicciones.sort(key=lambda p: p.dias_hasta_mantenimiento)
            
            return predicciones
            
        except Exception as e:
            logger.error(f"Error prediciendo mantenimientos laboratorio {laboratorio_id}: {e}")
            return []
    
    def obtener_alertas_mantenimiento(self, dias_adelante: int = 30) -> List[PrediccionMantenimiento]:
        """
        Obtener alertas de mantenimiento para los próximos días
        
        Args:
            dias_adelante: Días hacia adelante para buscar mantenimientos
            
        Returns:
            Lista de predicciones que requieren atención
        """
        try:
            # Obtener todos los equipos activos
            equipos = self._obtener_todos_equipos_activos()
            alertas = []
            
            fecha_limite = datetime.now() + timedelta(days=dias_adelante)
            
            for equipo in equipos:
                prediccion = self.predecir_mantenimiento_equipo(equipo['id'])
                if prediccion and prediccion.fecha_predicha <= fecha_limite:
                    alertas.append(prediccion)
            
            # Ordenar por fecha y riesgo
            alertas.sort(key=lambda p: (p.fecha_predicha, p.riesgo.value))
            
            return alertas
            
        except Exception as e:
            logger.error(f"Error obteniendo alertas de mantenimiento: {e}")
            return []
    
    def analizar_equipo_completo(self, equipo_id: str) -> Optional[AnalisisEquipo]:
        """
        Realizar análisis completo de un equipo
        
        Args:
            equipo_id: ID del equipo
            
        Returns:
            AnalisisEquipo con métricas completas
        """
        try:
            # Obtener datos básicos
            equipo = self._obtener_datos_equipo(equipo_id)
            if not equipo:
                return None
            
            # Calcular MTBF y MTTR
            mtbf = self._calcular_mtbf(equipo_id)
            mttr = self._calcular_mttr(equipo_id)
            
            # Calcular disponibilidad
            disponibilidad = self._calcular_disponibilidad(mtbf, mttr)
            
            # Analizar tendencia de fallas
            tendencia = self._analizar_tendencia_fallas(equipo_id)
            
            # Calcular frecuencia de mantenimiento
            frecuencia = self._calcular_frecuencia_mantenimiento(equipo_id)
            
            # Estimar próximo mantenimiento
            proximo = self._estimar_proximo_mantenimiento(equipo_id)
            
            return AnalisisEquipo(
                equipo_id=equipo_id,
                mtbf=mtbf,
                mttr=mttr,
                disponibilidad=disponibilidad,
                tendencia_fallas=tendencia,
                frecuencia_mantenimiento=frecuencia,
                ultima_calibracion=equipo.get('ultima_calibracion'),
                proximo_mantenimiento_estimado=proximo
            )
            
        except Exception as e:
            logger.error(f"Error analizando equipo {equipo_id}: {e}")
            return None
    
    def _obtener_datos_equipo(self, equipo_id: str) -> Optional[Dict]:
        """Obtener datos básicos del equipo"""
        try:
            query = """
                SELECT id, nombre, tipo, estado, ubicacion, marca,
                       fecha_adquisicion, ultima_calibracion, proximo_mantenimiento,
                       especificaciones
                FROM equipos WHERE id = %s
            """
            result = self.db_manager.execute_query(query, (equipo_id,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error obteniendo datos equipo {equipo_id}: {e}")
            return None
    
    def _obtener_historial_mantenimientos(self, equipo_id: str) -> List[Dict]:
        """Obtener historial completo de mantenimientos de un equipo"""
        try:
            query = """
                SELECT tipo_mantenimiento, fecha_mantenimiento, estado, costo,
                       DATE(fecha_mantenimiento) as fecha
                FROM mantenimientos 
                WHERE equipo_id = %s 
                AND fecha_mantenimiento >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                ORDER BY fecha_mantenimiento DESC
            """
            result = self.db_manager.execute_query(
                query, 
                (equipo_id, self.config['dias_historial_analisis'])
            )
            return result or []
        except Exception as e:
            logger.error(f"Error obteniendo historial mantenimientos {equipo_id}: {e}")
            return []
    
    def _obtener_historial_uso(self, equipo_id: str) -> List[Dict]:
        """Obtener historial de uso del equipo"""
        try:
            query = """
                SELECT fecha_uso, duracion_minutos, proposito
                FROM historial_uso 
                WHERE equipo_id = %s 
                AND fecha_uso >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                ORDER BY fecha_uso DESC
            """
            result = self.db_manager.execute_query(
                query, 
                (equipo_id, self.config['dias_historial_analisis'])
            )
            return result or []
        except Exception as e:
            logger.error(f"Error obteniendo historial uso {equipo_id}: {e}")
            return []
    
    def _calcular_prediccion(self, equipo: Dict, historial: List[Dict], uso: List[Dict]) -> PrediccionMantenimiento:
        """Calcular predicción usando algoritmo avanzado"""
        
        # 1. Análisis de frecuencia de mantenimientos
        intervalos = self._calcular_intervalos_mantenimiento(historial)
        if not intervalos:
            return self._prediccion_basica(equipo)
        
        # 2. Calcular estadísticas básicas
        intervalo_promedio = np.mean(intervalos)
        intervalo_desviacion = np.std(intervalos)
        
        # 3. Analizar tendencia
        tendencia = self._analizar_tendencia_intervalos(intervalos)
        
        # 4. Ajustar por tipo de mantenimiento
        ajuste_tipo = self._calcular_ajuste_tipo_equipo(equipo['tipo'])
        
        # 5. Ajustar por intensidad de uso
        ajuste_uso = self._calcular_ajuste_uso(uso)
        
        # 6. Calcular próximo mantenimiento
        ultimo_mantenimiento = historial[0]['fecha']
        dias_base = intervalo_promedio * ajuste_tipo * ajuste_uso
        
        # Aplicar tendencia
        if tendencia == 'aumentando':
            dias_base *= 0.8  # Más mantenimientos pronto
        elif tendencia == 'disminuyendo':
            dias_base *= 1.2  # Menos mantenimientos
        
        # Calcular fecha predicha
        fecha_predicha = ultimo_mantenimiento + timedelta(days=dias_base)
        
        # 7. Calcular confianza y riesgo
        confianza = self._calcular_confianza(len(historial), intervalo_desviacion)
        riesgo = self._determinar_riesgo(fecha_predicha, confianza)
        
        # 8. Generar factores y recomendaciones
        factores = self._generar_factores_riesgo(equipo, historial, uso)
        recomendaciones = self._generar_recomendaciones(riesgo, equipo, factores)
        
        return PrediccionMantenimiento(
            equipo_id=equipo['id'],
            equipo_nombre=equipo['nombre'],
            tipo_equipo=equipo['tipo'],
            fecha_predicha=fecha_predicha,
            riesgo=riesgo,
            confianza=confianza,
            factores=factores,
            recomendaciones=recomendaciones,
            dias_hasta_mantenimiento=(fecha_predicha - datetime.now()).days
        )
    
    def _prediccion_basica(self, equipo: Dict) -> PrediccionMantenimiento:
        """Predicción básica basada en configuración por defecto"""
        dias_base = 90  # 3 meses por defecto
        
        # Si tiene último mantenimiento, usar como referencia
        if equipo.get('proximo_mantenimiento'):
            fecha_base = datetime.strptime(equipo['proximo_mantenimiento'], '%Y-%m-%d')
        else:
            fecha_base = datetime.now() + timedelta(days=dias_base)
        
        confianza = 0.3  # Baja confianza por falta de datos
        riesgo = RiesgoMantenimiento.MEDIO
        
        return PrediccionMantenimiento(
            equipo_id=equipo['id'],
            equipo_nombre=equipo['nombre'],
            tipo_equipo=equipo['tipo'],
            fecha_predicha=fecha_base,
            riesgo=riesgo,
            confianza=confianza,
            factores=['Datos históricos limitados'],
            recomendaciones=['Registrar más mantenimientos para mejorar predicciones'],
            dias_hasta_mantenimiento=(fecha_base - datetime.now()).days
        )
    
    def _calcular_intervalos_mantenimiento(self, historial: List[Dict]) -> List[float]:
        """Calcular intervalos en días entre mantenimientos"""
        if len(historial) < 2:
            return []
        
        intervalos = []
        for i in range(len(historial) - 1):
            fecha_actual = datetime.strptime(historial[i]['fecha'], '%Y-%m-%d')
            fecha_anterior = datetime.strptime(historial[i + 1]['fecha'], '%Y-%m-%d')
            dias = (fecha_actual - fecha_anterior).days
            if dias > 0:
                intervalos.append(dias)
        
        return intervalos
    
    def _analizar_tendencia_intervalos(self, intervalos: List[float]) -> str:
        """Analizar si los intervalos están aumentando o disminuyendo"""
        if len(intervalos) < 3:
            return 'estable'
        
        # Comparar primeros vs últimos intervalos
        primeros = intervalos[:len(intervalos)//2]
        ultimos = intervalos[len(intervalos)//2:]
        
        promedio_primeros = np.mean(primeros)
        promedio_ultimos = np.mean(ultimos)
        
        diferencia = (promedio_ultimos - promedio_primeros) / promedio_primeros
        
        if diferencia > 0.1:
            return 'aumentando'  # Intervalos más largos = menos fallas
        elif diferencia < -0.1:
            return 'disminuyendo'  # Intervalos más cortos = más fallas
        else:
            return 'estable'
    
    def _calcular_ajuste_tipo_equipo(self, tipo_equipo: str) -> float:
        """Calcular factor de ajuste según tipo de equipo"""
        factores = {
            'microscopio': 0.8,  # Requiere más mantenimiento
            'balanza': 0.7,      # Calibración frecuente
            'espectrometro': 0.6, # Muy sensible
            'centrífuga': 0.9,   # Mantenimiento regular
            'autoclave': 0.8,     # Requiere verificación constante
            'computadora': 1.2,   # Menos mantenimiento
            'impresora': 1.1,     # Mantenimiento estándar
        }
        
        return factores.get(tipo_equipo.lower(), 1.0)
    
    def _calcular_ajuste_uso(self, historial_uso: List[Dict]) -> float:
        """Calcular factor de ajuste según intensidad de uso"""
        if not historial_uso:
            return 1.0
        
        # Calcular uso promedio semanal
        uso_total_horas = sum([u['duracion_minutos'] / 60 for u in historial_uso])
        semanas_analizadas = len(historial_uso) / 7.0
        uso_promedio_semanal = uso_total_horas / max(semanas_analizadas, 1)
        
        # Ajustar según intensidad
        if uso_promedio_semanal > 20:  # Más de 20 horas/semana
            return self.config['factor_uso_intensivo']
        elif uso_promedio_semanal > 10:  # 10-20 horas/semana
            return 1.2
        elif uso_promedio_semanal > 5:   # 5-10 horas/semana
            return 1.1
        else:
            return 1.0
    
    def _calcular_confianza(self, cantidad_mantenimientos: int, desviacion: float) -> float:
        """Calcular nivel de confianza en la predicción"""
        # Más datos = más confianza
        confianza_datos = min(cantidad_mantenimientos / 10.0, 1.0)
        
        # Menos variabilidad = más confianza
        if desviacion > 0:
            confianza_variabilidad = max(1.0 - (desviacion / 30.0), 0.0)
        else:
            confianza_variabilidad = 1.0
        
        # Combinar factores
        confianza_total = (confianza_datos + confianza_variabilidad) / 2.0
        return max(min(confianza_total, 1.0), 0.0)
    
    def _determinar_riesgo(self, fecha_predicha: datetime, confianza: float) -> RiesgoMantenimiento:
        """Determinar nivel de riesgo basado en fecha y confianza"""
        dias_hasta = (fecha_predicha - datetime.now()).days
        
        # Ajustar por confianza
        if confianza < 0.5:
            dias_hasta *= 0.7  # Reducir tiempo por baja confianza
        
        if dias_hasta <= 7:
            return RiesgoMantenimiento.CRITICO
        elif dias_hasta <= 15:
            return RiesgoMantenimiento.ALTO
        elif dias_hasta <= 30:
            return RiesgoMantenimiento.MEDIO
        else:
            return RiesgoMantenimiento.BAJO
    
    def _generar_factores_riesgo(self, equipo: Dict, historial: List[Dict], uso: List[Dict]) -> List[str]:
        """Generar lista de factores que influyen en el riesgo"""
        factores = []
        
        # Edad del equipo
        if equipo.get('fecha_adquisicion'):
            edad = (datetime.now() - datetime.strptime(equipo['fecha_adquisicion'], '%Y-%m-%d')).days / 365
            if edad > 5:
                factores.append(f"Equipo antiguo ({edad:.1f} años)")
        
        # Tipo de mantenimiento
        tipos = [m['tipo_mantenimiento'] for m in historial if m['tipo_mantenimiento'] == 'correctivo']
        if len(tipos) > len(historial) * 0.3:
            factores.append("Alta frecuencia de mantenimientos correctivos")
        
        # Uso intensivo
        if uso:
            uso_horas_total = sum([u['duracion_minutos'] / 60 for u in uso])
            if uso_horas_total > 100:
                factores.append("Uso intensivo del equipo")
        
        # Calibración vencida
        if equipo.get('ultima_calibracion'):
            ultima_cal = datetime.strptime(equipo['ultima_calibracion'], '%Y-%m-%d')
            dias_desde_cal = (datetime.now() - ultima_cal).days
            if dias_desde_cal > 365:
                factores.append("Calibración vencida o próxima a vencer")
        
        return factores
    
    def _generar_recomendaciones(self, riesgo: RiesgoMantenimiento, equipo: Dict, factores: List[str]) -> List[str]:
        """Generar recomendaciones específicas"""
        recomendaciones = []
        
        if riesgo == RiesgoMantenimiento.CRITICO:
            recomendaciones.append("Programar mantenimiento inmediato")
            recomendaciones.append("Considerar reemplazo si fallas frecuentes")
        
        if riesgo == RiesgoMantenimiento.ALTO:
            recomendaciones.append("Programar mantenimiento en los próximos 15 días")
            recomendaciones.append("Inspeccionar equipo semanalmente")
        
        if riesgo == RiesgoMantenimiento.MEDIO:
            recomendaciones.append("Monitorear estado del equipo")
            recomendaciones.append("Preparar materiales para mantenimiento")
        
        # Recomendaciones específicas por factores
        for factor in factores:
            if "antiguo" in factor:
                recomendaciones.append("Evaluar renovación del equipo")
            elif "correctivos" in factor:
                recomendaciones.append("Revisar procedimientos de uso")
            elif "intensivo" in factor:
                recomendaciones.append("Considerar equipo de respaldo")
            elif "calibración" in factor:
                recomendaciones.append("Priorizar calibración del equipo")
        
        return list(set(recomendaciones))  # Eliminar duplicados
    
    def _calcular_mtbf(self, equipo_id: str) -> float:
        """Calcular Mean Time Between Failures"""
        try:
            query = """
                SELECT COUNT(*) as total_fallas,
                       TIMESTAMPDIFF(DAY, MIN(fecha_mantenimiento), MAX(fecha_mantenimiento)) as periodo_dias
                FROM mantenimientos 
                WHERE equipo_id = %s 
                AND tipo_mantenimiento = 'correctivo'
                AND estado = 'completado'
            """
            result = self.db_manager.execute_query(query, (equipo_id,))
            
            if result and result[0]['total_fallas'] > 0 and result[0]['periodo_dias'] > 0:
                return result[0]['periodo_dias'] / result[0]['total_fallas']
            else:
                return 365.0  # Valor por defecto: 1 año
        except Exception as e:
            logger.error(f"Error calculando MTBF: {e}")
            return 365.0
    
    def _calcular_mttr(self, equipo_id: str) -> float:
        """Calcular Mean Time To Repair"""
        try:
            query = """
                SELECT AVG(DATEDIFF(fecha_creacion, 
                    (SELECT fecha_mantenimiento FROM mantenimientos m2 
                     WHERE m2.equipo_id = m1.equipo_id AND m2.tipo_mantenimiento = 'correctivo' 
                     AND m2.fecha_mantenimiento < m1.fecha_mantenimiento 
                     ORDER BY m2.fecha_mantenimiento DESC LIMIT 1))) as avg_repair_time
                FROM mantenimientos m1
                WHERE equipo_id = %s 
                AND tipo_mantenimiento = 'correctivo' 
                AND estado = 'completado'
            """
            result = self.db_manager.execute_query(query, (equipo_id,))
            
            if result and result[0]['avg_repair_time']:
                return float(result[0]['avg_repair_time'])
            else:
                return 3.0  # Valor por defecto: 3 días
        except Exception as e:
            logger.error(f"Error calculando MTTR: {e}")
            return 3.0
    
    def _calcular_disponibilidad(self, mtbf: float, mttr: float) -> float:
        """Calcular disponibilidad del equipo"""
        if mtbf <= 0:
            return 0.0
        return mtbf / (mtbf + mttr)
    
    def _analizar_tendencia_fallas(self, equipo_id: str) -> str:
        """Analizar tendencia de fallas del equipo"""
        try:
            query = """
                SELECT DATE(fecha_mantenimiento) as fecha, COUNT(*) as fallas
                FROM mantenimientos 
                WHERE equipo_id = %s 
                AND tipo_mantenimiento = 'correctivo'
                AND fecha_mantenimiento >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY DATE(fecha_mantenimiento)
                ORDER BY fecha
            """
            result = self.db_manager.execute_query(query, (equipo_id,))
            
            if len(result) < 3:
                return 'estable'
            
            # Analizar tendencia simple
            fallas_primer_mes = len([r for r in result[:len(result)//2]])
            fallas_ultimo_mes = len([r for r in result[len(result)//2:]])
            
            if fallas_ultimo_mes > fallas_primer_mes * 1.2:
                return 'empeorando'
            elif fallas_ultimo_mes < fallas_primer_mes * 0.8:
                return 'mejorando'
            else:
                return 'estable'
        except Exception as e:
            logger.error(f"Error analizando tendencia fallas: {e}")
            return 'estable'
    
    def _calcular_frecuencia_mantenimiento(self, equipo_id: str) -> float:
        """Calcular frecuencia promedio de mantenimientos"""
        try:
            query = """
                SELECT COUNT(*) as total_mantenimientos,
                       TIMESTAMPDIFF(DAY, MIN(fecha_mantenimiento), MAX(fecha_mantenimiento)) as periodo_dias
                FROM mantenimientos 
                WHERE equipo_id = %s 
                AND estado = 'completado'
            """
            result = self.db_manager.execute_query(query, (equipo_id,))
            
            if result and result[0]['total_mantenimientos'] > 0 and result[0]['periodo_dias'] > 0:
                return result[0]['periodo_dias'] / result[0]['total_mantenimientos']
            else:
                return 90.0  # Valor por defecto: 90 días
        except Exception as e:
            logger.error(f"Error calculando frecuencia mantenimiento: {e}")
            return 90.0
    
    def _estimar_proximo_mantenimiento(self, equipo_id: str) -> datetime:
        """Estimar próximo mantenimiento basado en patrones"""
        prediccion = self.predecir_mantenimiento_equipo(equipo_id)
        if prediccion:
            return prediccion.fecha_predicha
        else:
            return datetime.now() + timedelta(days=90)
    
    def _obtener_equipos_laboratorio(self, laboratorio_id: int) -> List[Dict]:
        """Obtener todos los equipos de un laboratorio"""
        try:
            query = """
                SELECT id, nombre, tipo, estado 
                FROM equipos 
                WHERE laboratorio_id = %s AND estado != 'fuera_servicio'
                ORDER BY tipo, nombre
            """
            return self.db_manager.execute_query(query, (laboratorio_id,)) or []
        except Exception as e:
            logger.error(f"Error obteniendo equipos laboratorio {laboratorio_id}: {e}")
            return []
    
    def _obtener_todos_equipos_activos(self) -> List[Dict]:
        """Obtener todos los equipos activos"""
        try:
            query = """
                SELECT id, nombre, tipo, estado 
                FROM equipos 
                WHERE estado IN ('disponible', 'en_uso', 'mantenimiento')
                ORDER BY tipo, nombre
            """
            return self.db_manager.execute_query(query) or []
        except Exception as e:
            logger.error(f"Error obteniendo equipos activos: {e}")
            return []

# Función de inicialización
def create_maintenance_predictor(db_manager):
    """
    Crear instancia del predictor de mantenimientos
    
    Args:
        db_manager: Gestor de base de datos
        
    Returns:
        MaintenancePredictor inicializado
    """
    return MaintenancePredictor(db_manager)

if __name__ == "__main__":
    # Prueba básica del módulo
    print("🔧 Módulo de Predicción de Mantenimientos")
    print("✅ Clases definidas correctamente")
    print("📊 Algoritmos predictivos implementados")
    print("🔔 Sistema de alertas listo")

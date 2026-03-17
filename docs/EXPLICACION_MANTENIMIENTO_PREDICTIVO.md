# 🔍 **Sistema de Alertas y Mantenimientos Predictivos - Explicación Detallada**

## 📋 **Resumen del Sistema**

El sistema de mantenimiento predictivo utiliza **análisis estadístico y algoritmos de machine learning básicos** para predecir cuándo los equipos necesitarán mantenimiento y generar alertas automáticas.

---

## 🧠 **Bases para Generar Alertas y Programación**

### **1. 📊 Análisis de Datos Históricos**

#### **📅 Historial de Mantenimientos:**
```python
# Analiza el último año de datos
dias_historial_analisis: int = 365
min_mantenimientos_para_prediccion: int = 3
```

**Datos analizados:**
- 📅 **Fecha de cada mantenimiento**
- 🔧 **Tipo** (preventivo, correctivo, calibración, limpieza)
- 💰 **Costo** del mantenimiento
- 📈 **Estado** (programado, en_proceso, completado, cancelado)

#### **⏱️ Cálculos Estadísticos:**
- **MTBF (Mean Time Between Failures):** Tiempo promedio entre fallas
- **MTTR (Mean Time To Repair):** Tiempo promedio de reparación
- **Disponibilidad:** Porcentaje de tiempo operativo
- **Frecuencia de mantenimiento:** Intervalo promedio entre mantenimientos

---

### **2. 📈 Análisis de Tendencias**

#### **🔍 Detección de Patrones:**
```python
def _analizar_tendencia_fallas(self, equipo_id: str) -> str:
    # Analiza si las fallas están aumentando, disminuyendo o estables
    # Usa regresión lineal sobre los intervalos de mantenimiento
```

**Tipos de tendencias:**
- 📈 **Aumentando:** Fallas más frecuentes → Reducir intervalo 20%
- 📉 **Disminuyendo:** Fallas menos frecuentes → Aumentar intervalo 20%
- ➡️ **Estable:** Sin cambios → Mantener intervalo

---

### **3. 🔧 Factores Específicos por Tipo de Equipo**

#### **📋 Factores de Ajuste por Tipo:**
```python
factores = {
    'microscopio': 0.8,     # Requiere más mantenimiento (óptica delicada)
    'balanza': 0.7,         # Calibración frecuente (precisión crítica)
    'espectrometro': 0.6,    # Muy sensible (análisis químico)
    'centrífuga': 0.9,      # Mantenimiento regular (partes móviles)
    'autoclave': 0.8,       # Requiere verificación constante (presión/temperatura)
    'computadora': 1.2,     # Menos mantenimiento (sólido)
    'impresora': 1.1,       # Mantenimiento estándar
}
```

---

### **4. 💪 Análisis de Intensidad de Uso**

#### **📊 Cálculo de Uso:**
```python
def _calcular_ajuste_uso(self, historial_uso: List[Dict]) -> float:
    uso_promedio_semanal = total_horas / semanas_analizadas
    
    if uso_promedio_semanal > 20:    # Más de 20 horas/semana
        return 1.5  # Uso intensivo → Mantenimiento más frecuente
    elif uso_promedio_semanal > 10:  # 10-20 horas/semana
        return 1.2  # Uso moderado-alto
    elif uso_promedio_semanal > 5:   # 5-10 horas/semana
        return 1.1  # Uso moderado
    else:
        return 1.0  # Uso ligero
```

---

### **5. 📅 Edad y Antigüedad del Equipo**

#### **🕰️ Factor de Envejecimiento:**
```python
if edad > 5:
    factores.append(f"Equipo antiguo ({edad:.1f} años)")
    # Aplica factor de 1.3 para equipos antiguos
```

---

## 🎯 **Algoritmo de Predicción**

### **🔢 Fórmula Principal:**
```python
# 1. Intervalo base promedio
intervalo_promedio = calcular_intervalo_promedio(historial)

# 2. Ajuste por tipo de equipo
ajuste_tipo = factores_tipo_equipo[tipo_equipo]

# 3. Ajuste por intensidad de uso
ajuste_uso = calcular_ajuste_uso(historial_uso)

# 4. Ajuste por tendencia
if tendencia == 'aumentando':
    factor_tendencia = 0.8  # Reducir días
elif tendencia == 'disminuyendo':
    factor_tendencia = 1.2  # Aumentar días

# 5. Cálculo final
dias_base = intervalo_promedio * ajuste_tipo * ajuste_uso * factor_tendencia
fecha_predicha = ultimo_mantenimiento + timedelta(days=dias_base)
```

---

## 🚨 **Sistema de Alertas**

### **📋 Tipos de Alertas Generadas:**

#### **1. 📅 Mantenimientos Próximos**
- **Anticipación:** 30 días por defecto
- **Prioridad:** Alta si < 15 días
- **Mensaje:** "Mantenimiento programado en X días"

#### **2. ⚠️ Mantenimientos Vencidos**
- **Condición:** Fecha de mantenimiento < hoy
- **Prioridad:** Crítica
- **Mensaje:** "Mantenimiento vencido hace X días"

#### **3. 🔧 Calibraciones Vencidas**
- **Anticipación:** 15 días
- **Condición:** Última calibración > 365 días
- **Prioridad:** Alta

#### **4. 💥 Equipos Críticos**
- **Condición:** Estado = 'en_mantenimiento' o 'dado_de_baja'
- **Prioridad:** Crítica
- **Mensaje:** "Equipo requiere atención inmediata"

#### **5. 📈 Uso Excesivo**
- **Condición:** Uso > 20 horas/semana
- **Prioridad:** Media
- **Mensaje:** "Uso intensivo detectado"

#### **6. 📉 Tendencias de Fallas**
- **Condición:** Tendencia = 'aumentando'
- **Prioridad:** Media-Alta
- **Mensaje:** "Aumento en frecuencia de fallas"

---

## 🎯 **Niveles de Riesgo y Confianza**

### **🔴 Niveles de Riesgo:**
```python
def _determinar_riesgo(self, fecha_predicha: datetime, confianza: float) -> RiesgoMantenimiento:
    dias_hasta = (fecha_predicha - datetime.now()).days
    
    if dias_hasta <= 7:
        return RiesgoMantenimiento.CRITICO    # 🔴 Rojo
    elif dias_hasta <= 15:
        return RiesgoMantenimiento.ALTO        # 🟡 Amarillo  
    elif dias_hasta <= 30:
        return RiesgoMantenimiento.MEDIO       # 🔵 Azul
    else:
        return RiesgoMantenimiento.BAJO        # 🟢 Verde
```

### **📊 Nivel de Confianza:**
```python
confianza = (confianza_datos + confianza_variabilidad) / 2.0
# Más datos históricos = más confianza
# Menos variabilidad = más confianza
```

---

## 📋 **Factores de Riesgo Considerados**

### **🔍 Análisis Multifactorial:**

#### **✅ Factores Cuantificables:**
- 📅 **Edad del equipo:** Años desde adquisición
- ⏱️ **Horas de uso:** Total horas/semana
- 🔧 **Mantenimientos previos:** Cantidad y tipo
- 💰 **Costos acumulados:** Tendencia de costos
- 📈 **Frecuencia de fallas:** Intervalos entre mantenimientos

#### **⚠️ Factores Cualitativos:**
- 🔧 **Tipo de equipo:** Sensibilidad y complejidad
- 📍 **Ubicación:** Condiciones ambientales
- 👥 **Operador:** Experiencia del usuario
- 🌡️ **Condiciones de uso:** Temperatura, humedad, vibración

---

## 🎯 **Recomendaciones Generadas**

### **📝 Por Nivel de Riesgo:**

#### **🔴 CRÍTICO:**
- "Programar mantenimiento inmediato"
- "Considerar reemplazo si fallas recurrentes"
- "Inspección completa recomendada"

#### **🟡 ALTO:**
- "Programar mantenimiento en los próximos 15 días"
- "Monitorear uso intensivo"
- "Preparar repuestos necesarios"

#### **🔵 MEDIO:**
- "Programar mantenimiento en 30 días"
- "Revisar calendario de uso"
- "Considerar inspección visual"

#### **🟢 BAJO:**
- "Mantener programa regular"
- "Continuar monitoreo normal"
- "Registrar uso para futuros análisis"

---

## 🔄 **Actualización y Aprendizaje**

### **📈 Mejora Continua:**
- **Cache de predicciones:** 1 hora para no recalcular
- **Ajuste automático:** Los nuevos datos mejoran futuras predicciones
- **Retroalimentación:** Mantenimientos reales vs. predichos

### **🎯 Precisión del Sistema:**
- **Confianza alta:** >80% con 10+ mantenimientos históricos
- **Confianza media:** 50-80% con 5-10 mantenimientos
- **Confianza baja:** <50% con <5 mantenimientos (usa predicción básica)

---

## 🌐 **Integración con el Sistema**

### **📊 Dashboard:**
- **Indicadores visuales:** Colores por nivel de riesgo
- **Alertas en tiempo real:** Actualizadas automáticamente
- **Análisis detallado:** Modal con información completa

### **🔔 Notificaciones:**
- **Email:** Configurable para administradores
- **Dashboard:** Alertas integradas en la interfaz
- **SMS:** Futuro (configuración lista)

### **📱 API REST:**
- **7 endpoints** para consulta y gestión
- **JSON responses** con predicciones y alertas
- **Autenticación** por JWT

---

## 🎉 **Resultado Final**

El sistema combina:
- 📊 **Análisis estadístico** de datos históricos
- 🤖 **Machine learning** básico para patrones
- 🔧 **Factores específicos** por tipo de equipo
- 💪 **Análisis de uso** e intensidad
- 📈 **Tendencias** y predicciones
- 🚨 **Alertas automáticas** contextuales

**Todo esto para predecir con alta precisión cuándo cada equipo necesitará mantenimiento, optimizando recursos y evitando fallas inesperadas.** 🚀

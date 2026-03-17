# 🚀 Sistema de Mantenimiento Predictivo - Guía de Uso

## 📋 Resumen de Implementación

El sistema de mantenimiento predictivo ha sido **completamente implementado** con las siguientes características:

### ✅ Componentes Principales

| Componente | Archivo | Función |
|------------|---------|---------|
| **🔧 Predictor** | `modules/maintenance_predictor.py` | Algoritmos de predicción basados en IA |
| **🔔 Alertas** | `modules/maintenance_alerts.py` | Sistema de notificaciones automáticas |
| **⚙️ Configuración** | `modules/maintenance_config.py` | Gestión de configuración flexible |
| **🌐 API** | `web_app.py` (endpoints) | 7 endpoints REST para predicciones |
| **🎨 UI** | `app/templates/modules/equipos.html` | Interfaz con indicadores IA |

---

## 🚀 Inicio Rápido

### 1. **Iniciar la Aplicación**

```bash
# Activar entorno virtual (si aplica)
.venv\Scripts\activate

# Iniciar servidor
python web_app.py runserver
```

### 2. **Acceder a las Funciones**

- **📊 Dashboard de Mantenimiento:** Visita `/equipos`
- **🔍 Análisis Predictivo:** Haz clic en el botón 🤖 de cualquier equipo
- **🚨 Alertas:** Las alertas aparecen automáticamente en el dashboard

---

## 🎯 Funcionalidades Disponibles

### 🔮 **Predicción de Mantenimientos**

**Algoritmos implementados:**
- 📈 **Análisis de frecuencia** de mantenimientos históricos
- 🎯 **Cálculo de MTBF/MTTR** (Mean Time Between/To Repair)
- 📊 **Análisis de tendencias** de fallas
- ⚖️ **Factores de ajuste** por tipo de equipo y uso
- 🎲 **Predicción con confianza** y nivel de riesgo

**Factores considerados:**
- 📅 Historial de mantenimientos (último año)
- ⏱️ Frecuencia y tendencias de fallas
- 🔧 Tipo de equipo (microscopio, balanza, etc.)
- 💪 Intensidad de uso (horas/semana)
- 📅 Edad del equipo (años de antigüedad)

### 🚨 **Alertas Automáticas**

**Tipos de alertas:**
- 📅 **Mantenimientos próximos** (30 días por defecto)
- ⚠️ **Mantenimientos vencidos**
- 🔧 **Calibraciones vencidas/próximas**
- 💥 **Equipos en estado crítico**
- 📈 **Uso excesivo** (>20 horas/semana)
- 📉 **Tendencias de fallas** preocupantes

**Niveles de riesgo:**
- 🔴 **Crítico:** Mantenimientos vencidos, equipos críticos
- 🟡 **Alto:** Mantenimientos < 15 días, calibraciones vencidas
- 🔵 **Medio:** Mantenimientos 15-30 días, tendencias preocupantes
- 🟢 **Bajo:** Mantenimientos > 30 días, uso moderado

### 🌐 **API REST**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/maintenance/predict/<equipo_id>` | GET | Predecir mantenimiento individual |
| `/api/maintenance/predict/laboratorio/<id>` | GET | Predicciones por laboratorio |
| `/api/maintenance/analyze/<equipo_id>` | GET | Análisis completo de equipo |
| `/api/maintenance/alerts` | GET | Obtener alertas del usuario |
| `/api/maintenance/alerts/<id>/read` | POST | Marcar alerta como leída |
| `/api/maintenance/dashboard` | GET | Datos para dashboard |
| `/api/maintenance/generate-alerts` | POST | Generar alertas manualmente |

---

## 🎨 **Uso de la Interfaz**

### 📊 **Vista de Equipos**

En la página `/equipos` encontrarás:

**Nueva columna "Predicción IA":**
- 🤖 **Indicador visual** con días hasta mantenimiento
- 🎨 **Colores por riesgo:** Verde (bajo), Azul (medio), Amarillo (alto), Rojo (crítico)
- 📊 **Badge con formato:** `🚨 7d` (riesgo y días restantes)

**Botón de análisis:**
- 🔍 **Botón 🤖** al lado de cada equipo
- 📈 **Modal detallado** con análisis completo
- 📊 **Métricas MTBF/MTTR** y disponibilidad
- 💡 **Recomendaciones** específicas

### 📈 **Modal de Análisis Predictivo**

Al hacer clic en 🤖:

**Sección de Predicción:**
- 📅 **Fecha predicha** del próximo mantenimiento
- 🎯 **Nivel de riesgo** con indicador visual
- 📊 **Confianza del modelo** en porcentaje
- 📋 **Factores de riesgo** identificados

**Sección de Rendimiento:**
- 📈 **MTBF:** Tiempo promedio entre fallas
- ⏱️ **MTTR:** Tiempo promedio de reparación
- 💯 **Disponibilidad:** Porcentaje de tiempo operativo
- 📉 **Tendencia de fallas:** Mejorando/estable/empeorando

---

## ⚙️ **Configuración**

### 📧 **Configurar Email (Opcional)**

Edita tu archivo `.env`:

```bash
# Habilitar notificaciones por email
HABILITAR_EMAIL=true

# Configuración SMTP (Gmail ejemplo)
EMAIL_SERVIDOR=smtp.gmail.com
EMAIL_PUERTO=587
EMAIL_USUARIO=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_app
EMAIL_REMITENTE=sistema@sena.edu.co
```

### 🎛️ **Ajustar Parámetros de Predicción**

```bash
# Días de anticipación para alertas
DIAS_ANTICIPACION_MANTENIMIENTO=30
DIAS_ANTICIPACION_CALIBRACION=15

# Umbrales de riesgo
UMBRAL_RIESGO_ALTO=0.7
UMBRAL_RIESGO_MEDIO=0.4

# Configuración de análisis
DIAS_HISTORIAL=365
MIN_MANTENIMIENTOS_PREDICCION=3
```

---

## 🧪 **Pruebas y Verificación**

### ✅ **Verificar Instalación**

Ejecuta el script de prueba:

```bash
python test_maintenance.py
```

**Salida esperada:**
```
🧪 Probando Sistema de Mantenimiento Predictivo
✅ Configuración cargada
✅ Predictor importado
✅ Alert manager importado
✅ NumPy 2.2.6 disponible
🎉 Todas las pruebas pasaron exitosamente!
```

### 📊 **Probar API**

```bash
# Probar predicción de equipo (reemplaza ID_EQUIPO)
curl http://localhost:5000/api/maintenance/predict/ID_EQUIPO

# Probar dashboard de mantenimiento
curl http://localhost:5000/api/maintenance/dashboard
```

---

## 📈 **Ejemplos de Uso**

### 🔍 **Análisis Individual**

1. **Ve a `/equipos`**
2. **Busca un equipo** con historial de mantenimientos
3. **Haz clic en 🤖** para ver análisis completo
4. **Revisa predicción** y recomendaciones

### 📊 **Predicciones por Laboratorio**

```javascript
// Obtener predicciones del laboratorio 1
fetch('/api/maintenance/predict/laboratorio/1')
  .then(response => response.json())
  .then(data => {
    console.log('Predicciones:', data.predicciones);
  });
```

### 🚨 **Generar Alertas Manualmente**

```bash
# Generar alertas para todos los equipos
curl -X POST http://localhost:5000/api/maintenance/generate-alerts
```

---

## 🔧 **Solución de Problemas**

### ❌ **Error: "Datos insuficientes para predicción"**

**Causa:** El equipo tiene menos de 3 mantenimientos registrados.

**Solución:**
- Registra más mantenimientos históricos
- El sistema usará predicción básica mientras acumula datos

### ⚠️ **Error: "No hay datos históricos"**

**Causa:** El equipo es nuevo o no tiene mantenimientos registrados.

**Solución:**
- El sistema mostrará predicción básica (90 días por defecto)
- Registra mantenimientos para mejorar predicciones

### 📧 **Email no funciona**

**Verifica:**
1. `HABILITAR_EMAIL=true` en `.env`
2. Credenciales SMTP correctas
3. Contraseña de aplicación (no contraseña normal)

---

## 🚀 **Mejoras Futuras**

### 📋 **Próximas Versiones**

1. **Machine Learning Avanzado:**
   - Modelos de regresión más sofisticados
   - Análisis de series temporales
   - Clustering de patrones

2. **Integraciones:**
   - Conexión con sistemas ERP
   - Webhooks para sistemas externos
   - API móvil

3. **Automatización:**
   - Programación automática de mantenimientos
   - Órdenes de trabajo generadas
   - Notificaciones a técnicos

---

## 🎉 **Resumen de Beneficios**

### 🏢 **Para el Laboratorio**

- 📅 **Planificación anticipada** de mantenimientos
- 💰 **Reducción de costos** por fallas inesperadas  
- ⏰ **Maximización de disponibilidad** de equipos
- 📊 **Decisiones basadas en datos** reales

### 👥 **Para los Usuarios**

- 🔔 **Alertas oportunas** antes de fallas
- 📱 **Información accesible** desde dashboard
- 🤖 **Asistencia IA** para decisiones
- 📋 **Análisis detallado** con un clic

---

## 🆘 **Soporte**

Si encuentras algún problema:

1. **Revisa este documento** para soluciones comunes
2. **Ejecuta `test_maintenance.py`** para verificar instalación
3. **Revisa los logs** en la consola de la aplicación
4. **Verifica la configuración** en tu archivo `.env`

**¡El sistema está listo para usar! 🚀**

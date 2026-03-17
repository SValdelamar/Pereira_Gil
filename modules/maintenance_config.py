# -*- coding: utf-8 -*-
"""
Configuración del Sistema de Notificaciones de Mantenimiento
Sistema de Gestión Inteligente - Centro Minero SENA

Archivo de configuración para personalizar el comportamiento del sistema
de alertas y notificaciones automáticas.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class TipoNotificacion(Enum):
    """Tipos de notificaciones disponibles"""
    EMAIL = "email"
    DASHBOARD = "dashboard"
    SMS = "sms"
    WEBHOOK = "webhook"

class NivelPrioridad(Enum):
    """Niveles de prioridad para notificaciones"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

@dataclass
class ConfiguracionEmail:
    """Configuración para notificaciones por email"""
    servidor: str = "smtp.gmail.com"
    puerto: int = 587
    usuario: str = ""
    password: str = ""
    remitente: str = "sistema@sena.edu.co"
    nombre_remitente: str = "Sistema de Laboratorios SENA"
    usar_tls: bool = True
    usar_ssl: bool = False
    
    # Plantillas
    plantilla_html: str = "default"
    plantilla_texto: str = "default"
    
    # Límites
    max_emails_por_hora: int = 100
    max_destinatarios_por_email: int = 50

@dataclass
class ConfiguracionDashboard:
    """Configuración para notificaciones en dashboard"""
    mostrar_alertas_criticas_primero: bool = True
    max_alertas_mostradas: int = 50
    auto_actualizar_cada: int = 300  # segundos
    mostrar_solo_no_leidas: bool = False
    agrupar_por_tipo: bool = True

@dataclass
class ConfiguracionSMS:
    """Configuración para notificaciones SMS (futuro)"""
    proveedor: str = "twilio"
    api_key: str = ""
    api_secret: str = ""
    numero_remitente: str = ""
    max_sms_por_dia: int = 100
    solo_alertas_criticas: bool = True

@dataclass
class ConfiguracionWebhook:
    """Configuración para webhooks (futuro)"""
    urls: List[str] = None
    headers: Dict[str, str] = None
    timeout: int = 30
    reintentos: int = 3
    solo_alertas_criticas: bool = False
    
    def __post_init__(self):
        if self.urls is None:
            self.urls = []
        if self.headers is None:
            self.headers = {}

@dataclass
class ConfiguracionMantenimiento:
    """Configuración general del sistema de mantenimiento"""
    # Tiempos de anticipación (días)
    dias_anticipacion_mantenimiento: int = 30
    dias_anticipacion_calibracion: int = 15
    dias_anticipacion_critico: int = 7
    
    # Umbrales de riesgo
    umbral_riesgo_alto: float = 0.7
    umbral_riesgo_medio: float = 0.4
    umbral_uso_excesivo_horas: int = 20
    
    # Frecuencias
    frecuencia_revision_automatica: int = 24  # horas
    frecuencia_limpiar_cache: int = 3600  # segundos
    
    # Datos históricos
    dias_historial_analisis: int = 365
    min_mantenimientos_para_prediccion: int = 3
    
    # Factores de ajuste
    factor_calibracion: float = 1.2
    factor_uso_intensivo: float = 1.5
    factor_equipo_antiguo: float = 1.3

@dataclass
class ConfiguracionNotificaciones:
    """Configuración completa del sistema de notificaciones"""
    # Habilitación de canales
    habilitar_email: bool = False
    habilitar_dashboard: bool = True
    habilitar_sms: bool = False
    habilitar_webhook: bool = False
    
    # Configuraciones específicas
    email: ConfiguracionEmail = None
    dashboard: ConfiguracionDashboard = None
    sms: ConfiguracionSMS = None
    webhook: ConfiguracionWebhook = None
    mantenimiento: ConfiguracionMantenimiento = None
    
    # Prioridades por tipo de alerta
    prioridades_por_tipo: Dict[str, NivelPrioridad] = None
    
    # Reglas de envío
    enviar_solo_horario_laboral: bool = False
    horario_laboral_inicio: str = "08:00"
    horario_laboral_fin: str = "18:00"
    dias_laborales: List[str] = None
    
    # Destinatarios por defecto
    administradores: List[str] = None
    instructores: List[str] = None
    
    def __post_init__(self):
        # Inicializar configuraciones por defecto
        if self.email is None:
            self.email = ConfiguracionEmail()
        if self.dashboard is None:
            self.dashboard = ConfiguracionDashboard()
        if self.sms is None:
            self.sms = ConfiguracionSMS()
        if self.webhook is None:
            self.webhook = ConfiguracionWebhook()
        if self.mantenimiento is None:
            self.mantenimiento = ConfiguracionMantenimiento()
        if self.prioridades_por_tipo is None:
            self.prioridades_por_tipo = {
                'mantenimiento_vencido': NivelPrioridad.CRITICA,
                'equipo_critico': NivelPrioridad.CRITICA,
                'calibracion_vencida': NivelPrioridad.ALTA,
                'mantenimiento_proximo': NivelPrioridad.MEDIA,
                'tendencia_fallas': NivelPrioridad.MEDIA,
                'uso_excesivo': NivelPrioridad.BAJA
            }
        if self.dias_laborales is None:
            self.dias_laborales = ["lunes", "martes", "miércoles", "jueves", "viernes"]
        if self.administradores is None:
            self.administradores = []
        if self.instructores is None:
            self.instructores = []

def cargar_configuracion_desde_env() -> ConfiguracionNotificaciones:
    """
    Cargar configuración desde variables de entorno
    
    Returns:
        ConfiguracionNotificaciones con valores desde .env
    """
    # Configuración de email
    email_config = ConfiguracionEmail(
        servidor=os.getenv('EMAIL_SERVIDOR', 'smtp.gmail.com'),
        puerto=int(os.getenv('EMAIL_PUERTO', '587')),
        usuario=os.getenv('EMAIL_USUARIO', ''),
        password=os.getenv('EMAIL_PASSWORD', ''),
        remitente=os.getenv('EMAIL_REMITENTE', 'sistema@sena.edu.co'),
        nombre_remitente=os.getenv('EMAIL_NOMBRE_REMITENTE', 'Sistema de Laboratorios SENA'),
        usar_tls=os.getenv('EMAIL_USAR_TLS', 'true').lower() == 'true',
        usar_ssl=os.getenv('EMAIL_USAR_SSL', 'false').lower() == 'true',
        max_emails_por_hora=int(os.getenv('EMAIL_MAX_POR_HORA', '100')),
        max_destinatarios_por_email=int(os.getenv('EMAIL_MAX_DESTINATARIOS', '50'))
    )
    
    # Configuración de mantenimiento
    mantenimiento_config = ConfiguracionMantenimiento(
        dias_anticipacion_mantenimiento=int(os.getenv('DIAS_ANTICIPACION_MANTENIMIENTO', '30')),
        dias_anticipacion_calibracion=int(os.getenv('DIAS_ANTICIPACION_CALIBRACION', '15')),
        dias_anticipacion_critico=int(os.getenv('DIAS_ANTICIPACION_CRITICO', '7')),
        umbral_riesgo_alto=float(os.getenv('UMBRAL_RIESGO_ALTO', '0.7')),
        umbral_riesgo_medio=float(os.getenv('UMBRAL_RIESGO_MEDIO', '0.4')),
        umbral_uso_excesivo_horas=int(os.getenv('UMBRAL_USO_EXCESIVO', '20')),
        frecuencia_revision_automatica=int(os.getenv('FRECUENCIA_REVISION', '24')),
        dias_historial_analisis=int(os.getenv('DIAS_HISTORIAL', '365')),
        min_mantenimientos_para_prediccion=int(os.getenv('MIN_MANTENIMIENTOS_PREDICCION', '3')),
        factor_calibracion=float(os.getenv('FACTOR_CALIBRACION', '1.2')),
        factor_uso_intensivo=float(os.getenv('FACTOR_USO_INTENSIVO', '1.5')),
        factor_equipo_antiguo=float(os.getenv('FACTOR_EQUIPO_ANTIGUO', '1.3'))
    )
    
    # Configuración de dashboard
    dashboard_config = ConfiguracionDashboard(
        mostrar_alertas_criticas_primero=os.getenv('DASHBOARD_CRITICAS_PRIMERO', 'true').lower() == 'true',
        max_alertas_mostradas=int(os.getenv('DASHBOARD_MAX_ALERTAS', '50')),
        auto_actualizar_cada=int(os.getenv('DASHBOARD_AUTO_ACTUALIZAR', '300')),
        mostrar_solo_no_leidas=os.getenv('DASHBOARD_SOLO_NO_LEIDAS', 'false').lower() == 'true',
        agrupar_por_tipo=os.getenv('DASHBOARD_AGRUPAR_TIPO', 'true').lower() == 'true'
    )
    
    # Configuración SMS (si está habilitado)
    sms_config = ConfiguracionSMS(
        proveedor=os.getenv('SMS_PROVEEDOR', 'twilio'),
        api_key=os.getenv('SMS_API_KEY', ''),
        api_secret=os.getenv('SMS_API_SECRET', ''),
        numero_remitente=os.getenv('SMS_REMITENTE', ''),
        max_sms_por_dia=int(os.getenv('SMS_MAX_POR_DIA', '100')),
        solo_alertas_criticas=os.getenv('SMS_SOLO_CRITICAS', 'true').lower() == 'true'
    )
    
    # Configuración Webhook
    webhook_config = ConfiguracionWebhook(
        urls=os.getenv('WEBHOOK_URLS', '').split(',') if os.getenv('WEBHOOK_URLS') else [],
        headers=json.loads(os.getenv('WEBHOOK_HEADERS', '{}')) if os.getenv('WEBHOOK_HEADERS') else {},
        timeout=int(os.getenv('WEBHOOK_TIMEOUT', '30')),
        reintentos=int(os.getenv('WEBHOOK_REINTENTOS', '3')),
        solo_alertas_criticas=os.getenv('WEBHOOK_SOLO_CRITICAS', 'false').lower() == 'true'
    )
    
    # Configuración completa
    return ConfiguracionNotificaciones(
        habilitar_email=os.getenv('HABILITAR_EMAIL', 'false').lower() == 'true',
        habilitar_dashboard=os.getenv('HABILITAR_DASHBOARD', 'true').lower() == 'true',
        habilitar_sms=os.getenv('HABILITAR_SMS', 'false').lower() == 'true',
        habilitar_webhook=os.getenv('HABILITAR_WEBHOOK', 'false').lower() == 'true',
        email=email_config,
        dashboard=dashboard_config,
        sms=sms_config,
        webhook=webhook_config,
        mantenimiento=mantenimiento_config,
        enviar_solo_horario_laboral=os.getenv('ENVIAR_SOLO_LABORAL', 'false').lower() == 'true',
        horario_laboral_inicio=os.getenv('HORARIO_LABORAL_INICIO', '08:00'),
        horario_laboral_fin=os.getenv('HORARIO_LABORAL_FIN', '18:00'),
        dias_laborales=os.getenv('DIAS_LABORALES', 'lunes,martes,miércoles,jueves,viernes').split(','),
        administradores=os.getenv('ADMINISTRADORES', '').split(',') if os.getenv('ADMINISTRADORES') else [],
        instructores=os.getenv('INSTRUCTORES', '').split(',') if os.getenv('INSTRUCTORES') else []
    )

def guardar_configuracion_en_env(config: ConfiguracionNotificaciones, archivo_env: str = '.env'):
    """
    Guardar configuración en archivo .env
    
    Args:
        config: Configuración a guardar
        archivo_env: Ruta del archivo .env
    """
    import json
    
    lines = []
    
    # Email
    lines.append("# Configuración de Email")
    lines.append(f"HABILITAR_EMAIL={'true' if config.habilitar_email else 'false'}")
    lines.append(f"EMAIL_SERVIDOR={config.email.servidor}")
    lines.append(f"EMAIL_PUERTO={config.email.puerto}")
    lines.append(f"EMAIL_USUARIO={config.email.usuario}")
    lines.append(f"EMAIL_PASSWORD={config.email.password}")
    lines.append(f"EMAIL_REMITENTE={config.email.remitente}")
    lines.append(f"EMAIL_NOMBRE_REMITENTE={config.email.nombre_remitente}")
    lines.append(f"EMAIL_USAR_TLS={'true' if config.email.usar_tls else 'false'}")
    lines.append(f"EMAIL_USAR_SSL={'true' if config.email.usar_ssl else 'false'}")
    lines.append(f"EMAIL_MAX_POR_HORA={config.email.max_emails_por_hora}")
    lines.append(f"EMAIL_MAX_DESTINATARIOS={config.email.max_destinatarios_por_email}")
    lines.append("")
    
    # Mantenimiento
    lines.append("# Configuración de Mantenimiento")
    lines.append(f"DIAS_ANTICIPACION_MANTENIMIENTO={config.mantenimiento.dias_anticipacion_mantenimiento}")
    lines.append(f"DIAS_ANTICIPACION_CALIBRACION={config.mantenimiento.dias_anticipacion_calibracion}")
    lines.append(f"DIAS_ANTICIPACION_CRITICO={config.mantenimiento.dias_anticipacion_critico}")
    lines.append(f"UMBRAL_RIESGO_ALTO={config.mantenimiento.umbral_riesgo_alto}")
    lines.append(f"UMBRAL_RIESGO_MEDIO={config.mantenimiento.umbral_riesgo_medio}")
    lines.append(f"UMBRAL_USO_EXCESIVO={config.mantenimiento.umbral_uso_excesivo_horas}")
    lines.append(f"FRECUENCIA_REVISION={config.mantenimiento.frecuencia_revision_automatica}")
    lines.append(f"DIAS_HISTORIAL={config.mantenimiento.dias_historial_analisis}")
    lines.append(f"MIN_MANTENIMIENTOS_PREDICCION={config.mantenimiento.min_mantenimientos_para_prediccion}")
    lines.append(f"FACTOR_CALIBRACION={config.mantenimiento.factor_calibracion}")
    lines.append(f"FACTOR_USO_INTENSIVO={config.mantenimiento.factor_uso_intensivo}")
    lines.append(f"FACTOR_EQUIPO_ANTIGUO={config.mantenimiento.factor_equipo_antiguo}")
    lines.append("")
    
    # Dashboard
    lines.append("# Configuración de Dashboard")
    lines.append(f"HABILITAR_DASHBOARD={'true' if config.habilitar_dashboard else 'false'}")
    lines.append(f"DASHBOARD_CRITICAS_PRIMERO={'true' if config.dashboard.mostrar_alertas_criticas_primero else 'false'}")
    lines.append(f"DASHBOARD_MAX_ALERTAS={config.dashboard.max_alertas_mostradas}")
    lines.append(f"DASHBOARD_AUTO_ACTUALIZAR={config.dashboard.auto_actualizar_cada}")
    lines.append(f"DASHBOARD_SOLO_NO_LEIDAS={'true' if config.dashboard.mostrar_solo_no_leidas else 'false'}")
    lines.append(f"DASHBOARD_AGRUPAR_TIPO={'true' if config.dashboard.agrupar_por_tipo else 'false'}")
    lines.append("")
    
    # SMS
    lines.append("# Configuración de SMS")
    lines.append(f"HABILITAR_SMS={'true' if config.habilitar_sms else 'false'}")
    lines.append(f"SMS_PROVEEDOR={config.sms.proveedor}")
    lines.append(f"SMS_API_KEY={config.sms.api_key}")
    lines.append(f"SMS_API_SECRET={config.sms.api_secret}")
    lines.append(f"SMS_REMITENTE={config.sms.numero_remitente}")
    lines.append(f"SMS_MAX_POR_DIA={config.sms.max_sms_por_dia}")
    lines.append(f"SMS_SOLO_CRITICAS={'true' if config.sms.solo_alertas_criticas else 'false'}")
    lines.append("")
    
    # Webhook
    lines.append("# Configuración de Webhook")
    lines.append(f"HABILITAR_WEBHOOK={'true' if config.habilitar_webhook else 'false'}")
    lines.append(f"WEBHOOK_URLS={','.join(config.webhook.urls)}")
    lines.append(f"WEBHOOK_HEADERS={json.dumps(config.webhook.headers)}")
    lines.append(f"WEBHOOK_TIMEOUT={config.webhook.timeout}")
    lines.append(f"WEBHOOK_REINTENTOS={config.webhook.reintentos}")
    lines.append(f"WEBHOOK_SOLO_CRITICAS={'true' if config.webhook.solo_alertas_criticas else 'false'}")
    lines.append("")
    
    # General
    lines.append("# Configuración General")
    lines.append(f"ENVIAR_SOLO_LABORAL={'true' if config.enviar_solo_horario_laboral else 'false'}")
    lines.append(f"HORARIO_LABORAL_INICIO={config.horario_laboral_inicio}")
    lines.append(f"HORARIO_LABORAL_FIN={config.horario_laboral_fin}")
    lines.append(f"DIAS_LABORALES={','.join(config.dias_laborales)}")
    lines.append(f"ADMINISTRADORES={','.join(config.administradores)}")
    lines.append(f"INSTRUCTORES={','.join(config.instructores)}")
    
    # Escribir archivo
    with open(archivo_env, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def validar_configuracion(config: ConfiguracionNotificaciones) -> List[str]:
    """
    Validar configuración y retornar errores encontrados
    
    Args:
        config: Configuración a validar
        
    Returns:
        Lista de errores encontrados
    """
    errores = []
    
    # Validar email
    if config.habilitar_email:
        if not config.email.usuario:
            errores.append("Email habilitado pero no se configuró usuario")
        if not config.email.password:
            errores.append("Email habilitado pero no se configuró contraseña")
        if not config.email.remitente:
            errores.append("Email habilitado pero no se configuró remitente")
        if config.email.puerto <= 0:
            errores.append("Puerto de email inválido")
    
    # Validar SMS
    if config.habilitar_sms:
        if not config.sms.api_key:
            errores.append("SMS habilitado pero no se configuró API key")
        if not config.sms.numero_remitente:
            errores.append("SMS habilitado pero no se configuró número remitente")
    
    # Validar Webhook
    if config.habilitar_webhook:
        if not config.webhook.urls:
            errores.append("Webhook habilitado pero no se configuraron URLs")
    
    # Validar mantenimiento
    if config.mantenimiento.dias_anticipacion_mantenimiento <= 0:
        errores.append("Días de anticipación de mantenimiento deben ser positivos")
    if config.mantenimiento.umbral_riesgo_alto < 0 or config.mantenimiento.umbral_riesgo_alto > 1:
        errores.append("Umbral de riesgo alto debe estar entre 0 y 1")
    if config.mantenimiento.umbral_riesgo_medio < 0 or config.mantenimiento.umbral_riesgo_medio > 1:
        errores.append("Umbral de riesgo medio debe estar entre 0 y 1")
    if config.mantenimiento.umbral_riesgo_medio >= config.mantenimiento.umbral_riesgo_alto:
        errores.append("Umbral de riesgo medio debe ser menor que umbral de riesgo alto")
    
    # Validar horarios
    try:
        from datetime import datetime
        datetime.strptime(config.horario_laboral_inicio, '%H:%M')
        datetime.strptime(config.horario_laboral_fin, '%H:%M')
    except ValueError:
        errores.append("Formato de horario laboral inválido (usar HH:MM)")
    
    return errores

# Configuración por defecto para desarrollo
CONFIGURACION_DEFECTO = ConfiguracionNotificaciones(
    habilitar_email=False,
    habilitar_dashboard=True,
    habilitar_sms=False,
    habilitar_webhook=False,
    mantenimiento=ConfiguracionMantenimiento(
        dias_anticipacion_mantenimiento=30,
        dias_anticipacion_calibracion=15,
        dias_anticipacion_critico=7,
        umbral_riesgo_alto=0.7,
        umbral_riesgo_medio=0.4,
        umbral_uso_excesivo_horas=20,
        frecuencia_revision_automatica=24,
        dias_historial_analisis=365,
        min_mantenimientos_para_prediccion=3
    )
)

if __name__ == "__main__":
    # Prueba del módulo de configuración
    print("📋 Módulo de Configuración de Notificaciones")
    print("✅ Clases definidas correctamente")
    
    # Probar carga desde entorno
    try:
        config = cargar_configuracion_desde_env()
        print("✅ Configuración cargada desde variables de entorno")
        
        # Validar configuración
        errores = validar_configuracion(config)
        if errores:
            print("⚠️ Errores de configuración:")
            for error in errores:
                print(f"   - {error}")
        else:
            print("✅ Configuración válida")
            
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
    
    print("📧 Sistema de notificaciones listo para configurar")

# -*- coding: utf-8 -*-
"""
Configuración de Módulos por Nivel de Acceso
Sistema de Gestión de Laboratorios - Centro Minero SENA

Define qué módulos y funciones están disponibles según el nivel de usuario.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class CategoriaModulo(Enum):
    """Categorías de módulos para mejor organización"""
    GESTION = "gestion"
    OPERACION = "operacion"
    REPORTES = "reportes"
    ADMINISTRACION = "administracion"
    SEGURIDAD = "seguridad"
    IA = "ia"

@dataclass
class ModuloConfig:
    """Configuración de un módulo"""
    id: str
    nombre: str
    descripcion: str
    icono: str
    categoria: CategoriaModulo
    url: str
    nivel_minimo: int
    caracteristicas: List[str]
    color: str = "primary"
    requerimientos: Optional[List[str]] = None

# Definición de módulos del sistema
MODULOS_SISTEMA = {
    # Módulos de Operación (acceso básico)
    "laboratorios": ModuloConfig(
        id="laboratorios",
        nombre="Laboratorios",
        descripcion="Gestionar laboratorios y espacios",
        icono="bi-building",
        categoria=CategoriaModulo.OPERACION,
        url="/laboratorios",
        nivel_minimo=1,  # Todos los usuarios
        caracteristicas=["Ver laboratorios", "Consultar disponibilidad"],
        color="info"
    ),
    
    "equipos": ModuloConfig(
        id="equipos",
        nombre="Equipos",
        descripcion="Ver y consultar equipos disponibles",
        icono="bi-cpu",
        categoria=CategoriaModulo.OPERACION,
        url="/equipos",
        nivel_minimo=1,  # Todos los usuarios
        caracteristicas=["Ver equipos", "Consultar estado", "Predicción IA"],
        color="warning"
    ),
    
    "reservas": ModuloConfig(
        id="reservas",
        nombre="Reservas",
        descripcion="Gestionar reservas de equipos",
        icono="bi-calendar-check",
        categoria=CategoriaModulo.OPERACION,
        url="/reservas",
        nivel_minimo=1,  # Todos los usuarios
        caracteristicas=["Ver reservas", "Crear reservas"],
        color="success"
    ),
    
    # Módulos de Gestión (nivel intermedio)
    "inventario": ModuloConfig(
        id="inventario",
        nombre="Inventario",
        descripcion="Gestionar inventario de materiales",
        icono="bi-box-seam",
        categoria=CategoriaModulo.GESTION,
        url="/inventario",
        nivel_minimo=3,  # Instructor en adelante
        caracteristicas=["Ver inventario", "Gestionar stock", "Ajustes"],
        color="secondary"
    ),
    
    "registro_completo": ModuloConfig(
        id="registro_completo",
        nombre="Registro con IA",
        descripcion="Registrar equipos/items con fotos",
        icono="bi-plus-circle",
        categoria=CategoriaModulo.GESTION,
        url="/registro_completo",
        nivel_minimo=4,  # Instructor en adelante
        caracteristicas=["Registro con fotos", "Reconocimiento IA", "Validación automática"],
        color="sena"
    ),
    
    # Módulos de Reportes (nivel intermedio-alto)
    "reportes": ModuloConfig(
        id="reportes",
        nombre="Reportes",
        descripcion="Ver estadísticas y reportes",
        icono="bi-graph-up",
        categoria=CategoriaModulo.REPORTES,
        url="/reportes",
        nivel_minimo=3,  # Instructor en adelante
        caracteristicas=["Estadísticas", "Reportes de uso", "Análisis de datos"],
        color="secondary"
    ),
    
    # Módulos de IA (requieren permisos especiales)
    "facial": ModuloConfig(
        id="facial",
        nombre="Registro Facial",
        descripcion="Registrar rostros para reconocimiento",
        icono="bi-person-check",
        categoria=CategoriaModulo.SEGURIDAD,
        url="/facial",
        nivel_minimo=4,  # Instructor en adelante
        caracteristicas=["Reconocimiento facial", "Registro biométrico"],
        color="primary",
        requerimientos=["camara_web"]
    ),
    
    "visual": ModuloConfig(
        id="visual",
        nombre="IA Visual",
        descripcion="Entrenar reconocimiento visual",
        icono="bi-eye",
        categoria=CategoriaModulo.IA,
        url="/visual",
        nivel_minimo=5,  # Instructor inventario en adelante
        caracteristicas=["Entrenamiento IA", "Reconocimiento de objetos", "Modelos personalizados"],
        color="danger",
        requerimientos=["datos_entrenamiento"]
    ),
    
    # Módulos de Administración (solo administradores)
    "usuarios": ModuloConfig(
        id="usuarios",
        nombre="Gestión de Usuarios",
        descripcion="Administrar usuarios del sistema",
        icono="bi-people",
        categoria=CategoriaModulo.ADMINISTRACION,
        url="/usuarios",
        nivel_minimo=6,  # Solo administradores
        caracteristicas=["Crear usuarios", "Gestionar permisos", "Control de acceso"],
        color="primary"
    ),
    
    "configuracion": ModuloConfig(
        id="configuracion",
        nombre="Configuración",
        descripcion="Ajustes del sistema",
        icono="bi-gear",
        categoria=CategoriaModulo.ADMINISTRACION,
        url="/configuracion",
        nivel_minimo=4,  # Instructor en adelante
        caracteristicas=["Configuración general", "Ajustes de sistema"],
        color="dark"
    ),
    
    "backup": ModuloConfig(
        id="backup",
        nombre="Backup BD",
        descripcion="Respaldar base de datos",
        icono="bi-database",
        categoria=CategoriaModulo.ADMINISTRACION,
        url="/backup",
        nivel_minimo=6,  # Solo administradores
        caracteristicas=["Backup automático", "Restauración", "Exportación"],
        color="warning"
    ),
}

# Configuración de acciones rápidas por nivel
ACCIONES_RAPIDAS = {
    1: [  # Aprendiz
        {
            "id": "ver_equipos",
            "nombre": "Ver Equipos",
            "descripcion": "Consultar equipos disponibles",
            "icono": "bi-cpu",
            "url": "/equipos",
            "color": "warning"
        }
    ],
    2: [  # Funcionario
        {
            "id": "ver_equipos",
            "nombre": "Ver Equipos",
            "descripcion": "Consultar equipos disponibles",
            "icono": "bi-cpu",
            "url": "/equipos",
            "color": "warning"
        },
        {
            "id": "reservar_equipo",
            "nombre": "Reservar Equipo",
            "descripcion": "Reservar equipos para uso",
            "icono": "bi-calendar-check",
            "url": "/reservas",
            "color": "success"
        }
    ],
    3: [  # Instructor (No Química)
        {
            "id": "ver_equipos",
            "nombre": "Ver Equipos",
            "descripcion": "Consultar equipos disponibles",
            "icono": "bi-cpu",
            "url": "/equipos",
            "color": "warning"
        },
        {
            "id": "reservar_equipo",
            "nombre": "Reservar Equipo",
            "descripcion": "Reservar equipos para uso",
            "icono": "bi-calendar-check",
            "url": "/reservas",
            "color": "success"
        },
        {
            "id": "ver_reportes",
            "nombre": "Ver Reportes",
            "descripcion": "Consultar estadísticas",
            "icono": "bi-graph-up",
            "url": "/reportes",
            "color": "secondary"
        }
    ],
    4: [  # Instructor (Química)
        {
            "id": "registro_equipo",
            "nombre": "Registrar Equipo/Item",
            "descripcion": "Registro con fotos e IA",
            "icono": "bi-plus-circle",
            "url": "/registro_completo",
            "color": "sena"
        },
        {
            "id": "registro_facial",
            "nombre": "Registro Facial",
            "descripcion": "Registrar rostro",
            "icono": "bi-person-check",
            "url": "/facial",
            "color": "primary"
        },
        {
            "id": "configuracion",
            "nombre": "Configuración",
            "descripcion": "Ajustes del sistema",
            "icono": "bi-gear",
            "url": "/configuracion",
            "color": "dark"
        }
    ],
    5: [  # Instructor a cargo de Inventario
        {
            "id": "registro_equipo",
            "nombre": "Registrar Equipo/Item",
            "descripcion": "Registro con fotos e IA",
            "icono": "bi-plus-circle",
            "url": "/registro_completo",
            "color": "sena"
        },
        {
            "id": "gestionar_inventario",
            "nombre": "Gestionar Inventario",
            "descripcion": "Ajustar stock y materiales",
            "icono": "bi-box-seam",
            "url": "/inventario",
            "color": "secondary"
        },
        {
            "id": "ia_visual",
            "nombre": "IA Visual",
            "descripcion": "Entrenar reconocimiento",
            "icono": "bi-eye",
            "url": "/visual",
            "color": "danger"
        }
    ],
    6: [  # Administrador
        {
            "id": "registro_equipo",
            "nombre": "Registrar Equipo/Item",
            "descripcion": "Registro con fotos e IA",
            "icono": "bi-plus-circle",
            "url": "/registro_completo",
            "color": "sena"
        },
        {
            "id": "gestionar_usuarios",
            "nombre": "Gestionar Usuarios",
            "descripcion": "Administrar usuarios",
            "icono": "bi-people",
            "url": "/usuarios",
            "color": "primary"
        },
        {
            "id": "backup_bd",
            "nombre": "Backup BD",
            "descripcion": "Respaldar base de datos",
            "icono": "bi-database",
            "url": "/backup",
            "color": "warning"
        }
    ]
}

# Estadísticas visibles por nivel
ESTADISTICAS_POR_NIVEL = {
    1: ["equipos_activos", "total_laboratorios"],  # Aprendiz
    2: ["equipos_activos", "total_laboratorios", "items_criticos"],  # Funcionario
    3: ["equipos_activos", "total_laboratorios", "items_criticos", "reservas_proximas"],  # Instructor
    4: ["equipos_activos", "total_laboratorios", "items_criticos", "reservas_proximas"],  # Instructor Química
    5: ["equipos_activos", "total_laboratorios", "items_criticos", "reservas_proximas", "movimientos_inventario"],  # Instructor Inventario
    6: ["equipos_activos", "total_laboratorios", "items_criticos", "reservas_proximas", "movimientos_inventario", "usuarios_activos"]  # Administrador
}

class ModulosManager:
    """Gestor de módulos con control de acceso"""
    
    @staticmethod
    def obtener_modulos_usuario(nivel_usuario: int) -> List[ModuloConfig]:
        """
        Obtener módulos disponibles para un nivel de usuario
        
        Args:
            nivel_usuario: Nivel del usuario (1-6)
            
        Returns:
            Lista de módulos configurados para el usuario
        """
        modulos_disponibles = []
        
        for modulo_id, modulo_config in MODULOS_SISTEMA.items():
            if nivel_usuario >= modulo_config.nivel_minimo:
                # Verificar requisitos especiales si existen
                if ModulosManager._verificar_requisitos(modulo_config, nivel_usuario):
                    modulos_disponibles.append(modulo_config)
        
        # Ordenar por categoría y nombre
        modulos_disponibles.sort(key=lambda m: (m.categoria.value, m.nombre))
        
        return modulos_disponibles
    
    @staticmethod
    def obtener_acciones_rapidas(nivel_usuario: int) -> List[Dict]:
        """
        Obtener acciones rápidas para un nivel de usuario
        
        Args:
            nivel_usuario: Nivel del usuario (1-6)
            
        Returns:
            Lista de acciones rápidas configuradas
        """
        return ACCIONES_RAPIDAS.get(nivel_usuario, [])
    
    @staticmethod
    def obtener_estadisticas_usuario(nivel_usuario: int) -> List[str]:
        """
        Obtener estadísticas visibles para un nivel de usuario
        
        Args:
            nivel_usuario: Nivel del usuario (1-6)
            
        Returns:
            Lista de claves de estadísticas
        """
        return ESTADISTICAS_POR_NIVEL.get(nivel_usuario, [])
    
    @staticmethod
    def puede_acceder_modulo(modulo_id: str, nivel_usuario: int) -> bool:
        """
        Verificar si un usuario puede acceder a un módulo específico
        
        Args:
            modulo_id: ID del módulo
            nivel_usuario: Nivel del usuario
            
        Returns:
            True si puede acceder, False si no
        """
        if modulo_id not in MODULOS_SISTEMA:
            return False
        
        modulo = MODULOS_SISTEMA[modulo_id]
        
        if nivel_usuario < modulo.nivel_minimo:
            return False
        
        return ModulosManager._verificar_requisitos(modulo, nivel_usuario)
    
    @staticmethod
    def _verificar_requisitos(modulo: ModuloConfig, nivel_usuario: int) -> bool:
        """
        Verificar requisitos especiales del módulo
        
        Args:
            modulo: Configuración del módulo
            nivel_usuario: Nivel del usuario
            
        Returns:
            True si cumple requisitos, False si no
        """
        if not modulo.requerimientos:
            return True
        
        # Aquí se pueden agregar verificaciones especiales
        # Por ahora, todos los requisitos se consideran cumplidos
        # Se puede expandir para verificar hardware, permisos especiales, etc.
        
        return True
    
    @staticmethod
    def obtener_modulos_por_categoria(nivel_usuario: int) -> Dict[str, List[ModuloConfig]]:
        """
        Obtener módulos agrupados por categoría
        
        Args:
            nivel_usuario: Nivel del usuario
            
        Returns:
            Diccionario con módulos agrupados por categoría
        """
        modulos = ModulosManager.obtener_modulos_usuario(nivel_usuario)
        
        categorias = {}
        for modulo in modulos:
            categoria = modulo.categoria.value
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(modulo)
        
        return categorias
    
    @staticmethod
    def obtener_info_modulo(modulo_id: str) -> Optional[ModuloConfig]:
        """
        Obtener información completa de un módulo
        
        Args:
            modulo_id: ID del módulo
            
        Returns:
            Configuración del módulo o None si no existe
        """
        return MODULOS_SISTEMA.get(modulo_id)

# Funciones de ayuda para templates
def get_modulos_disponibles(nivel_usuario: int) -> List[ModuloConfig]:
    """Función helper para templates"""
    return ModulosManager.obtener_modulos_usuario(nivel_usuario)

def get_acciones_rapidas_disponibles(nivel_usuario: int) -> List[Dict]:
    """Función helper para templates"""
    return ModulosManager.obtener_acciones_rapidas(nivel_usuario)

def get_estadisticas_disponibles(nivel_usuario: int) -> List[str]:
    """Función helper para templates"""
    return ModulosManager.obtener_estadisticas_usuario(nivel_usuario)

def puede_ver_modulo(modulo_id: str, nivel_usuario: int) -> bool:
    """Función helper para templates"""
    return ModulosManager.puede_acceder_modulo(modulo_id, nivel_usuario)

if __name__ == "__main__":
    # Prueba del sistema de módulos
    print("🔧 Sistema de Módulos por Nivel de Acceso")
    print("=" * 50)
    
    # Probar para cada nivel
    for nivel in range(1, 7):
        modulos = ModulosManager.obtener_modulos_usuario(nivel)
        acciones = ModulosManager.obtener_acciones_rapidas(nivel)
        stats = ModulosManager.obtener_estadisticas_usuario(nivel)
        
        print(f"\n📋 Nivel {nivel} ({ROLES_NOMBRES.get(nivel, 'Desconocido')}):")
        print(f"   Módulos: {len(modulos)}")
        print(f"   Acciones rápidas: {len(acciones)}")
        print(f"   Estadísticas: {len(stats)}")
    
    print("\n✅ Sistema de módulos funcionando correctamente")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Notificaciones
Maneja el envío y gestión de notificaciones a usuarios del sistema
"""

from datetime import datetime
from typing import List, Dict, Optional
import json


class NotificacionesManager:
    """Gestor de notificaciones del sistema"""
    
    def __init__(self, db_manager):
        """
        Inicializar el gestor de notificaciones
        
        Args:
            db_manager: Instancia del gestor de base de datos
        """
        self.db = db_manager
    
    def crear_notificacion(
        self,
        tipo: str,
        titulo: str,
        mensaje: str,
        destinatario_id: str,
        remitente_id: Optional[str] = None,
        referencia_tipo: Optional[str] = None,
        referencia_id: Optional[str] = None,
        prioridad: str = 'normal',
        accion_url: Optional[str] = None,
        metadatos: Optional[Dict] = None
    ) -> bool:
        """
        Crear una nueva notificación
        
        Args:
            tipo: Tipo de notificación (reserva_nueva, reserva_aprobada, etc.)
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            destinatario_id: ID del usuario destinatario
            remitente_id: ID del usuario remitente (opcional)
            referencia_tipo: Tipo de referencia (reserva, equipo, etc.)
            referencia_id: ID de la referencia
            prioridad: Prioridad de la notificación (baja, normal, alta, urgente)
            accion_url: URL para acción relacionada (opcional)
            metadatos: Información adicional en JSON (opcional)
        
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            query = """
                INSERT INTO notificaciones (
                    tipo, titulo, mensaje, destinatario_id, remitente_id,
                    referencia_tipo, referencia_id, prioridad, accion_url, metadatos
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            metadatos_json = json.dumps(metadatos) if metadatos else None
            
            self.db.execute_query(query, (
                tipo, titulo, mensaje, destinatario_id, remitente_id,
                referencia_tipo, referencia_id, prioridad, accion_url, metadatos_json
            ))
            
            return True
        except Exception as e:
            print(f"Error creando notificación: {e}")
            return False
    
    def notificar_nueva_reserva(
        self,
        reserva_id: str,
        usuario_id: str,
        equipo_nombre: str,
        fecha_inicio: str,
        fecha_fin: str,
        laboratorio_id: Optional[int] = None
    ) -> bool:
        """
        Notificar a instructores a cargo sobre una nueva reserva
        
        Args:
            reserva_id: ID de la reserva
            usuario_id: ID del usuario que hizo la reserva
            equipo_nombre: Nombre del equipo reservado
            fecha_inicio: Fecha de inicio de la reserva
            fecha_fin: Fecha de fin de la reserva
            laboratorio_id: ID del laboratorio (opcional, para filtrar instructores)
        
        Returns:
            bool: True si se enviaron notificaciones exitosamente
        """
        try:
            # Obtener información del usuario que reservó
            query_usuario = "SELECT nombre, programa FROM usuarios WHERE id = %s"
            usuario = self.db.execute_query(query_usuario, (usuario_id,))
            
            if not usuario:
                return False
            
            usuario_nombre = usuario[0]['nombre']
            usuario_programa = usuario[0].get('programa', 'N/A')
            
            # Obtener instructores a cargo del inventario
            if laboratorio_id:
                query_instructores = """
                    SELECT id, nombre, email 
                    FROM usuarios 
                    WHERE a_cargo_inventario = 1 
                    AND activo = 1 
                    AND (laboratorio_id = %s OR laboratorio_id IS NULL)
                    AND nivel_acceso >= 5
                """
                instructores = self.db.execute_query(query_instructores, (laboratorio_id,))
            else:
                query_instructores = """
                    SELECT id, nombre, email 
                    FROM usuarios 
                    WHERE a_cargo_inventario = 1 
                    AND activo = 1
                    AND nivel_acceso >= 5
                """
                instructores = self.db.execute_query(query_instructores)
            
            if not instructores:
                print("No se encontraron instructores a cargo del inventario")
                return False
            
            # Crear notificación para cada instructor
            titulo = f"Nueva reserva pendiente de aprobación"
            mensaje = (
                f"{usuario_nombre} ({usuario_programa}) ha solicitado reservar "
                f"'{equipo_nombre}' desde {fecha_inicio} hasta {fecha_fin}. "
                f"Por favor, revisa y responde a esta solicitud."
            )
            
            metadatos = {
                'reserva_id': reserva_id,
                'usuario_nombre': usuario_nombre,
                'equipo_nombre': equipo_nombre,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
            
            notificaciones_enviadas = 0
            for instructor in instructores:
                if self.crear_notificacion(
                    tipo='reserva_nueva',
                    titulo=titulo,
                    mensaje=mensaje,
                    destinatario_id=instructor['id'],
                    remitente_id=usuario_id,
                    referencia_tipo='reserva',
                    referencia_id=reserva_id,
                    prioridad='alta',
                    accion_url=f'/reservas?id={reserva_id}',
                    metadatos=metadatos
                ):
                    notificaciones_enviadas += 1
            
            print(f"✓ {notificaciones_enviadas} notificaciones enviadas a instructores")
            return notificaciones_enviadas > 0
            
        except Exception as e:
            print(f"Error notificando nueva reserva: {e}")
            return False
    
    def notificar_respuesta_reserva(
        self,
        reserva_id: str,
        usuario_id: str,
        instructor_nombre: str,
        aprobada: bool,
        motivo: Optional[str] = None
    ) -> bool:
        """
        Notificar al usuario sobre la respuesta a su reserva
        
        Args:
            reserva_id: ID de la reserva
            usuario_id: ID del usuario que hizo la reserva
            instructor_nombre: Nombre del instructor que respondió
            aprobada: True si fue aprobada, False si fue rechazada
            motivo: Motivo del rechazo (si aplica)
        
        Returns:
            bool: True si se envió la notificación
        """
        try:
            if aprobada:
                tipo = 'reserva_aprobada'
                titulo = "✓ Reserva Aprobada"
                mensaje = f"Tu reserva ha sido aprobada por {instructor_nombre}. Puedes proceder con tu actividad programada."
                prioridad = 'normal'
            else:
                tipo = 'reserva_rechazada'
                titulo = "✗ Reserva Rechazada"
                mensaje = f"Tu reserva ha sido rechazada por {instructor_nombre}."
                if motivo:
                    mensaje += f"\n\nMotivo: {motivo}"
                prioridad = 'alta'
            
            metadatos = {
                'reserva_id': reserva_id,
                'aprobada': aprobada,
                'instructor_nombre': instructor_nombre,
                'motivo': motivo
            }
            
            return self.crear_notificacion(
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                destinatario_id=usuario_id,
                referencia_tipo='reserva',
                referencia_id=reserva_id,
                prioridad=prioridad,
                accion_url=f'/reservas?id={reserva_id}',
                metadatos=metadatos
            )
            
        except Exception as e:
            print(f"Error notificando respuesta de reserva: {e}")
            return False
    
    def obtener_notificaciones_usuario(
        self,
        usuario_id: str,
        solo_no_leidas: bool = False,
        limite: int = 50
    ) -> List[Dict]:
        """
        Obtener notificaciones de un usuario
        
        Args:
            usuario_id: ID del usuario
            solo_no_leidas: Si True, solo devuelve notificaciones no leídas
            limite: Cantidad máxima de notificaciones a devolver
        
        Returns:
            Lista de notificaciones
        """
        try:
            query = """
                SELECT n.id, n.tipo, n.titulo, n.mensaje, n.leida, 
                       n.fecha_creacion, n.prioridad, n.accion_url,
                       n.referencia_tipo, n.referencia_id,
                       u.nombre as remitente_nombre
                FROM notificaciones n
                LEFT JOIN usuarios u ON n.remitente_id = u.id
                WHERE n.destinatario_id = %s
            """
            
            params = [usuario_id]
            
            if solo_no_leidas:
                query += " AND n.leida = FALSE"
            
            query += " ORDER BY n.fecha_creacion DESC LIMIT %s"
            params.append(limite)
            
            return self.db.execute_query(query, tuple(params)) or []
            
        except Exception as e:
            print(f"Error obteniendo notificaciones: {e}")
            return []
    
    def marcar_como_leida(self, notificacion_id: int) -> bool:
        """
        Marcar una notificación como leída
        
        Args:
            notificacion_id: ID de la notificación
        
        Returns:
            bool: True si se marcó exitosamente
        """
        try:
            query = """
                UPDATE notificaciones 
                SET leida = TRUE, fecha_lectura = NOW()
                WHERE id = %s
            """
            self.db.execute_query(query, (notificacion_id,))
            return True
        except Exception as e:
            print(f"Error marcando notificación como leída: {e}")
            return False
    
    def marcar_todas_como_leidas(self, usuario_id: str) -> bool:
        """
        Marcar todas las notificaciones de un usuario como leídas
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            bool: True si se marcaron exitosamente
        """
        try:
            query = """
                UPDATE notificaciones 
                SET leida = TRUE, fecha_lectura = NOW()
                WHERE destinatario_id = %s AND leida = FALSE
            """
            self.db.execute_query(query, (usuario_id,))
            return True
        except Exception as e:
            print(f"Error marcando todas las notificaciones como leídas: {e}")
            return False
    
    def contar_no_leidas(self, usuario_id: str) -> int:
        """
        Contar notificaciones no leídas de un usuario
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            int: Cantidad de notificaciones no leídas
        """
        try:
            query = """
                SELECT COUNT(*) as total 
                FROM notificaciones 
                WHERE destinatario_id = %s AND leida = FALSE
            """
            result = self.db.execute_query(query, (usuario_id,))
            return result[0]['total'] if result else 0
        except Exception as e:
            print(f"Error contando notificaciones no leídas: {e}")
            return 0
    
    def eliminar_notificacion(self, notificacion_id: int, usuario_id: str) -> bool:
        """
        Eliminar una notificación (solo si pertenece al usuario)
        
        Args:
            notificacion_id: ID de la notificación
            usuario_id: ID del usuario (para verificar permisos)
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            query = """
                DELETE FROM notificaciones 
                WHERE id = %s AND destinatario_id = %s
            """
            self.db.execute_query(query, (notificacion_id, usuario_id))
            return True
        except Exception as e:
            print(f"Error eliminando notificación: {e}")
            return False

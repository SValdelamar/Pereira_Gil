#!/usr/bin/env python3
"""
Validación mejorada para aprobación de reservas y entregas
"""

def puede_aprobar_reservas(session):
    """
    Verificar si el usuario actual puede aprobar reservas
    """
    user_level = session.get('user_level', 0)
    a_cargo_inventario = session.get('a_cargo_inventario', False)
    
    # Administrador siempre puede aprobar
    if user_level == 6:
        return True, "Administrador tiene acceso completo"
    
    # Instructor Inventario (Nivel 5) solo si está a cargo del inventario
    if user_level == 5 and a_cargo_inventario:
        return True, "Instructor de inventario autorizado"
    
    # Instructor Química (Nivel 4) solo si está a cargo del inventario
    if user_level == 4 and a_cargo_inventario:
        return True, "Instructor química con inventario a cargo"
    
    # Otros niveles no pueden aprobar
    return False, f"Nivel {user_level} no autorizado para aprobar reservas"

def puede_entregar_consumibles(session):
    """
    Verificar si el usuario actual puede entregar consumibles
    """
    user_level = session.get('user_level', 0)
    a_cargo_inventario = session.get('a_cargo_inventario', False)
    
    # Administrador siempre puede entregar
    if user_level == 6:
        return True, "Administrador tiene acceso completo"
    
    # Instructor Inventario (Nivel 5) solo si está a cargo del inventario
    if user_level == 5 and a_cargo_inventario:
        return True, "Instructor de inventario autorizado"
    
    # Instructor Química (Nivel 4) solo si está a cargo del inventario
    if user_level == 4 and a_cargo_inventario:
        return True, "Instructor química con inventario a cargo"
    
    # Otros niveles no pueden entregar
    return False, f"Nivel {user_level} no autorizado para entregar consumibles"

def decorador_aprobacion_inventario(f):
    """
    Decorador para validar que el usuario está autorizado para aprobar/entregar
    """
    from functools import wraps
    from flask import session, flash, redirect, url_for
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si puede aprobar
        puede, mensaje = puede_aprobar_reservas(session)
        if not puede:
            flash(f'⚠️ No tienes permiso para realizar esta acción: {mensaje}', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function

# Ejemplo de cómo usarlo en los endpoints
"""
@app.route('/reservas/aprobar/<reserva_id>', methods=['POST'])
@require_login
@decorador_aprobacion_inventario
def aprobar_reserva(reserva_id):
    # Lógica de aprobación
    pass

@app.route('/inventario/entregar', methods=['POST'])
@require_login
@decorador_aprobacion_inventario
def entregar_consumible():
    # Lógica de entrega
    pass
"""

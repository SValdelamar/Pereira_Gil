"""
Gestor Centralizado de Entidades (CRUD Manager)
Solución definitiva para sistema de herencia consistente
"""

class EntityManager:
    """
    Gestor centralizado para operaciones CRUD de entidades
    Reemplaza el sistema híbrido actual con una arquitectura limpia
    """
    
    def __init__(self, api_base_url, logger=None):
        self.api_base_url = api_base_url
        self.logger = logger
        
    def get_entity_config(self, entity_type):
        """Obtener configuración centralizada de entidad"""
        configs = {
            'usuario': {
                'endpoints': {
                    'get': '/api/usuarios/{id}',
                    'update': '/api/usuarios/{id}',
                    'delete': '/api/usuarios/{id}'
                },
                'messages': {
                    'confirmDelete': '¿Estás seguro de eliminar al usuario "{name}"? Esta acción no se puede deshacer.',
                    'deleteSuccess': 'Usuario eliminado correctamente',
                    'updateSuccess': 'Usuario actualizado correctamente'
                },
                'fields': {
                    'id': 'id',
                    'name': 'nombre'
                }
            },
            'laboratorio': {
                'endpoints': {
                    'get': '/api/laboratorios/{id}',
                    'update': '/api/laboratorios/{id}',
                    'delete': '/api/laboratorios/{id}'
                },
                'messages': {
                    'confirmDelete': '¿Estás seguro de eliminar el laboratorio "{name}"? Esta acción no se puede deshacer.',
                    'deleteSuccess': 'Laboratorio eliminado correctamente',
                    'updateSuccess': 'Laboratorio actualizado correctamente'
                },
                'fields': {
                    'id': 'id',
                    'name': 'nombre'
                }
            },
            'equipo': {
                'endpoints': {
                    'get': '/api/registro-editar/equipo/{id}',
                    'update': '/api/registro-actualizar/equipo/{id}',
                    'delete': '/api/registro-eliminar/equipo/{id}'
                },
                'messages': {
                    'confirmDelete': '¿Estás seguro de eliminar el equipo "{name}"? Esta acción no se puede deshacer.',
                    'deleteSuccess': 'Equipo eliminado correctamente',
                    'updateSuccess': 'Equipo actualizado correctamente'
                },
                'fields': {
                    'id': 'equipo_id',
                    'name': 'nombre'
                }
            },
            'item': {
                'endpoints': {
                    'get': '/api/registro-editar/item/{id}',
                    'update': '/api/registro-actualizar/item/{id}',
                    'delete': '/api/registro-eliminar/item/{id}'
                },
                'messages': {
                    'confirmDelete': '¿Estás seguro de eliminar el item "{name}"? Esta acción no se puede deshacer.',
                    'deleteSuccess': 'Item eliminado correctamente',
                    'updateSuccess': 'Item actualizado correctamente'
                },
                'fields': {
                    'id': 'item_id',
                    'name': 'nombre'
                }
            }
        }
        return configs.get(entity_type, {})
    
    async def get_entity(self, entity_type, entity_id):
        """Obtener datos de una entidad para edición"""
        try:
            config = self.get_entity_config(entity_type)
            url = self.api_base_url + config['endpoints']['get'].format(id=entity_id)
            
            response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {localStorage.getItem("jwt") or ""}'
                }
            })
            
            if not response.ok:
                raise Exception(f'Error {response.status}: {response.statusText}')
            
            data = await response.json()
            return data
            
        except Exception as error:
            if self.logger:
                self.logger.error(f'Error obteniendo {entity_type} {entity_id}:', error)
            raise error
    
    async def update_entity(self, entity_type, entity_id, form_data):
        """Actualizar una entidad"""
        try:
            config = self.get_entity_config(entity_type)
            url = self.api_base_url + config['endpoints']['update'].format(id=entity_id)
            
            response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {localStorage.getItem("jwt") or ""}'
                },
                body: JSON.stringify(form_data)
            })
            
            if not response.ok:
                error_data = await response.json()
                raise Exception(error_data.message or f'Error {response.status}')
            
            data = await response.json()
            
            if self.logger:
                self.logger.info(f'{entity_type} {entity_id} actualizado', data)
            
            return {
                'success': True,
                'message': config['messages']['updateSuccess'],
                'data': data
            }
            
        except Exception as error:
            if self.logger:
                self.logger.error(f'Error actualizando {entity_type} {entity_id}:', error)
            raise error
    
    async def delete_entity(self, entity_type, entity_id, entity_name):
        """Eliminar una entidad con confirmación"""
        try:
            config = self.get_entity_config(entity_type)
            
            if self.logger:
                self.logger.debug(f'Solicitando eliminación de {entity_type} {entity_id}')
            
            # Confirmación usando Logger Manager
            confirmed = None
            if self.logger and hasattr(self.logger, 'confirm'):
                confirmed = await self.logger.confirm(
                    config['messages']['confirmDelete'].replace('{name}', entity_name),
                    'Confirmar Eliminación',
                    'danger'
                )
            else:
                # Fallback a confirm nativo
                import js2py
                confirmed = js2py.eval(f'confirm("{config["messages"]["confirmDelete"].replace("{name}", entity_name)}")')
            
            if not confirmed:
                if self.logger:
                    self.logger.info('Eliminación cancelada por el usuario')
                return {'success': False, 'cancelled': True}
            
            url = self.api_base_url + config['endpoints']['delete'].format(id=entity_id)
            
            response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {localStorage.getItem("jwt") or ""}'
                }
            })
            
            if not response.ok:
                error_data = await response.json()
                raise Exception(error_data.message or f'Error {response.status}')
            
            if self.logger:
                self.logger.info(f'{entity_type} {entity_id} eliminado correctamente')
            
            return {
                'success': True,
                'message': config['messages']['deleteSuccess']
            }
            
        except Exception as error:
            if self.logger:
                self.logger.error(f'Error eliminando {entity_type} {entity_id}:', error)
            raise error
    
    def validate_form(self, form_element, required_fields):
        """Validar formulario de forma centralizada"""
        try:
            # Para Python puro, necesitamos una forma diferente de validar
            # Esto es un placeholder - la validación real se haría en el frontend
            return {
                'valid': True,
                'missing_fields': [],
                'data': {}
            }
            
        except Exception as error:
            if self.logger:
                self.logger.error('Error validando formulario:', error)
            return {
                'valid': False,
                'error': str(error)
            }

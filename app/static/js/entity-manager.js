/**
 * Gestor Centralizado de Entidades (JavaScript)
 * Solución definitiva para sistema de herencia consistente
 * 
 * @author Sistema Laboratorio v2
 * @version 2.0.0 - Arquitectura Limpia
 */

class EntityManager {
    /**
     * Constructor del gestor de entidades
     * @param {string} apiBaseUrl - URL base de la API
     */
    constructor(apiBaseUrl = '') {
        this.apiBaseUrl = apiBaseUrl;
    }

    /**
     * Obtener configuración centralizada de entidad
     * @param {string} entityType - Tipo de entidad
     */
    getEntityConfig(entityType) {
        const configs = {
            usuario: {
                endpoints: {
                    get: '/api/usuarios/{id}',
                    update: '/api/usuarios/{id}',
                    delete: '/api/usuarios/{id}'
                },
                messages: {
                    confirmDelete: '¿Estás seguro de eliminar al usuario "{name}"? Esta acción no se puede deshacer.',
                    deleteSuccess: 'Usuario eliminado correctamente',
                    updateSuccess: 'Usuario actualizado correctamente'
                },
                fields: {
                    id: 'id',
                    name: 'nombre'
                }
            },
            laboratorio: {
                endpoints: {
                    get: '/api/laboratorios/{id}',
                    update: '/api/laboratorios/{id}',
                    delete: '/api/laboratorios/{id}'
                },
                messages: {
                    confirmDelete: '¿Estás seguro de eliminar el laboratorio "{name}"? Esta acción no se puede deshacer.',
                    deleteSuccess: 'Laboratorio eliminado correctamente',
                    updateSuccess: 'Laboratorio actualizado correctamente'
                },
                fields: {
                    id: 'id',
                    name: 'nombre'
                }
            },
            equipo: {
                endpoints: {
                    get: '/api/registro-editar/equipo/{id}',
                    update: '/api/registro-actualizar/equipo/{id}',
                    delete: '/api/registro-eliminar/equipo/{id}'
                },
                messages: {
                    confirmDelete: '¿Estás seguro de eliminar el equipo "{name}"? Esta acción no se puede deshacer.',
                    deleteSuccess: 'Equipo eliminado correctamente',
                    updateSuccess: 'Equipo actualizado correctamente'
                },
                fields: {
                    id: 'equipo_id',
                    name: 'nombre'
                }
            },
            item: {
                endpoints: {
                    get: '/api/inventario/{id}',
                    update: '/api/inventario/{id}',
                    delete: '/api/inventario/{id}'
                },
                messages: {
                    confirmDelete: '¿Estás seguro de eliminar el item "{name}"? Esta acción no se puede deshacer.',
                    deleteSuccess: 'Item eliminado correctamente',
                    updateSuccess: 'Item actualizado correctamente'
                },
                fields: {
                    id: 'id',
                    name: 'nombre'
                }
            },
            inventario: {
                endpoints: {
                    get: '/api/inventario/{id}',
                    update: '/api/inventario/{id}',
                    delete: '/api/inventario/{id}'
                },
                messages: {
                    confirmDelete: '¿Estás seguro de eliminar el item "{name}" del inventario? Esta acción no se puede deshacer.',
                    deleteSuccess: 'Item del inventario eliminado correctamente',
                    updateSuccess: 'Item del inventario actualizado correctamente'
                },
                fields: {
                    id: 'id',
                    name: 'nombre'
                }
            }
        };
        return configs[entityType] || {};
    }

    /**
     * Construir URL con parámetros
     * @param {string} urlTemplate - Template de URL
     * @param {object} params - Parámetros
     */
    buildUrl(urlTemplate, params) {
        let url = urlTemplate;
        for (const [key, value] of Object.entries(params)) {
            url = url.replace(`{${key}}`, value);
        }
        return this.apiBaseUrl + url;
    }

    /**
     * Obtener datos de una entidad para edición
     * @param {string} entityType - Tipo de entidad
     * @param {string} entityId - ID de la entidad
     */
    async getEntityForEdit(entityType, entityId) {
        try {
            const config = this.getEntityConfig(entityType);
            const url = this.buildUrl(config.endpoints.get, { id: entityId });
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt') || ''}`
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            if (typeof window.Logger !== 'undefined') {
                window.Logger.error(`Error obteniendo ${entityType} ${entityId}:`, error);
            }
            throw error;
        }
    }

    /**
     * Editar una entidad
     * @param {string} entityType - Tipo de entidad
     * @param {string} entityId - ID de la entidad
     * @param {Function} fillModalFn - Función para llenar modal
     * @param {string} modalId - ID del modal
     */
    async editEntity(entityType, entityId, fillModalFn, modalId) {
        try {
            const data = await this.getEntityForEdit(entityType, entityId);
            
            if (data.success) {
                fillModalFn(data);
                
                // Mostrar modal
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
            } else {
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.showToast('No se pudieron cargar los datos', 'error');
                }
            }

        } catch (error) {
            if (typeof window.Logger !== 'undefined') {
                window.Logger.showToast(`Error al cargar datos: ${error.message}`, 'error');
            }
        }
    }

    /**
     * Guardar cambios de una entidad
     * @param {string} entityType - Tipo de entidad
     * @param {string} entityId - ID de la entidad
     * @param {object} formData - Datos del formulario
     * @param {Function} onSuccess - Callback de éxito
     * @param {string} modalId - ID del modal
     */
    async saveEntity(entityType, entityId, formData, onSuccess = null, modalId = null) {
        try {
            const config = this.getEntityConfig(entityType);
            const url = this.buildUrl(config.endpoints.update, { id: entityId });

            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt') || ''}`
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.showToast(config.messages.updateSuccess, 'success');
                }

                // Cerrar modal
                if (modalId) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                    if (modal) {
                        modal.hide();
                    }
                }

                // Ejecutar callback
                if (typeof onSuccess === 'function') {
                    onSuccess(result);
                } else {
                    // Recargar página por defecto
                    setTimeout(() => location.reload(), 1500);
                }

            } else {
                const errorMsg = result.message || 'Error al guardar cambios';
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.showToast(errorMsg, 'error');
                }
            }

        } catch (error) {
            if (typeof window.Logger !== 'undefined') {
                window.Logger.showToast(`Error al guardar: ${error.message}`, 'error');
            }
        }
    }

    /**
     * Eliminar una entidad con confirmación
     * @param {string} entityType - Tipo de entidad
     * @param {string} entityId - ID de la entidad
     * @param {string} entityName - Nombre de la entidad
     * @param {Function} onSuccess - Callback de éxito
     */
    async deleteEntity(entityType, entityId, entityName, onSuccess = null) {
        try {
            const config = this.getEntityConfig(entityType);
            const message = config.messages.confirmDelete.replace('{name}', entityName);

            // Confirmación usando Logger Manager siempre
            let confirmed = false;
            if (typeof window.Logger !== 'undefined' && typeof window.Logger.confirm === 'function') {
                confirmed = await window.Logger.confirm(message, 'Confirmar Eliminación', 'danger');
            } else {
                // Si Logger no está disponible, mostrar mensaje simple y continuar
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.warn('Logger Manager no disponible, usando confirmación simple');
                }
                confirmed = confirm(message);
            }

            if (!confirmed) {
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.info('Eliminación cancelada por el usuario');
                }
                return;
            }

            const url = this.buildUrl(config.endpoints.delete, { id: entityId });

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt') || ''}`
                }
            });

            const result = await response.json();

            if (response.ok) {
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.showToast(config.messages.deleteSuccess, 'success');
                    window.Logger.debug(`${entityType} ${entityId} eliminado correctamente`);
                }

                // Ejecutar callback
                if (typeof onSuccess === 'function') {
                    onSuccess(result);
                } else {
                    // Recargar página por defecto
                    setTimeout(() => location.reload(), 1000);
                }

            } else {
                const errorMsg = result.message || 'Error al eliminar';
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.showToast(errorMsg, 'error');
                }
            }

        } catch (error) {
            if (typeof window.Logger !== 'undefined') {
                window.Logger.showToast(`Error al eliminar: ${error.message}`, 'error');
            }
        }
    }

    /**
     * Validar formulario de forma centralizada
     * @param {HTMLElement} formElement - Elemento del formulario
     * @param {Array} requiredFields - Campos requeridos
     */
    validateForm(formElement, requiredFields) {
        try {
            const formData = new FormData(formElement);
            const data = {};
            
            for (const [key, value] of formData.entries()) {
                data[key] = value.trim();
            }

            const missingFields = requiredFields.filter(field => !data[field]);

            if (missingFields.length > 0) {
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.error(`Campos requeridos faltantes: ${missingFields.join(', ')}`);
                }
                return {
                    valid: false,
                    missingFields,
                    data
                };
            }

            return {
                valid: true,
                missingFields: [],
                data
            };

        } catch (error) {
            if (typeof window.Logger !== 'undefined') {
                window.Logger.error('Error validando formulario:', error);
            }
            return {
                valid: false,
                error: error.message
            };
        }
    }

    /**
     * Ver detalles de una entidad
     * @param {string} entityType - Tipo de entidad
     * @param {string} entityId - ID de la entidad
     * @param {Function} callback - Callback para manejar datos
     */
    async viewEntityDetails(entityType, entityId, callback = null) {
        try {
            const data = await this.getEntityForEdit(entityType, entityId);
            
            if (typeof callback === 'function') {
                callback(data);
            } else {
                // Mostrar en consola por defecto
                if (typeof window.Logger !== 'undefined') {
                    window.Logger.debug(`Detalles de ${entityType}:`, data);
                }
            }

        } catch (error) {
            if (typeof window.Logger !== 'undefined') {
                window.Logger.error(`Error obteniendo detalles: ${error.message}`);
            }
        }
    }
}

// Crear instancia global del EntityManager
window.EntityManager = new EntityManager();

// Clases especializadas para compatibilidad
window.UserManager = {
    editUser: (userId, fillModalFn, modalId) => 
        window.EntityManager.editEntity('usuario', userId, fillModalFn, modalId || 'editarUsuarioModal'),
    
    saveUser: (userId, formData, onSuccess, modalId) => 
        window.EntityManager.saveEntity('usuario', userId, formData, onSuccess, modalId || 'editarUsuarioModal'),
    
    deleteUser: (userId, userName, onSuccess) => 
        window.EntityManager.deleteEntity('usuario', userId, userName, onSuccess)
};

window.LaboratoryManager = {
    editLaboratory: (labId, fillModalFn, modalId) => 
        window.EntityManager.editEntity('laboratorio', labId, fillModalFn, modalId || 'editarLaboratorioModal'),
    
    saveLaboratory: (labId, formData, onSuccess, modalId) => 
        window.EntityManager.saveEntity('laboratorio', labId, formData, onSuccess, modalId || 'editarLaboratorioModal'),
    
    deleteLaboratory: (labId, labName, onSuccess) => 
        window.EntityManager.deleteEntity('laboratorio', labId, labName, onSuccess)
};

window.RegistroManager = {
    editRegistro: (id, tipo, fillModalFn, modalId) => 
        window.EntityManager.editEntity(tipo, id, fillModalFn, modalId),
    
    saveRegistro: (id, tipo, formData, onSuccess, modalId) => 
        window.EntityManager.saveEntity(tipo, id, formData, onSuccess, modalId),
    
    deleteRegistro: (id, tipo, nombre, onSuccess) => 
        window.EntityManager.deleteEntity(tipo, id, nombre, onSuccess)
};

window.InventarioManager = {
    editInventario: (id, fillModalFn, modalId) => 
        window.EntityManager.editEntity('inventario', id, fillModalFn, modalId),
    
    saveInventario: (id, formData, onSuccess, modalId) => 
        window.EntityManager.saveEntity('inventario', id, formData, onSuccess, modalId),
    
    deleteInventario: (id, nombre, onSuccess) => 
        window.EntityManager.deleteEntity('inventario', id, nombre, onSuccess)
};

// Logger para compatibilidad
if (typeof window.Logger !== 'undefined') {
    window.Logger.info('EntityManager v2.0.0 inicializado correctamente', {
        version: '2.0.0',
        features: ['centralized_config', 'unified_validation', 'logger_integration']
    });
}
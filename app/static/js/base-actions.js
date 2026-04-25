/**
 * Sistema de Herencia para Acciones CRUD
 * Proporciona funcionalidades genéricas para evitar duplicación de código
 * 
 * @author Sistema Laboratorio v2
 * @version 1.0.0
 */

/**
 * Clase base para acciones CRUD genéricas
 * Implementa patrones comunes para editar, eliminar y ver detalles
 */
class BaseActions {
    /**
     * Configuración por defecto para diferentes tipos de entidades
     */
    static entityConfig = {
        usuario: {
            endpoints: {
                get: '/api/usuarios/{id}/update',
                update: '/api/usuarios/{id}/update',
                delete: '/api/usuarios/{id}/delete'
            },
            messages: {
                confirmDelete: '¿Estás seguro de eliminar al usuario "{name}"? Esta acción no se puede deshacer.',
                deleteSuccess: 'Usuario eliminado correctamente',
                updateSuccess: 'Usuario actualizado correctamente'
            },
            idField: 'id',
            nameField: 'nombre'
        },
        laboratorio: {
            endpoints: {
                get: '/api/laboratorios/{id}/update',
                update: '/api/laboratorios/{id}/update',
                delete: '/api/laboratorios/{id}/delete'
            },
            messages: {
                confirmDelete: '¿Estás seguro de eliminar el laboratorio "{name}"? Esta acción no se puede deshacer.',
                deleteSuccess: 'Laboratorio eliminado correctamente',
                updateSuccess: 'Laboratorio actualizado correctamente'
            },
            idField: 'id',
            nameField: 'nombre'
        },
        equipo: {
            endpoints: {
                get: '/api/registro-editar/equipo/{id}',
                update: '/api/registro-actualizar/equipo/{id}',
                delete: '/api/registro-eliminar/equipo/{id}'
            },
            messages: {
                confirmDelete: (name) => `¿Estás seguro de eliminar al equipo "${name}"? Esta acción no se puede deshacer.`,
                deleteSuccess: 'Equipo eliminado correctamente',
                updateSuccess: 'Equipo actualizado correctamente',
                fetchError: 'Error de conexión al obtener equipo',
                saveError: 'Error de conexión al guardar cambios',
                deleteError: 'Error de conexión al eliminar equipo'
            },
            nameField: 'nombre'
        },
        item: {
            endpoints: {
                get: '/api/registro-editar/item/{id}',
                update: '/api/registro-actualizar/item/{id}',
                delete: '/api/registro-eliminar/item/{id}'
            },
            messages: {
                confirmDelete: (name) => `¿Estás seguro de eliminar el item "${name}"? Esta acción no se puede deshacer.`,
                deleteSuccess: 'Item eliminado correctamente',
                updateSuccess: 'Item actualizado correctamente',
                fetchError: 'Error de conexión al obtener item',
                saveError: 'Error de conexión al guardar cambios',
                deleteError: 'Error de conexión al eliminar item'
            },
            nameField: 'nombre'
        }
    };

    /**
     * Obtiene la configuración para un tipo de entidad
     * @param {string} entityType - Tipo de entidad (usuario, laboratorio, equipo, item)
     * @returns {Object} Configuración de la entidad
     */
    static getConfig(entityType) {
        return this.entityConfig[entityType] || this.entityConfig.usuario;
    }

    /**
     * Construye URL de endpoint reemplazando placeholders
     * @param {string} template - Template de URL con placeholders
     * @param {string} id - ID a reemplazar
     * @returns {string} URL construida
     */
    static buildUrl(template, id) {
        return template.replace('{id}', id);
    }

    /**
     * Muestra mensaje de depuración usando Logger Manager
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de mensaje (info, error, success, warning)
     * @param {any} data - Datos adicionales (opcional)
     */
    static debug(message, type = 'info', data = null) {
        if (typeof window.Logger !== 'undefined') {
            switch (type) {
                case 'error':
                    window.Logger.error(message, data);
                    break;
                case 'success':
                    window.Logger.info(message, data);
                    window.Logger.showToast(message, 'success');
                    break;
                case 'warning':
                    window.Logger.warn(message, data);
                    break;
                default:
                    window.Logger.info(message, data);
            }
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`, data || '');
        }
    }

    /**
     * Muestra toast notification
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de toast (success, error, warning, info)
     * @param {number} duration - Duración en milisegundos (opcional)
     */
    static showToast(message, type = 'info', duration = 3000) {
        if (typeof window.Logger !== 'undefined') {
            window.Logger.showToast(message, type, duration);
        } else {
            console.log(`[TOAST] ${type}: ${message}`);
        }
    }

    /**
     * Muestra diálogo de confirmación usando Logger Manager
     * @param {string} message - Mensaje de confirmación
     * @param {string} title - Título del diálogo
     * @param {string} type - Tipo de diálogo (warning, danger, info)
     * @returns {Promise<boolean>} Promesa con la respuesta del usuario
     */
    static async confirm(message, title = 'Confirmación', type = 'warning') {
        if (typeof window.Logger !== 'undefined') {
            return await window.Logger.confirm(message, title, type);
        } else {
            return confirm(message);
        }
    }

    /**
     * Realiza solicitud fetch genérica con manejo de errores
     * @param {string} url - URL de la solicitud
     * @param {Object} options - Opciones de fetch (method, headers, body)
     * @returns {Promise<Object>} Respuesta de la API
     */
    static async fetchApi(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('jwt') || ''}`
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            this.debug(`Error en API: ${error.message}`, 'error', { url, error });
            throw error;
        }
    }

    /**
     * Obtiene datos de una entidad para edición
     * @param {string} entityType - Tipo de entidad
     * @param {string} id - ID de la entidad
     * @returns {Promise<Object>} Datos de la entidad
     */
    static async getEntityForEdit(entityType, id) {
        const config = this.getConfig(entityType);
        const url = this.buildUrl(config.endpoints.get, id);

        try {
            const data = await this.fetchApi(url, { method: 'GET' });
            this.debug(`Datos obtenidos para ${entityType} ${id}`, 'info', data);
            return data;
        } catch (error) {
            this.showToast(`Error al obtener datos: ${error.message}`, 'error');
            throw error;
        }
    }

    /**
     * Elimina una entidad con confirmación
     * @param {string} entityType - Tipo de entidad
     * @param {string} id - ID de la entidad
     * @param {string} name - Nombre de la entidad (para mensaje)
     * @param {Function} onSuccess - Callback opcional después de eliminar
     */
    static async deleteEntity(entityType, id, name, onSuccess = null) {
        const config = this.getConfig(entityType);
        const message = config.messages.confirmDelete.replace('{name}', name);

        try {
            const confirmed = await this.confirm(message, 'Confirmar Eliminación', 'danger');
            
            if (!confirmed) {
                this.debug('Eliminación cancelada por el usuario', 'info');
                return;
            }

            const url = this.buildUrl(config.endpoints.delete, id);
            await this.fetchApi(url, { method: 'DELETE' });

            this.showToast(config.messages.deleteSuccess, 'success');
            this.debug(`${entityType} ${id} eliminado correctamente`, 'success');

            if (typeof onSuccess === 'function') {
                onSuccess();
            } else {
                // Recargar página por defecto
                setTimeout(() => location.reload(), 1000);
            }

        } catch (error) {
            this.showToast(`Error al eliminar: ${error.message}`, 'error');
        }
    }

    /**
     * Ver detalles de una entidad
     * @param {string} entityType - Tipo de entidad
     * @param {string} id - ID de la entidad
     * @param {Function} callback - Callback para manejar los datos
     */
    static async viewEntityDetails(entityType, id, callback = null) {
        try {
            const data = await this.getEntityForEdit(entityType, id);
            
            if (typeof callback === 'function') {
                callback(data);
            } else {
                // Comportamiento por defecto: mostrar en consola
                this.debug(`Detalles de ${entityType}:`, 'info', data);
            }
        } catch (error) {
            this.showToast(`Error al ver detalles: ${error.message}`, 'error');
        }
    }

    /**
     * Prepara y muestra modal de edición
     * @param {string} entityType - Tipo de entidad
     * @param {string} id - ID de la entidad
     * @param {Function} fillModalFn - Función para llenar el modal
     * @param {string} modalId - ID del modal (opcional)
     */
    static async editEntity(entityType, id, fillModalFn, modalId = null) {
        try {
            const data = await this.getEntityForEdit(entityType, id);
            
            if (typeof fillModalFn === 'function') {
                fillModalFn(data);
            }

            if (modalId && typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
            }

        } catch (error) {
            this.showToast(`Error al preparar edición: ${error.message}`, 'error');
        }
    }

    /**
     * Guarda cambios de una entidad
     * @param {string} entityType - Tipo de entidad
     * @param {string} id - ID de la entidad
     * @param {Object} formData - Datos del formulario
     * @param {Function} onSuccess - Callback después de guardar
     * @param {string} modalId - ID del modal a cerrar (opcional)
     */
    static async saveEntity(entityType, id, formData, onSuccess = null, modalId = null) {
        const config = this.getConfig(entityType);
        const url = this.buildUrl(config.endpoints.update, id);

        try {
            const data = await this.fetchApi(url, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });

            this.showToast(config.messages.updateSuccess, 'success');
            this.debug(`${entityType} ${id} actualizado correctamente`, 'success', data);

            // Cerrar modal si se especificó
            if (modalId && typeof bootstrap !== 'undefined') {
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                if (modal) modal.hide();
            }

            if (typeof onSuccess === 'function') {
                onSuccess(data);
            } else {
                // Recargar página por defecto
                setTimeout(() => location.reload(), 1000);
            }

        } catch (error) {
            this.showToast(`Error al guardar: ${error.message}`, 'error');
        }
    }

    /**
     * Valida formulario básico
     * @param {HTMLFormElement} form - Elemento formulario
     * @param {Array} requiredFields - Campos requeridos
     * @returns {boolean} True si válido
     */
    static validateForm(form, requiredFields = []) {
        for (const fieldName of requiredFields) {
            const field = form.elements[fieldName];
            if (!field || !field.value.trim()) {
                this.showToast(`El campo ${fieldName} es obligatorio`, 'error');
                if (field) field.focus();
                return false;
            }
        }
        return true;
    }

    /**
     * Crea funciones específicas para un tipo de entidad
     * @param {string} entityType - Tipo de entidad
     * @returns {Object} Objeto con funciones específicas
     */
    static createEntityActions(entityType) {
        return {
            verDetalles: (id, callback) => this.viewEntityDetails(entityType, id, callback),
            editar: (id, fillModalFn, modalId) => this.editEntity(entityType, id, fillModalFn, modalId),
            eliminar: (id, name, onSuccess) => this.deleteEntity(entityType, id, name, onSuccess),
            guardar: (id, formData, onSuccess, modalId) => this.saveEntity(entityType, id, formData, onSuccess, modalId)
        };
    }
}

/**
 * Clase especializada para acciones de usuarios
 */
class UserActions extends BaseActions {
    static async editUser(userId, fillModalFn, modalId = 'editarUsuarioModal') {
        return await this.editEntity('usuario', userId, fillModalFn, modalId);
    }

    static async deleteUser(userId, userName, onSuccess = null) {
        return await this.deleteEntity('usuario', userId, userName, onSuccess);
    }

    static async saveUser(userId, formData, onSuccess = null, modalId = 'editarUsuarioModal') {
        return await this.saveEntity('usuario', userId, formData, onSuccess, modalId);
    }
}

/**
 * Clase especializada para acciones de laboratorios
 */
class LaboratoryActions extends BaseActions {
    static async editLaboratory(labId, fillModalFn, modalId = 'editarLaboratorioModal') {
        return await this.editEntity('laboratorio', labId, fillModalFn, modalId);
    }

    static async deleteLaboratory(labId, labName, onSuccess = null) {
        return await this.deleteEntity('laboratorio', labId, labName, onSuccess);
    }

    static async saveLaboratory(labId, formData, onSuccess = null, modalId = 'editarLaboratorioModal') {
        return await this.saveEntity('laboratorio', labId, formData, onSuccess, modalId);
    }
}

/**
 * Clase especializada para acciones de equipos/items (registros)
 */
class RegistroActions extends BaseActions {
    static async editRegistro(id, tipo, fillModalFn, modalId = null) {
        return await this.editEntity(tipo, id, fillModalFn, modalId);
    }

    static async deleteRegistro(id, tipo, name, onSuccess = null) {
        return await this.deleteEntity(tipo, id, name, onSuccess);
    }

    static async saveRegistro(id, tipo, formData, onSuccess = null, modalId = null) {
        return await this.saveEntity(tipo, id, formData, onSuccess, modalId);
    }

    static async verDetallesRegistro(id, tipo, callback = null) {
        return await this.viewEntityDetails(tipo, id, callback);
    }
}

// Exportar clases para uso global
window.BaseActions = BaseActions;
window.UserActions = UserActions;
window.LaboratoryActions = LaboratoryActions;
window.RegistroActions = RegistroActions;

// Crear instancias globales para compatibilidad
window.baseActions = BaseActions;
window.userActions = UserActions;
window.laboratoryActions = LaboratoryActions;
window.registroActions = RegistroActions;

// BaseActions System inicializado - Logger Manager maneja la sincronización automáticamente

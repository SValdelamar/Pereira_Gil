/**
 * Logger Manager v2.0 - Sistema profesional de logging
 * 
 * Características principales:
 * ✅ Logging estructurado por niveles (debug, info, warn, error)
 * ✅ Toast notifications profesionales para usuarios
 * ✅ Modal de confirmación Bootstrap
 * ✅ Detección automática de entorno (desarrollo/producción)
 * ✅ Almacenamiento en memoria opcional
 * ✅ Configuración flexible y segura
 * ✅ Manejo robusto de errores
 * ✅ Sin conflictos con console nativo
 * ✅ API simple y profesional
 */

class LoggerManager {
    constructor() {
        // Configuración por defecto
        this.config = {
            enabled: true,
            level: 'info',
            showInConsole: true,
            storeInMemory: false,
            maxMemoryLogs: 100,
            enableToast: true,
            productionLevel: 'error'
        };
        
        // Estado interno
        this.memoryLogs = [];
        this.levels = { debug: 0, info: 1, warn: 2, error: 3 };
        this.isDevelopment = this.detectEnvironment();
        
        // Ajustar configuración según entorno
        this.adjustConfigForEnvironment();
        
        // Inicializar componentes UI
        this.initializeUI();
    }

    /**
     * Detectar entorno de forma robusta
     */
    detectEnvironment() {
        try {
            const hostname = window.location?.hostname || '';
            const port = window.location?.port || '';
            
            const devHosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1'];
            const devPorts = ['3000', '5000', '8000', '8080', '9000'];
            
            return devHosts.includes(hostname) || 
                   devPorts.includes(port) || 
                   hostname.includes('dev') || 
                   hostname.includes('local');
        } catch (error) {
            return false; // Asumir producción por seguridad
        }
    }

    /**
     * Ajustar configuración según entorno
     */
    adjustConfigForEnvironment() {
        if (!this.isDevelopment) {
            this.config.level = this.config.productionLevel;
            this.config.showInConsole = false;
            this.config.storeInMemory = false;
        }
    }

    /**
     * Inicializar componentes UI
     */
    initializeUI() {
        if (this.config.enableToast) {
            this.ensureToastContainer();
        }
    }

    /**
     * Configurar el logger
     */
    configure(options) {
        if (options && typeof options === 'object') {
            this.config = { ...this.config, ...options };
            this.adjustConfigForEnvironment();
        }
    }

    /**
     * Verificar si un nivel debe ser mostrado
     */
    shouldLog(level) {
        return this.config.enabled && 
               this.levels[level] >= this.levels[this.config.level];
    }

    /**
     * Sanitizar mensaje para evitar errores
     */
    sanitizeMessage(message) {
        if (message === null || message === undefined) return '[empty]';
        if (typeof message === 'string') return message.trim() || '[empty]';
        if (typeof message === 'object') {
            try { return JSON.stringify(message); } 
            catch (e) { return '[object]'; }
        }
        return String(message);
    }

    /**
     * Logging principal
     */
    log(level, message, data = null) {
        if (!this.shouldLog(level)) return;

        try {
            const safeMessage = this.sanitizeMessage(message);
            const timestamp = new Date().toISOString();
            const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${safeMessage}`;

            // Mostrar en consola si está habilitado
            if (this.config.showInConsole && console) {
                switch (level) {
                    case 'debug': console.debug(formattedMessage, data); break;
                    case 'info': console.info(formattedMessage, data); break;
                    case 'warn': console.warn(formattedMessage, data); break;
                    case 'error': console.error(formattedMessage, data); break;
                }
            }

            // Almacenar en memoria
            if (this.config.storeInMemory) {
                this.memoryLogs.push({
                    timestamp,
                    level,
                    message: safeMessage,
                    data
                });
                if (this.memoryLogs.length > this.config.maxMemoryLogs) {
                    this.memoryLogs.shift();
                }
            }
        } catch (error) {
            // Evitar errores recursivos
            if (console && console.error) {
                console.error('Logger internal error:', error);
            }
        }
    }

    /**
     * Métodos de conveniencia
     */
    debug(message, data) { this.log('debug', message, data); }
    info(message, data) { this.log('info', message, data); }
    warn(message, data) { this.log('warn', message, data); }
    error(message, data) { this.log('error', message, data); }

    /**
     * Mostrar toast notification profesional
     */
    showUserMessage(message, type = 'info', duration = 3000) {
        if (!this.config.enableToast) {
            this.info('Toast disabled', { message, type });
            return;
        }

        try {
            const safeMessage = this.sanitizeMessage(message);
            const safeType = this.validateMessageType(type);
            const safeDuration = Math.min(Math.max(Number(duration) || 3000, 1000), 10000);

            this.ensureToastContainer();
            const toast = this.createToastElement(safeMessage, safeType);
            
            const container = document.getElementById('logger-toast-container');
            if (container) {
                container.appendChild(toast);
                this.animateToast(toast, safeDuration);
            }
        } catch (error) {
            this.error('Failed to show toast', error);
        }
    }

    /**
     * Validar tipo de mensaje
     */
    validateMessageType(type) {
        const validTypes = ['success', 'error', 'warning', 'info'];
        return validTypes.includes(type) ? type : 'info';
    }

    /**
     * Asegurar contenedor de toasts
     */
    ensureToastContainer() {
        if (!document.getElementById('logger-toast-container')) {
            const container = document.createElement('div');
            container.id = 'logger-toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    /**
     * Crear elemento toast
     */
    createToastElement(message, type) {
        const toast = document.createElement('div');
        toast.className = `logger-toast-${type}`;
        toast.style.cssText = `
            background: ${this.getToastColor(type)};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: auto;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            position: relative;
        `;

        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">${icon}</span>
                <span>${message}</span>
            </div>
            <button style="
                position: absolute;
                top: 4px;
                right: 8px;
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                opacity: 0.7;
                padding: 0;
                width: 20px;
                height: 20px;
            " onclick="this.parentElement.remove()">×</button>
        `;

        return toast;
    }

    /**
     * Obtener icono para toast
     */
    getToastIcon(type) {
        const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
        return icons[type] || 'ℹ';
    }

    /**
     * Obtener color para toast
     */
    getToastColor(type) {
        const colors = { 
            success: '#28a745', 
            error: '#dc3545', 
            warning: '#ffc107', 
            info: '#17a2b8' 
        };
        return colors[type] || colors.info;
    }

    /**
     * Animar toast
     */
    animateToast(toast, duration) {
        setTimeout(() => {
            if (toast) {
                toast.style.opacity = '1';
                toast.style.transform = 'translateX(0)';
            }
        }, 50);

        setTimeout(() => {
            if (toast && toast.parentNode) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }
        }, duration);
    }

    /**
     * Inicializar contenedor de toasts
     */
    initializeToastContainer() {
        if (!document.getElementById('logger-toast-container')) {
            const container = document.createElement('div');
            container.id = 'logger-toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    /**
     * Mostrar toast notification
     */
    showToast(message, type = 'info', duration = 4000) {
        try {
            if (!this.config.enableToast) {
                return;
            }

            const safeMessage = this.sanitizeMessage(message);
            const safeType = this.validateToastType(type);

            // Inicializar contenedor si no existe
            this.initializeToastContainer();

            // Crear y mostrar toast
            const toast = this.createToastElement(safeMessage, safeType);
            const container = document.getElementById('logger-toast-container');
            
            if (container) {
                container.appendChild(toast);
                this.animateToast(toast, duration);
            }
        } catch (error) {
            console.error('Failed to show toast:', error);
        }
    }

    /**
     * Validar tipo de toast
     */
    validateToastType(type) {
        const validTypes = ['success', 'error', 'warning', 'info'];
        return validTypes.includes(type) ? type : 'info';
    }

    /**
     * Mostrar diálogo de confirmación Bootstrap
     */
    async confirm(message, title = 'Confirmación', type = 'warning') {
        return new Promise((resolve) => {
            try {
                const safeMessage = this.sanitizeMessage(message);
                const safeTitle = this.sanitizeMessage(title);
                const safeType = this.validateConfirmType(type);

                if (typeof bootstrap === 'undefined') {
                    resolve(confirm(`${safeTitle}\n\n${safeMessage}`));
                    return;
                }

                const modalId = 'logger-confirm-modal';
                this.cleanupExistingModal(modalId);

                const config = this.getConfirmConfig(safeType);
                const modalEl = this.createConfirmModal(modalId, safeTitle, safeMessage, config);

                this.showConfirmModal(modalEl, resolve);
            } catch (error) {
                this.error('Failed to show confirmation', error);
                resolve(false);
            }
        });
    }

    /**
     * Validar tipo de confirmación
     */
    validateConfirmType(type) {
        const validTypes = ['warning', 'danger', 'info', 'success'];
        return validTypes.includes(type) ? type : 'warning';
    }

    /**
     * Limpiar modal existente
     */
    cleanupExistingModal(modalId) {
        const existingModal = document.getElementById(modalId);
        if (existingModal) {
            try {
                const instance = bootstrap.Modal.getInstance(existingModal);
                if (instance) instance.dispose();
                existingModal.remove();
            } catch (error) {
                existingModal.remove();
            }
        }
    }

    /**
     * Obtener configuración de confirmación
     */
    getConfirmConfig(type) {
        const configs = {
            warning: { bg: '#f59e0b', btn: 'btn-warning', icon: 'bi-exclamation-triangle' },
            danger: { bg: '#ef4444', btn: 'btn-danger', icon: 'bi-exclamation-octagon' },
            info: { bg: '#3b82f6', btn: 'btn-primary', icon: 'bi-info-circle' },
            success: { bg: '#10b981', btn: 'btn-success', icon: 'bi-check-circle' }
        };
        return configs[type] || configs.warning;
    }

    /**
     * Crear modal de confirmación
     */
    createConfirmModal(modalId, title, message, config) {
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-header border-0 pb-0">
                            <h5 class="modal-title d-flex align-items-center fw-bold">
                                <div class="me-3 d-flex align-items-center justify-content-center" 
                                     style="width: 40px; height: 40px; border-radius: 10px; background: ${config.bg}20; color: ${config.bg};">
                                    <i class="bi ${config.icon}"></i>
                                </div>
                                ${title}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body py-4">
                            <p class="mb-0 text-muted" style="font-size: 1rem; line-height: 1.5;">${message.replace(/\n/g, '<br>')}</p>
                        </div>
                        <div class="modal-footer border-0 pt-0">
                            <button type="button" class="btn btn-light px-4 fw-semibold text-muted" data-bs-dismiss="modal" id="logger-confirm-cancel">Cancelar</button>
                            <button type="button" class="btn ${config.btn} px-4 fw-semibold shadow-sm" id="logger-confirm-ok">Confirmar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        return document.getElementById(modalId);
    }

    /**
     * Mostrar modal de confirmación
     */
    showConfirmModal(modalEl, resolve) {
        try {
            const modal = new bootstrap.Modal(modalEl, {
                backdrop: 'static',
                keyboard: false
            });

            const setupHandlers = () => {
                const handleConfirm = () => {
                    modal.hide();
                    resolve(true);
                };

                const handleCancel = () => {
                    modal.hide();
                    resolve(false);
                };

                const handleHidden = () => {
                    if (modalEl && modalEl.parentNode) {
                        modalEl.remove();
                    }
                    resolve(false);
                };

                const confirmBtn = document.getElementById('logger-confirm-ok');
                const cancelBtn = document.getElementById('logger-confirm-cancel');

                if (confirmBtn) confirmBtn.onclick = handleConfirm;
                if (cancelBtn) cancelBtn.onclick = handleCancel;
                if (modalEl) modalEl.addEventListener('hidden.bs.modal', handleHidden);
            };

            setTimeout(setupHandlers, 50);
            modal.show();
        } catch (error) {
            this.error('Failed to initialize modal', error);
            resolve(false);
        }
    }

    /**
     * Obtener logs de memoria
     */
    getMemoryLogs() {
        return [...this.memoryLogs];
    }

    /**
     * Limpiar logs de memoria
     */
    clearMemoryLogs() {
        this.memoryLogs = [];
    }

    /**
     * Obtener información del sistema
     */
    getSystemInfo() {
        return {
            version: '2.0.0',
            environment: this.isDevelopment ? 'development' : 'production',
            config: { ...this.config },
            memoryLogsCount: this.memoryLogs.length,
            enabled: this.config.enabled,
            currentLevel: this.config.level
        };
    }
}

// Inicialización profesional con ready state
(function() {
    'use strict';
    
    // Marcar que Logger Manager está cargando
    window.LoggerLoading = true;
    
    try {
        if (!window.Logger) {
            const loggerInstance = new LoggerManager();
            window.Logger = loggerInstance;
            window.Logger.version = '2.0.0';
            window.Logger.startTime = new Date().toISOString();
            window.Logger.ready = true;
            
            // Exponer Logger directamente para compatibilidad con código existente
            window.Logger = loggerInstance;
            
            // También exponer como Logger global (sin window.) para compatibilidad
            // Esto permite que Logger.info() funcione directamente
            window.Logger = loggerInstance;
            
            // Crear variable global Logger
            if (typeof Logger === 'undefined') {
                Logger = loggerInstance;
            }
            
            // Marcar que la carga está completa
            window.LoggerLoading = false;
            
            // Disparar evento de que Logger está listo
            if (typeof window.dispatchEvent === 'function') {
                window.dispatchEvent(new CustomEvent('loggerReady'));
            }
            
            loggerInstance.info('Logger Manager v2.0 initialized', loggerInstance.getSystemInfo());
        }
    } catch (error) {
        console.error('Failed to initialize Logger Manager', error);
        
        // Fallback básico con funciones funcionales
        const fallbackLogger = {
            version: '2.0.0-fallback',
            debug: console.log.bind(console),
            info: console.log.bind(console),
            warn: console.warn.bind(console),
            error: console.error.bind(console),
            showUserMessage: (msg, type) => console.log(`[${type?.toUpperCase() || 'INFO'}] ${msg}`),
            confirm: (msg, title) => confirm(`${title}\n\n${msg}`),
            getSystemInfo: () => ({ version: '2.0.0-fallback', status: 'fallback' }),
            initializeToastContainer: function() {
                if (!document.getElementById('logger-toast-container')) {
                    const container = document.createElement('div');
                    container.id = 'logger-toast-container';
                    container.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        z-index: 9999;
                        pointer-events: none;
                        max-width: 400px;
                    `;
                    document.body.appendChild(container);
                }
            },
            showToast: function(message, type = 'info', duration = 4000) {
                try {
                    // Inicializar contenedor si no existe
                    this.initializeToastContainer();
                    
                    // Crear toast simple
                    const toast = document.createElement('div');
                    toast.style.cssText = `
                        background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : type === 'warning' ? '#ffc107' : '#17a2b8'};
                        color: white;
                        padding: 12px 16px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        opacity: 0;
                        transform: translateX(100%);
                        transition: all 0.3s ease;
                        font-size: 14px;
                    `;
                    toast.innerHTML = message;
                    
                    const container = document.getElementById('logger-toast-container');
                    if (container) {
                        container.appendChild(toast);
                        
                        // Animar entrada
                        setTimeout(() => {
                            toast.style.opacity = '1';
                            toast.style.transform = 'translateX(0)';
                        }, 50);
                        
                        // Remover después del tiempo
                        setTimeout(() => {
                            toast.style.opacity = '0';
                            toast.style.transform = 'translateX(100%)';
                            setTimeout(() => {
                                if (toast.parentNode) {
                                    toast.parentNode.removeChild(toast);
                                }
                            }, 300);
                        }, duration);
                    }
                } catch (error) {
                    console.log(`[TOAST-${type?.toUpperCase() || 'INFO'}] ${message}`);
                }
            },
            ready: true
        };
        
        window.Logger = fallbackLogger;
        
        // Exponer Logger directamente para compatibilidad
        if (typeof Logger === 'undefined') {
            Logger = fallbackLogger;
        }
        
        // Establecer ready=true ANTES de disparar evento
        window.Logger.ready = true;
        
        // Marcar que la carga está completa incluso con fallback
        window.LoggerLoading = false;
        
        // Disparar evento de que Logger está listo (fallback)
        if (typeof window.dispatchEvent === 'function') {
            window.dispatchEvent(new CustomEvent('loggerReady'));
        }
    }
})();

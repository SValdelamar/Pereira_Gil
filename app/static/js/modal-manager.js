/**
 * Modal Manager - Sistema centralizado de gestión de modales
 * 
 * PROPÓSITO:
 * Este módulo soluciona de forma DEFINITIVA el problema de backdrops bloqueantes
 * en modales de Bootstrap. Se ejecuta automáticamente en todas las páginas.
 * 
 * PROBLEMA RESUELTO:
 * Bootstrap crea elementos <div class="modal-backdrop"> que bloquean la interacción
 * con la página, incluso cuando se configura backdrop: false.
 * 
 * SOLUCIÓN:
 * 1. CSS oculta visualmente los backdrops (modal-fix.css)
 * 2. JavaScript elimina físicamente los backdrops del DOM
 * 3. Observer detecta y elimina backdrops al momento de crearse
 * 
 * @version 2.0.0
 * @author Sistema Laboratorio SENA
 */

(function() {
    'use strict';
    
    // =====================================================================
    // CONFIGURACIÓN
    // =====================================================================
    
    const CONFIG = {
        debug: false, // Cambiar a true para ver logs en consola
        cleanupInterval: 50, // Intervalo de limpieza en milisegundos
        backdropSelectors: [
            '.modal-backdrop',
            'div.modal-backdrop',
            'div[class*="backdrop"]'
        ]
    };
    
    // =====================================================================
    // UTILIDADES DE LOGGING
    // =====================================================================
    
    const log = {
        info: (msg) => CONFIG.debug && console.log(`ℹ️ [ModalManager] ${msg}`),
        warn: (msg) => CONFIG.debug && console.warn(`⚠️ [ModalManager] ${msg}`),
        success: (msg) => CONFIG.debug && console.log(`✅ [ModalManager] ${msg}`)
    };
    
    // =====================================================================
    // GESTIÓN DE BACKDROPS
    // =====================================================================
    
    /**
     * Elimina todos los backdrops del DOM y restaura el body
     */
    function eliminarBackdrops() {
        let backdropCount = 0;
        
        // Eliminar todos los backdrops encontrados
        CONFIG.backdropSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                el.remove();
                backdropCount++;
            });
        });
        
        // Restaurar estado del body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        if (backdropCount > 0) {
            log.warn(`${backdropCount} backdrop(s) eliminado(s)`);
        }
    }
    
    // =====================================================================
    // OBSERVADOR DE MUTACIONES
    // =====================================================================
    
    /**
     * Observer que detecta y elimina backdrops inmediatamente al crearse
     */
    const backdropObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1 && node.classList) {
                    const isBackdrop = node.classList.contains('modal-backdrop') || 
                                     node.className.includes('backdrop');
                    if (isBackdrop) {
                        node.remove();
                        log.warn('Backdrop detectado y eliminado (Observer)');
                    }
                }
            });
        });
    });
    
    // =====================================================================
    // GESTIÓN DE MODALES
    // =====================================================================
    
    let activeCleanupInterval = null;
    
    /**
     * Inicia limpieza continua de backdrops
     */
    function iniciarLimpieza() {
        if (activeCleanupInterval) return;
        
        activeCleanupInterval = setInterval(eliminarBackdrops, CONFIG.cleanupInterval);
        log.success('Limpieza continua iniciada');
    }
    
    /**
     * Detiene limpieza continua de backdrops
     */
    function detenerLimpieza() {
        if (activeCleanupInterval) {
            clearInterval(activeCleanupInterval);
            activeCleanupInterval = null;
            log.info('Limpieza continua detenida');
        }
    }
    
    /**
     * Configura un modal para prevenir backdrops bloqueantes
     * @param {HTMLElement} modalElement - Elemento modal a configurar
     */
    function configurarModal(modalElement) {
        if (!modalElement) return;
        
        const modalId = modalElement.id || 'unknown';
        
        // Event listener: Cuando el modal se muestra
        modalElement.addEventListener('shown.bs.modal', function() {
            eliminarBackdrops();
            iniciarLimpieza();
            log.success(`Modal "${modalId}" abierto con protección activa`);
        });
        
        // Event listener: Cuando el modal se oculta
        modalElement.addEventListener('hidden.bs.modal', function() {
            detenerLimpieza();
            eliminarBackdrops();
            log.info(`Modal "${modalId}" cerrado`);
        });
        
        log.info(`Modal "${modalId}" configurado`);
    }
    
    // =====================================================================
    // INICIALIZACIÓN
    // =====================================================================
    
    /**
     * Inicializa el Modal Manager
     */
    function inicializar() {
        log.info('Inicializando Modal Manager v2.0.0...');
        
        // Limpieza inicial
        eliminarBackdrops();
        
        // Iniciar observer
        backdropObserver.observe(document.body, {
            childList: true,
            subtree: false
        });
        log.success('Observer de backdrops activo');
        
        // Configurar todos los modales existentes
        const modales = document.querySelectorAll('.modal');
        modales.forEach(configurarModal);
        log.success(`${modales.length} modal(es) configurado(s)`);
        
        // API global para uso manual
        window.ModalManager = {
            eliminarBackdrops,
            configurarModal,
            version: '2.0.0'
        };
        
        log.success('Modal Manager inicializado correctamente');
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
    
})();

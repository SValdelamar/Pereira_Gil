/**
 * Password Toggle Component
 * Sistema GIL - Centro Minero SENA
 * Componente para mostrar/ocultar contraseñas con buenas prácticas de seguridad
 */

class PasswordToggle {
    constructor() {
        this.init();
    }

    init() {
        // Auto-inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupPasswordToggles());
        } else {
            this.setupPasswordToggles();
        }
    }

    setupPasswordToggles() {
        // Buscar todos los inputs de contraseña
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        
        passwordInputs.forEach(input => {
            // Evitar duplicar el botón si ya existe
            if (input.hasAttribute('data-password-toggle-initialized')) {
                return;
            }
            
            this.createPasswordToggle(input);
            input.setAttribute('data-password-toggle-initialized', 'true');
        });

        // Observer para inputs dinámicos
        this.setupMutationObserver();
    }

    createPasswordToggle(input) {
        // Crear wrapper para el input y botón
        const wrapper = document.createElement('div');
        wrapper.className = 'password-toggle-wrapper';
        
        // Envolver el input
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        // Crear botón de toggle
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'password-toggle-btn';
        toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
        toggleButton.setAttribute('title', 'Mostrar contraseña');
        toggleButton.innerHTML = `
            <i class="bi bi-eye" aria-hidden="true"></i>
        `;
        
        // Agregar botón al wrapper
        wrapper.appendChild(toggleButton);
        
        // Aplicar estilos básicos
        this.applyStyles(wrapper, input, toggleButton);
        
        // Agregar evento de click
        toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.togglePassword(input, toggleButton);
        });
        
        // Agregar eventos de teclado para accesibilidad
        toggleButton.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.togglePassword(input, toggleButton);
            }
        });
    }

    togglePassword(input, button) {
        const isPassword = input.type === 'password';
        const icon = button.querySelector('i');
        
        // Cambiar tipo de input
        input.type = isPassword ? 'text' : 'password';
        
        // Actualizar botón
        if (isPassword) {
            button.setAttribute('aria-label', 'Ocultar contraseña');
            button.setAttribute('title', 'Ocultar contraseña');
            icon.className = 'bi bi-eye-slash';
            button.classList.add('visible');
        } else {
            button.setAttribute('aria-label', 'Mostrar contraseña');
            button.setAttribute('title', 'Mostrar contraseña');
            icon.className = 'bi bi-eye';
            button.classList.remove('visible');
        }
        
        // Disparar evento personalizado
        input.dispatchEvent(new CustomEvent('passwordToggle', {
            detail: { visible: !isPassword }
        }));
        
        // Log de seguridad (solo en desarrollo)
        if (this.isDevelopment()) {
            console.log(`Password visibility changed: ${!isPassword ? 'VISIBLE' : 'HIDDEN'}`);
        }
    }

    applyStyles(wrapper, input, button) {
        // Agregar clases CSS en lugar de estilos inline
        wrapper.classList.add('password-toggle-wrapper');
        
        // No aplicar estilos al input, las clases CSS lo manejan
        // input.style.flex = '1'; // Manejado por CSS
        
        // No aplicar estilos al botón, las clases CSS lo manejan
        // button.style.position = 'absolute'; // Manejado por CSS
        // button.style.right = '10px'; // Manejado por CSS
        // button.style.top = '50%'; // Manejado por CSS
        // button.style.transform = 'translateY(-50%)'; // Manejado por CSS
        // button.style.background = 'none'; // Manejado por CSS
        // button.style.border = 'none'; // Manejado por CSS
        // button.style.color = '#6c757d'; // Manejado por CSS
        // button.style.cursor = 'pointer'; // Manejado por CSS
        // button.style.padding = '5px'; // Manejado por CSS
        // button.style.borderRadius = '4px'; // Manejado por CSS
        // button.style.fontSize = '14px'; // Manejado por CSS
        // button.style.transition = 'all 0.2s ease'; // Manejado por CSS
        // button.style.zIndex = '10'; // Manejado por CSS
        
        // Los estilos hover y focus ahora son manejados por CSS
        // No se necesitan event listeners para hover
        
        // Ajustar padding-right del input para no sobreponer el botón
        // Esto es manejado por la clase CSS .password-toggle-wrapper .form-control
        // input.style.paddingRight = '40px'; // Manejado por CSS
    }

    setupMutationObserver() {
        // Observer para detectar inputs de contraseña agregados dinámicamente
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Verificar si es un input de contraseña
                        if (node.tagName === 'INPUT' && node.type === 'password') {
                            if (!node.hasAttribute('data-password-toggle-initialized')) {
                                this.createPasswordToggle(node);
                                node.setAttribute('data-password-toggle-initialized', 'true');
                            }
                        }
                        // Buscar inputs de contraseña dentro del nodo agregado
                        const passwordInputs = node.querySelectorAll ? 
                            node.querySelectorAll('input[type="password"]') : [];
                        
                        passwordInputs.forEach(input => {
                            if (!input.hasAttribute('data-password-toggle-initialized')) {
                                this.createPasswordToggle(input);
                                input.setAttribute('data-password-toggle-initialized', 'true');
                            }
                        });
                    }
                });
            });
        });

        // Observar cambios en el body
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    isDevelopment() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.hostname.includes('dev');
    }

    // Método público para inicializar manualmente
    refresh() {
        this.setupPasswordToggles();
    }

    // Método público para destruir todos los toggles
    destroy() {
        const wrappers = document.querySelectorAll('.password-toggle-wrapper');
        wrappers.forEach(wrapper => {
            const input = wrapper.querySelector('input[type="password"]');
            const button = wrapper.querySelector('.password-toggle-btn');
            
            if (input && button) {
                // Restaurar input
                input.type = 'password';
                input.style.paddingRight = '';
                input.removeAttribute('data-password-toggle-initialized');
                
                // Mover input fuera del wrapper
                wrapper.parentNode.insertBefore(input, wrapper);
                
                // Eliminar wrapper
                wrapper.remove();
            }
        });
    }
}

// Función de inicialización global
function initPasswordToggles() {
    window.passwordToggle = new PasswordToggle();
}

// Auto-inicialización
initPasswordToggles();

// Exportar para uso global
window.PasswordToggle = PasswordToggle;

// Evento personalizado para cuando se carga contenido dinámico
document.addEventListener('contentLoaded', () => {
    if (window.passwordToggle) {
        window.passwordToggle.refresh();
    }
});

console.log('Password Toggle Component loaded');

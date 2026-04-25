/**
 * Password Validator Component
 * Sistema GIL - Centro Minero SENA
 * Componente para validación de contraseñas con indicador de fortaleza
 */

class PasswordValidator {
    constructor() {
        this.init();
    }

    init() {
        // Auto-inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupPasswordValidators());
        } else {
            this.setupPasswordValidators();
        }
    }

    setupPasswordValidators() {
        // Buscar todos los inputs de contraseña que necesiten validación
        const passwordInputs = document.querySelectorAll('input[type="password"][data-validate="true"]');
        
        passwordInputs.forEach(input => {
            // Evitar duplicar la validación
            if (input.hasAttribute('data-password-validator-initialized')) {
                return;
            }
            
            this.createPasswordValidator(input);
            input.setAttribute('data-password-validator-initialized', 'true');
        });

        // Observer para inputs dinámicos
        this.setupMutationObserver();
    }

    createPasswordValidator(input) {
        // Crear contenedor de validación
        const validationContainer = document.createElement('div');
        validationContainer.className = 'password-validator-container';
        
        // Insertar después del input
        input.parentNode.insertBefore(validationContainer, input.nextSibling);
        
        // Crear indicador de fortaleza
        const strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength-indicator';
        strengthIndicator.innerHTML = `
            <div class="strength-label">
                <span class="strength-text">Fortaleza de la contraseña</span>
                <span class="strength-score">0/100</span>
            </div>
            <div class="strength-bar">
                <div class="strength-fill"></div>
            </div>
            <div class="strength-requirements">
                <div class="requirement" data-requirement="length">
                    <i class="bi bi-circle"></i>
                    <span>Mínimo 6 caracteres</span>
                </div>
                <div class="requirement" data-requirement="uppercase">
                    <i class="bi bi-circle"></i>
                    <span>Una mayúscula</span>
                </div>
                <div class="requirement" data-requirement="lowercase">
                    <i class="bi bi-circle"></i>
                    <span>Una minúscula</span>
                </div>
                <div class="requirement" data-requirement="number">
                    <i class="bi bi-circle"></i>
                    <span>Un número</span>
                </div>
                <div class="requirement" data-requirement="special">
                    <i class="bi bi-circle"></i>
                    <span>Un carácter especial (!@#$%^&*)</span>
                </div>
            </div>
        `;
        
        validationContainer.appendChild(strengthIndicator);
        
        // Agregar eventos de validación
        input.addEventListener('input', (e) => {
            this.validatePassword(e.target, validationContainer);
        });
        
        input.addEventListener('blur', (e) => {
            this.validatePassword(e.target, validationContainer);
        });
        
        // Validación inicial
        this.validatePassword(input, validationContainer);
    }

    validatePassword(password, validationContainer) {
        const value = password.value;
        const strengthIndicator = validationContainer.querySelector('.strength-indicator');
        const strengthFill = strengthIndicator.querySelector('.strength-fill');
        const strengthScore = strengthIndicator.querySelector('.strength-score');
        const strengthText = strengthIndicator.querySelector('.strength-text');
        const requirements = strengthIndicator.querySelectorAll('.requirement');
        
        // Calcular puntuación
        let score = 0;
        let maxScore = 100;
        
        // Validaciones
        const validations = {
            length: value.length >= 6,
            uppercase: /[A-Z]/.test(value),
            lowercase: /[a-z]/.test(value),
            number: /[0-9]/.test(value),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(value)
        };
        
        // Calcular puntos por cada validación
        const points = {
            length: value.length >= 6 ? 20 : (value.length >= 3 ? 10 : 0),
            uppercase: validations.uppercase ? 20 : 0,
            lowercase: validations.lowercase ? 20 : 0,
            number: validations.number ? 20 : 0,
            special: validations.special ? 20 : 0
        };
        
        // Sumar puntos
        score = Object.values(points).reduce((sum, points) => sum + points, 0);
        
        // Bonus por longitud extra
        if (value.length >= 12) score += 10;
        if (value.length >= 16) score += 10;
        
        // Limitar a 100
        score = Math.min(score, maxScore);
        
        // Actualizar indicador visual
        this.updateStrengthIndicator(score, strengthFill, strengthScore, strengthText);
        
        // Actualizar requisitos
        this.updateRequirements(validations, requirements);
        
        // Agregar clases al input según la fortaleza
        this.updateInputClasses(password, score);
        
        // Disparar evento personalizado
        password.dispatchEvent(new CustomEvent('passwordValidated', {
            detail: {
                score: score,
                validations: validations,
                isValid: score >= 60
            }
        }));
    }

    updateStrengthIndicator(score, fill, scoreElement, textElement) {
        // Actualizar puntuación
        scoreElement.textContent = `${score}/100`;
        
        // Determinar nivel de fortaleza
        let level, color, text;
        if (score < 30) {
            level = 'weak';
            color = '#dc3545';
            text = 'Débil';
        } else if (score < 60) {
            level = 'fair';
            color = '#ffc107';
            text = 'Regular';
        } else if (score < 80) {
            level = 'good';
            color = '#0dcaf0';
            text = 'Buena';
        } else {
            level = 'strong';
            color = '#198754';
            text = 'Fuerte';
        }
        
        // Actualizar barra de progreso
        fill.style.width = `${score}%`;
        fill.style.backgroundColor = color;
        
        // Actualizar texto
        textElement.textContent = `Fortaleza: ${text}`;
        textElement.style.color = color;
        
        // Actualizar clase del contenedor
        fill.parentElement.className = `strength-bar strength-${level}`;
    }

    updateRequirements(validations, requirements) {
        requirements.forEach(req => {
            const requirement = req.getAttribute('data-requirement');
            const icon = req.querySelector('i');
            const isValid = validations[requirement];
            
            if (isValid) {
                icon.className = 'bi bi-check-circle-fill';
                req.classList.add('valid');
                req.classList.remove('invalid');
            } else {
                icon.className = 'bi bi-circle';
                req.classList.add('invalid');
                req.classList.remove('valid');
            }
        });
    }

    updateInputClasses(input, score) {
        // Remover clases anteriores
        input.classList.remove('password-weak', 'password-fair', 'password-good', 'password-strong');
        
        // Agregar clase según la fortaleza
        if (score < 30) {
            input.classList.add('password-weak');
        } else if (score < 60) {
            input.classList.add('password-fair');
        } else if (score < 80) {
            input.classList.add('password-good');
        } else {
            input.classList.add('password-strong');
        }
    }

    setupMutationObserver() {
        // Observer para detectar inputs de contraseña agregados dinámicamente
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Verificar si es un input de contraseña con validación
                        if (node.tagName === 'INPUT' && 
                            node.type === 'password' && 
                            node.hasAttribute('data-validate')) {
                            if (!node.hasAttribute('data-password-validator-initialized')) {
                                this.createPasswordValidator(node);
                                node.setAttribute('data-password-validator-initialized', 'true');
                            }
                        }
                        // Buscar inputs de contraseña dentro del nodo agregado
                        const passwordInputs = node.querySelectorAll ? 
                            node.querySelectorAll('input[type="password"][data-validate="true"]') : [];
                        
                        passwordInputs.forEach(input => {
                            if (!input.hasAttribute('data-password-validator-initialized')) {
                                this.createPasswordValidator(input);
                                input.setAttribute('data-password-validator-initialized', 'true');
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

    // Método público para verificar si una contraseña es válida
    isValidPassword(password) {
        const value = typeof password === 'string' ? password : password.value;
        
        const validations = {
            length: value.length >= 6,
            uppercase: /[A-Z]/.test(value),
            lowercase: /[a-z]/.test(value),
            number: /[0-9]/.test(value),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(value)
        };
        
        const points = {
            length: value.length >= 6 ? 20 : (value.length >= 3 ? 10 : 0),
            uppercase: validations.uppercase ? 20 : 0,
            lowercase: validations.lowercase ? 20 : 0,
            number: validations.number ? 20 : 0,
            special: validations.special ? 20 : 0
        };
        
        let score = Object.values(points).reduce((sum, points) => sum + points, 0);
        
        if (value.length >= 12) score += 10;
        if (value.length >= 16) score += 10;
        
        score = Math.min(score, 100);
        
        return {
            score: score,
            validations: validations,
            isValid: score >= 60,
            level: score < 30 ? 'weak' : score < 60 ? 'fair' : score < 80 ? 'good' : 'strong'
        };
    }

    // Método público para inicializar manualmente
    refresh() {
        this.setupPasswordValidators();
    }

    // Método público para destruir todos los validadores
    destroy() {
        const containers = document.querySelectorAll('.password-validator-container');
        containers.forEach(container => {
            container.remove();
        });
        
        const inputs = document.querySelectorAll('input[data-password-validator-initialized]');
        inputs.forEach(input => {
            input.removeAttribute('data-password-validator-initialized');
            input.classList.remove('password-weak', 'password-fair', 'password-good', 'password-strong');
        });
    }
}

// Función de inicialización global
function initPasswordValidators() {
    window.passwordValidator = new PasswordValidator();
}

// Auto-inicialización
initPasswordValidators();

// Exportar para uso global
window.PasswordValidator = PasswordValidator;

// Evento personalizado para cuando se carga contenido dinámico
document.addEventListener('contentLoaded', () => {
    if (window.passwordValidator) {
        window.passwordValidator.refresh();
    }
});

console.log('Password Validator Component loaded');

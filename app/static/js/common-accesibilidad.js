// Common Accessibility Utilities - applies site-wide
(function(global){
  function aplicarAccesibilidad() {
    try {
      const body = document.body;
      const altoContraste = localStorage.getItem('accesibilidad_alto_contraste') === 'true';
      const tamanoTexto = localStorage.getItem('accesibilidad_tamano_texto') || '100';
      const modoOscuro = localStorage.getItem('accesibilidad_modo_oscuro') === 'true';
      const animaciones = localStorage.getItem('accesibilidad_animaciones') === 'true';
      if (!body) return;
      body.classList.toggle('alto-contraste', altoContraste);
      body.classList.toggle('modo-oscuro', modoOscuro);
      body.classList.toggle('animaciones-reducidas', animaciones);
      body.style.fontSize = tamanoTexto + '%';
    } catch (e) {
      // fail silently
    }
  }

  // expose globally
  global.aplicarAccesibilidad = aplicarAccesibilidad;

  // auto-apply on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', aplicarAccesibilidad);
  } else {
    aplicarAccesibilidad();
  }
})(window);

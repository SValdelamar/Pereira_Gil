// UI Común + Comandos de voz (Web Speech API)
// Versión: 2.0 - Comandos actualizados para todos los módulos (2025-01-23)
(() => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('toggleSidebar');
  const overlay = document.getElementById('sidebarOverlay');

  // Toggle sidebar + overlay on mobile
  function toggleSidebar() {
    sidebar?.classList.toggle('show');
    overlay?.classList.toggle('active');
  }

  if (toggle && sidebar) toggle.addEventListener('click', toggleSidebar);
  if (overlay) overlay.addEventListener('click', toggleSidebar);

  // Validación Bootstrap
  (() => {
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault(); event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  })();

  // --- API JWT Automático ---
  // El token se genera automáticamente al hacer login
  // Obtenemos el token de la sesión (inyectado por Flask)
  const apiJwtStatus = document.getElementById('apiJwtStatus');
  
  // Función para obtener el token actual
  async function getApiToken() {
    try {
      const res = await fetch('/api/get-token');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.token) {
          localStorage.setItem('jwt', data.token);
          return data.token;
        }
      }
    } catch (e) {
      Logger.error('Error obteniendo token:', e);
    }
    return localStorage.getItem('jwt') || null;
  }
  
  // Actualizar estado de API
  async function refreshApiStatus() {
    const token = await getApiToken();
    if (apiJwtStatus) {
      if (token) {
        apiJwtStatus.innerHTML = '<i class="bi bi-check-circle-fill"></i> API Activa';
        apiJwtStatus.className = 'small text-success d-none d-md-inline';
      } else {
        apiJwtStatus.innerHTML = 'API: sin sesión';
        apiJwtStatus.className = 'small text-muted d-none d-md-inline';
      }
    }
  }
  
  function clearJwt() { 
    localStorage.removeItem('jwt'); 
    refreshApiStatus(); 
  }
  
  async function ensureAuthOrPrompt(res) {
    if (res && res.status === 401) { 
      clearJwt(); 
      Logger.showUserMessage('Sesión API expirada. Por favor recarga la página.', 'warning', 3000);
    }
    return res;
  }
  
  window.ApiAuth = { refreshApiStatus, clearJwt, ensureAuthOrPrompt, getApiToken };
  
  // Inicializar token al cargar la página
  refreshApiStatus();

  // Sistema de mensajes unificado con Logger Manager
  function flash(msg, type='info', timeout=3000){
    Logger.showUserMessage(msg, type, timeout);
  }

  // Web Speech API - comandos simples
  const btnVoice = document.getElementById('btnVoice');
  const supported = ('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window);
  if (!supported) {
    if (btnVoice){ 
      btnVoice.disabled = true; 
      btnVoice.title = 'Voz no soportada por este navegador';
      btnVoice.classList.add('btn-outline-secondary');
    }
    Logger.warn('Web Speech API no disponible en este navegador');
    return;
  }
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const rec = new SpeechRecognition();
  rec.lang = 'es-ES';
  rec.interimResults = false; rec.maxAlternatives = 1;

  let activo = false;
  function setListeningState(on){
    activo = on;
    if(btnVoice){
      btnVoice.classList.toggle('active', on);
      btnVoice.innerHTML = on ? '<i class="bi bi-mic-mute"></i>' : '<i class="bi bi-mic"></i>';
      btnVoice.title = on ? 'Detener voz' : 'Comandos de voz';
    }
  }
  function toggleVoz(){
    try{
      if (!activo) { rec.start(); setListeningState(true); flash('🎤 Escuchando...', 'info', 1500); }
      else { rec.stop(); setListeningState(false); flash('🔇 Voz desactivada', 'secondary', 1500); }
    }catch(e){
      Logger.warn('No se pudo iniciar voz: ' + e.message); flash('No se pudo iniciar reconocimiento de voz', 'warning');
    }
  }
  btnVoice?.addEventListener('click', toggleVoz);

  rec.onstart = () => { /* iniciado */ };
  rec.onend = () => { if (activo) { try{ rec.start(); }catch{} } };
  rec.onerror = (e) => {
    Logger.error('Error reconocimiento de voz: ' + e.error);
    setListeningState(false);
    
    if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
      flash('❌ Permiso de micrófono denegado. Por favor, habilita el acceso al micrófono en tu navegador.', 'danger', 6000);
    } else if (e.error === 'no-speech') {
      flash('⚠️ No se detectó voz. Intenta hablar más cerca del micrófono.', 'warning', 4000);
    } else if (e.error === 'audio-capture') {
      flash('❌ No se pudo acceder al micrófono. Verifica que esté conectado.', 'danger', 5000);
    } else if (e.error === 'network') {
      flash('❌ Error de red. Verifica tu conexión a internet.', 'danger', 5000);
    } else {
      flash(`⚠️ Error en reconocimiento de voz: ${e.error}`, 'warning', 4000);
    }
  };

  rec.onresult = async (ev) => {
    const texto = ev.results[0][0].transcript.toLowerCase();
    Logger.debug('Comando de voz detectado:', texto);
    const token = localStorage.getItem('jwt');
    if (token) {
      try {
        const res = await fetch('/api/voz/comando', {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
          body: JSON.stringify({ comando: texto })
        });
        const data = await res.json();
        if (data?.mensaje) flash(data.mensaje, data.exito? 'success':'warning', 4000);
        
        // Ejecutar acciones específicas
        if (data?.accion) {
          switch(data.accion) {
            case 'navegar':
              if (data.url) setTimeout(() => window.location.href = data.url, 1000);
              break;
            case 'crear_equipo':
              flash('💡 Tip: Use el botón "Nuevo" en la página de equipos para crear equipos', 'info', 3000);
              break;
            case 'crear_reserva':
              flash('💡 Tip: Use el botón "Reservar" junto a cada equipo', 'info', 3000);
              break;
            case 'ajustar_stock':
              flash('💡 Tip: Vaya a inventario para ajustar cantidades', 'info', 3000);
              break;
          }
        }
      } catch (e) { 
        Logger.error('Error procesando comando de voz:', e); 
        flash('Error enviando comando', 'danger'); 
      }
    } else {
      // Comandos básicos sin JWT (navegación directa más flexible)
      const cmd = texto.toLowerCase().trim();
      
      // Dashboard / Inicio
      if (cmd.includes('dashboard') || cmd.includes('inicio') || cmd.includes('principal') || cmd.includes('home')) {
        flash('📊 Navegando a Dashboard', 'success', 1500);
        window.location.href = '/dashboard';
      }
      // Gestión
      else if (cmd.includes('laboratorio')) {
        flash('🏢 Navegando a Laboratorios', 'success', 1500);
        window.location.href = '/laboratorios';
      }
      else if (cmd.includes('equipo') && !cmd.includes('reconocimiento')) {
        flash('⚙️ Navegando a Equipos', 'success', 1500);
        window.location.href = '/equipos';
      }
      else if (cmd.includes('inventario') || cmd.includes('stock') || cmd.includes('almacén') || cmd.includes('almacen')) {
        flash('📦 Navegando a Inventario', 'success', 1500);
        window.location.href = '/inventario';
      }
      else if (cmd.includes('reserva')) {
        flash('📅 Navegando a Reservas', 'success', 1500);
        window.location.href = '/reservas';
      }
      else if (cmd.includes('usuario') || cmd.includes('personas') || cmd.includes('gestión de usuarios')) {
        flash('👥 Navegando a Usuarios', 'success', 1500);
        window.location.href = '/usuarios';
      }
      // IA y Automatización
      else if (cmd.includes('facial') || cmd.includes('rostro') || cmd.includes('reconocimiento facial') || cmd.includes('registro facial')) {
        flash('👤 Navegando a Registro Facial', 'success', 1500);
        window.location.href = '/facial';
      }
      else if (cmd.includes('visual') || cmd.includes('reconocimiento visual') || cmd.includes('entrenamiento visual') || cmd.includes('ia visual') || cmd.includes('reconocimiento de equipo')) {
        flash('🤖 Navegando a IA Visual', 'success', 1500);
        window.location.href = '/visual';
      }
      // Búsqueda y Reportes
      else if (cmd.includes('buscar') || cmd.includes('buscador') || cmd.includes('búsqueda')) {
        flash('🔍 Navegando a Inventario', 'success', 1500);
        window.location.href = '/inventario';
      }
      else if (cmd.includes('reporte') || cmd.includes('estadística') || cmd.includes('estadisticas') || cmd.includes('informe')) {
        flash('📈 Navegando a Reportes', 'success', 1500);
        window.location.href = '/reportes';
      }
      // Configuración y Ayuda
      else if (cmd.includes('configuración') || cmd.includes('configuracion') || cmd.includes('ajustes') || cmd.includes('preferencias')) {
        flash('⚙️ Navegando a Configuración', 'success', 1500);
        window.location.href = '/configuracion';
      }
      else if (cmd.includes('accesibilidad')) {
        flash('♿ Abriendo Configuración de Accesibilidad', 'success', 1500);
        // Abrir modal de accesibilidad si existe
        const modal = document.getElementById('modalAccesibilidad');
        if (modal) {
          new bootstrap.Modal(modal).show();
        } else {
          window.location.href = '/configuracion';
        }
      }
      else if (cmd.includes('manual') || cmd.includes('ayuda general') || cmd.includes('documentación') || cmd.includes('documentacion')) {
        flash('📚 Navegando a Ayuda', 'success', 1500);
        window.location.href = '/ayuda';
      }
      else if (cmd.includes('módulo') || cmd.includes('modulos') || cmd.includes('funcionalidades')) {
        flash('🧩 Navegando a Módulos', 'success', 1500);
        window.location.href = '/modulos';
      }
      else if (cmd.includes('mi perfil') || cmd.includes('perfil')) {
        flash('👤 Navegando a Mi Perfil', 'success', 1500);
        window.location.href = '/perfil';
      }
      // Sesión
      else if (cmd.includes('cerrar sesión') || cmd.includes('salir') || cmd.includes('logout') || cmd.includes('desconectar')) {
        flash('👋 Cerrando sesión...', 'info', 1500);
        setTimeout(() => window.location.href = '/logout', 1000);
      }
      // Ayuda
      else if (cmd.includes('ayuda') || cmd.includes('comando') || cmd.includes('qué puedo decir') || cmd.includes('que puedo decir')) {
        flash(`🎤 <strong>Comandos de Voz Disponibles:</strong><br><br>
        <strong>📊 Gestión:</strong><br>
        • Dashboard/Inicio • Laboratorios • Equipos<br>
        • Inventario/Stock • Reservas • Usuarios<br><br>
        <strong>🤖 IA y Automatización:</strong><br>
        • Registro Facial • IA Visual/Reconocimiento Visual<br><br>
        <strong>🔍 Herramientas:</strong><br>
        • Inventario/Buscador • Reportes • Configuración<br>
        • Accesibilidad • Mi Perfil<br><br>
        <strong>📚 Otros:</strong><br>
        • Ayuda • Módulos • Cerrar Sesión<br><br>
        💡 <em>Simplemente diga el nombre del módulo (ej: "inventario", "facial", "equipos")</em>`, 'info', 10000);
      }
      else {
        flash(`❌ <strong>Comando no reconocido:</strong> "${texto}"<br><br>💡 Diga <strong>"ayuda"</strong> para ver todos los comandos disponibles.`, 'warning', 4000);
      }
    }
  };
})();

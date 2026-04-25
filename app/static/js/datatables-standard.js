/**
 * DataTables Standard Configuration
 * Sistema GIL - Centro Minero SENA
 * Configuración estándar para todas las DataTables del sistema
 */

// Configuración base para todas las DataTables
const DataTableConfig = {
    // Configuración responsive
    responsive: true,
    
    // Paginación estándar
    pageLength: 25,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    
    // Idioma español
    language: {
        url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json',
        searchPlaceholder: "Buscar registros...",
        lengthMenu: "Mostrar _MENU_ registros",
        info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
        infoEmpty: "Mostrando 0 a 0 de 0 registros",
        infoFiltered: "(filtrado de _MAX_ registros totales)",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        zeroRecords: "No se encontraron registros coincidentes",
        emptyTable: "No hay datos disponibles en esta tabla",
        paginate: {
            first: "Primero",
            last: "Último",
            next: "Siguiente",
            previous: "Anterior"
        }
    },
    
    // Ordenamiento por defecto
    order: [[0, 'asc']],
    
    // Configuración de columnas responsive
    columnDefs: [
        { 
            responsivePriority: 1,
            targets: 0 // Primera columna siempre visible
        },
        { 
            responsivePriority: 2,
            targets: 1 // Segunda columna siempre visible
        },
        { 
            responsivePriority: 3,
            targets: -1, // Última columna (acciones) siempre visible
            orderable: false,
            className: "text-center"
        }
    ],
    
    // Estilos personalizados
    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
         '<"row"<"col-sm-12"tr>>' +
         '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
    
    // Callbacks
    initComplete: function(settings, json) {
        // Agregar clases personalizadas
        $(this).addClass('table-sena-standard');
        
        // Personalizar el input de búsqueda
        const searchInput = $('.dataTables_filter input');
        searchInput.addClass('form-control form-control-sm');
        searchInput.attr('placeholder', 'Buscar...');
        
        // Personalizar el selector de longitud
        const lengthSelect = $('.dataTables_length select');
        lengthSelect.addClass('form-select form-select-sm');
    },
    
    drawCallback: function(settings) {
        // Aplicar estilos después de cada redraw
        $(this).find('tbody tr').addClass('table-row-hover');
    }
};

// Configuración específica para tablas grandes
const DataTableConfigLarge = {
    ...DataTableConfig,
    pageLength: 50,
    lengthMenu: [[25, 50, 100, 200], [25, 50, 100, 200]],
    scrollX: true,
    scrollY: '400px',
    scrollCollapse: true
};

// Configuración para tablas pequeñas (sin paginación)
const DataTableConfigSmall = {
    ...DataTableConfig,
    paging: false,
    searching: false,
    info: false,
    ordering: true
};

// Función de inicialización estándar
function initializeDataTable(tableId, config = DataTableConfig) {
    try {
        const table = $(`#${tableId}`);
        
        if (!table.length) {
            Logger.error(`Tabla con ID "${tableId}" no encontrada`);
            return null;
        }
        
        // Verificar si ya está inicializada
        if ($.fn.DataTable.isDataTable(table)) {
            table.DataTable().destroy();
        }
        
        // Inicializar con configuración
        const dataTable = table.DataTable(config);
        
        // Agregar eventos personalizados
        addCustomEvents(dataTable);
        
        if (typeof window.Logger !== 'undefined') {
            window.Logger.info(`DataTable "${tableId}" inicializada correctamente`);
        } else {
            console.log(`DataTable "${tableId}" inicializada correctamente`);
        }
        return dataTable;
        
    } catch (error) {
        if (typeof window.Logger !== 'undefined') {
            window.Logger.error(`Error al inicializar DataTable "${tableId}":`, error);
        } else {
            console.error(`Error al inicializar DataTable "${tableId}":`, error);
        }
        return null;
    }
}

// Función para agregar eventos personalizados
function addCustomEvents(dataTable) {
    // Evento de click en fila
    dataTable.on('click', 'tbody tr', function(e) {
        // No activar si se hizo click en botones o enlaces
        if ($(e.target).closest('a, button').length === 0) {
            $(this).toggleClass('selected');
        }
    });
    
    // Evento de hover
    dataTable.on('mouseenter', 'tbody tr', function() {
        $(this).addClass('table-row-hover-effect');
    }).on('mouseleave', 'tbody tr', function() {
        $(this).removeClass('table-row-hover-effect');
    });
}

// Función para actualizar DataTable con nuevos datos
function updateDataTable(tableId, data) {
    try {
        const table = $(`#${tableId}`);
        
        if (!$.fn.DataTable.isDataTable(table)) {
            Logger.error(`DataTable "${tableId}" no está inicializada`);
            return false;
        }
        
        const dataTable = table.DataTable();
        dataTable.clear();
        dataTable.rows.add(data);
        dataTable.draw();
        
        return true;
    } catch (error) {
        Logger.error(`Error al actualizar DataTable "${tableId}":`, error);
        return false;
    }
}

// Función para buscar en DataTable
function searchDataTable(tableId, searchTerm) {
    try {
        const table = $(`#${tableId}`);
        
        if (!$.fn.DataTable.isDataTable(table)) {
            Logger.error(`DataTable "${tableId}" no está inicializada`);
            return false;
        }
        
        const dataTable = table.DataTable();
        dataTable.search(searchTerm).draw();
        
        return true;
    } catch (error) {
        Logger.error(`Error al buscar en DataTable "${tableId}":`, error);
        return false;
    }
}

// Función para exportar DataTable
function exportDataTable(tableId, format = 'csv') {
    try {
        const table = $(`#${tableId}`);
        
        if (!$.fn.DataTable.isDataTable(table)) {
            Logger.error(`DataTable "${tableId}" no está inicializada`);
            return false;
        }
        
        const dataTable = table.DataTable();
        
        switch (format.toLowerCase()) {
            case 'csv':
                dataTable.button().add(0, {
                    extend: 'csv',
                    text: 'Exportar CSV',
                    className: 'btn btn-sm btn-outline-primary'
                });
                break;
            case 'excel':
                dataTable.button().add(0, {
                    extend: 'excel',
                    text: 'Exportar Excel',
                    className: 'btn btn-sm btn-outline-success'
                });
                break;
            case 'pdf':
                dataTable.button().add(0, {
                    extend: 'pdf',
                    text: 'Exportar PDF',
                    className: 'btn btn-sm btn-outline-danger'
                });
                break;
        }
        
        return true;
    } catch (error) {
        Logger.error(`Error al exportar DataTable "${tableId}":`, error);
        return false;
    }
}

// Función para resetear DataTable
function resetDataTable(tableId) {
    try {
        const table = $(`#${tableId}`);
        
        if (!$.fn.DataTable.isDataTable(table)) {
            Logger.error(`DataTable "${tableId}" no está inicializada`);
            return false;
        }
        
        const dataTable = table.DataTable();
        dataTable.search('').columns().search('').draw();
        
        return true;
    } catch (error) {
        Logger.error(`Error al resetear DataTable "${tableId}":`, error);
        return false;
    }
}

// Exportar funciones para uso global
window.DataTableManager = {
    initialize: initializeDataTable,
    update: updateDataTable,
    search: searchDataTable,
    export: exportDataTable,
    reset: resetDataTable,
    configs: {
        standard: DataTableConfig,
        large: DataTableConfigLarge,
        small: DataTableConfigSmall
    }
};

// Auto-inicialización cuando el DOM está listo
$(document).ready(function() {
    // Buscar todas las tablas con clase 'datatable-standard'
    $('.datatable-standard').each(function() {
        const tableId = $(this).attr('id');
        if (tableId) {
            initializeDataTable(tableId);
        }
    });
});

// DataTables Standard Configuration inicializado - Logger Manager maneja la sincronización automáticamente

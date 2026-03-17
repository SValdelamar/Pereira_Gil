# =====================================================================
# Script de PowerShell para Aplicar Correcciones a la Base de Datos
# Sistema de Gestión de Laboratorios - Centro Minero SENA
# =====================================================================

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  APLICAR CORRECCIONES A BASE DE DATOS" -ForegroundColor Cyan
Write-Host "  Sistema de Gestión de Laboratorios - Centro Minero SENA" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Obtener credenciales
$usuario = "root"
$database = "laboratorio_sistema"
$scriptSQL = "scripts\fix_laboratorios.sql"

Write-Host "► Base de datos: $database" -ForegroundColor Yellow
Write-Host "► Usuario: $usuario" -ForegroundColor Yellow
Write-Host "► Script: $scriptSQL" -ForegroundColor Yellow
Write-Host ""

# Verificar que existe el archivo SQL
if (-not (Test-Path $scriptSQL)) {
    Write-Host "✗ ERROR: No se encontró el archivo $scriptSQL" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "► Aplicando correcciones..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar el script SQL
try {
    Get-Content $scriptSQL | mysql -u $usuario -p $database
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host "  ✓✓✓ CORRECCIONES APLICADAS EXITOSAMENTE" -ForegroundColor Green
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Cambios aplicados:" -ForegroundColor Green
        Write-Host "  ✓ Campo area_m2 agregado" -ForegroundColor Green
        Write-Host "  ✓ Campo equipamiento_especializado agregado" -ForegroundColor Green
        Write-Host "  ✓ Campo normas_seguridad agregado" -ForegroundColor Green
        Write-Host "  ✓ Campo fecha_modificacion agregado" -ForegroundColor Green
        Write-Host "  ✓ Tabla logs_sistema creada" -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 Próximo paso: python web_app.py" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host "✗ ERROR: Hubo un problema al aplicar las correcciones" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ ERROR: $_" -ForegroundColor Red
    exit 1
}

# HomeEase 2.0 — диагностика и исправление доступа к фронтенду/бэкенду
# Запуск от администратора рекомендуется (правила брандмауэра).

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=== HomeEase 2.0: диагностика сети ===" -ForegroundColor Cyan

# 1. Docker
Write-Host "`n[1] Контейнеры Docker..." -ForegroundColor Yellow
docker compose -p homeease ps
$down = docker compose -p homeease ps --status exited --status dead -q 2>$null
if ($down) {
    Write-Host "Запуск остановленных сервисов..." -ForegroundColor Yellow
    docker compose -p homeease up -d
}

# 2. Порты
Write-Host "`n[2] Занятость портов..." -ForegroundColor Yellow
foreach ($port in @(8001, 8081, 8083)) {
    $line = netstat -ano | Select-String ":$port\s" | Select-Object -First 1
    if ($line) { Write-Host "  :$port — занят ($line)" } else { Write-Host "  :$port — свободен" }
}

# 3. HTTP-проверка
Write-Host "`n[3] HTTP-проверка..." -ForegroundColor Yellow
function Test-Url($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
        Write-Host "  OK $url -> $($r.StatusCode)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  FAIL $url -> $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}
$backendOk = Test-Url "http://127.0.0.1:8001/health"
$frontendOk = Test-Url "http://127.0.0.1:8081"

# 4. Брандмауэр: Node.js + порты
Write-Host "`n[4] Брандмауэр Windows..." -ForegroundColor Yellow
$nodePath = "C:\Program Files\nodejs\node.exe"
if (-not (Test-Path $nodePath)) {
    $nodePath = (Get-Command node -ErrorAction SilentlyContinue).Source
}
if ($nodePath -and (Test-Path $nodePath)) {
    $ruleName = "Node.js (HomeEase)"
    $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if (-not $existing) {
        try {
            New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Program $nodePath `
                -Action Allow -Profile Private,Public -Protocol TCP -Enabled True | Out-Null
            Write-Host "  Добавлено правило для $nodePath" -ForegroundColor Green
        } catch {
            Write-Host "  Не удалось добавить правило Node.js (нужны права администратора): $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  Правило Node.js уже существует" -ForegroundColor Green
    }
} else {
    Write-Host "  node.exe не найден" -ForegroundColor Red
}

foreach ($port in @(8001, 8081, 8083)) {
    $portRule = "HomeEase TCP $port"
    $existing = Get-NetFirewallRule -DisplayName $portRule -ErrorAction SilentlyContinue
    if (-not $existing) {
        try {
            New-NetFirewallRule -DisplayName $portRule -Direction Inbound -Action Allow `
                -Protocol TCP -LocalPort $port -Profile Private,Public -Enabled True | Out-Null
            Write-Host "  Открыт порт $port" -ForegroundColor Green
        } catch {
            Write-Host "  Порт $port: нужны права администратора" -ForegroundColor Red
        }
    }
}

# 5. Итог
Write-Host "`n=== Итог ===" -ForegroundColor Cyan
if ($backendOk -and $frontendOk) {
    Write-Host "Приложение доступно:" -ForegroundColor Green
    Write-Host "  Backend:  http://127.0.0.1:8001/docs"
    Write-Host "  Frontend: http://127.0.0.1:8081"
    Write-Host "  (используйте 127.0.0.1, если localhost не открывается)"
} else {
    Write-Host "Есть проблемы. Логи фронтенда:" -ForegroundColor Red
    docker compose -p homeease logs frontend --tail 30
    Write-Host "`nЛокальный запуск без Docker: cd frontend; npm install; npm run web"
}

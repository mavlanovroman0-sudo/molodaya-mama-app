# Verify git identity and frontend folder.
# Run from project root:
#   .\scripts\verify-repo-identity.ps1

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

Write-Host "Project root: $root"

if (-not (Test-Path (Join-Path $root ".git"))) {
    Write-Error "FAIL: .git not found. Git root must be the app project folder."
}

$email = git config user.email 2>$null
$name = git config user.name 2>$null

if ([string]::IsNullOrWhiteSpace($email)) {
    Write-Error "FAIL: git user.email is empty. Run: git config user.email `"your@email.com`""
}

if ([string]::IsNullOrWhiteSpace($name)) {
    Write-Error "FAIL: git user.name is empty. Run: git config user.name `"Your Name`""
}

$frontendPkg = Join-Path $root "frontend\package.json"
$frontendApp = Join-Path $root "frontend\app.json"

if (-not (Test-Path $frontendPkg)) {
    Write-Error "FAIL: missing frontend/package.json (Codemagic Project path must be frontend)"
}

if (-not (Test-Path $frontendApp)) {
    Write-Error "FAIL: missing frontend/app.json"
}

Write-Host "OK: user.email = $email"
Write-Host "OK: user.name  = $name"
Write-Host "OK: git root   = $root"
Write-Host "OK: frontend/package.json and app.json found"
Write-Host ""
Write-Host "Reminder: this email must match GitHub owner and Codemagic login."
Write-Host "Codemagic: Application settings -> Project path = frontend"
exit 0

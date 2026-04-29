# ============================================================================
# Quasar ERP — Windows Installer (EN / 中文)
# License-protected Docker deployment
# ============================================================================

param(
    [string]$InstallDir = "$env:USERPROFILE\quasar-erp",
    [string]$SiteName = "erp.local",
    [string]$AdminPassword = "admin"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LicenseFile = Join-Path $ScriptDir "licenses.txt"

# ============================
# Language Selection
# ============================
function Select-Language {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  Quasar ERP - Installer / 安装程序" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Please select language / 请选择语言:" -ForegroundColor White
    Write-Host "  [1] English" -ForegroundColor Green
    Write-Host "  [2] 中文" -ForegroundColor Green
    Write-Host ""
    $choice = Read-Host "  Enter choice (1-2) [1]"
    if ($choice -eq "2") { $script:LANG = "zh" } else { $script:LANG = "en" }
}

function Msg {
    param([string]$Key)
    if ($script:LANG -eq "zh") {
        switch ($Key) {
            "license_title"  { Write-Host "`n=== 软件授权验证 ===" -ForegroundColor Yellow }
            "license_prompt" { Write-Host "请输入授权码: " -NoNewline -ForegroundColor White }
            "license_valid"  { Write-Host "[OK] 授权验证通过" -ForegroundColor Green }
            "license_invalid"{ Write-Host "[ERROR] 授权码无效！安装已终止。" -ForegroundColor Red }
            "license_contact"{ Write-Host "请联系供应商获取有效授权码。" -ForegroundColor Yellow }
            "check_docker"   { Write-Host "[检查] Docker Desktop..." -ForegroundColor Yellow }
            "no_docker"      { Write-Host "[ERROR] 未检测到 Docker Desktop" -ForegroundColor Red }
            "install_docker" { Write-Host "请安装 Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor White }
            "ok_docker"      { Write-Host "[OK] Docker 已就绪" -ForegroundColor Green }
            "deploying"      { Write-Host "[部署] 启动 Quasar ERP 容器..." -ForegroundColor Yellow }
            "complete_title" { Write-Host "`n=========================================" -ForegroundColor Green }
            "complete_msg1"  { Write-Host "  部署完成！" -ForegroundColor Green }
            "complete_msg2"  { Write-Host "  访问 http://localhost" -ForegroundColor Cyan }
            "complete_msg3"  { Write-Host "  用户名: Administrator" -ForegroundColor White }
            "complete_msg4"  { Write-Host "  密码: $AdminPassword" -ForegroundColor White }
        }
    } else {
        switch ($Key) {
            "license_title"  { Write-Host "`n=== Software License Verification ===" -ForegroundColor Yellow }
            "license_prompt" { Write-Host "Enter license key: " -NoNewline -ForegroundColor White }
            "license_valid"  { Write-Host "[OK] License verified" -ForegroundColor Green }
            "license_invalid"{ Write-Host "[ERROR] Invalid license key! Installation aborted." -ForegroundColor Red }
            "license_contact"{ Write-Host "Please contact your vendor for a valid license key." -ForegroundColor Yellow }
            "check_docker"   { Write-Host "[Check] Docker Desktop..." -ForegroundColor Yellow }
            "no_docker"      { Write-Host "[ERROR] Docker Desktop not found" -ForegroundColor Red }
            "install_docker" { Write-Host "Install from: https://www.docker.com/products/docker-desktop/" -ForegroundColor White }
            "ok_docker"      { Write-Host "[OK] Docker ready" -ForegroundColor Green }
            "deploying"      { Write-Host "[Deploy] Starting Quasar ERP containers..." -ForegroundColor Yellow }
            "complete_title" { Write-Host "`n=========================================" -ForegroundColor Green }
            "complete_msg1"  { Write-Host "  Deployment Complete!" -ForegroundColor Green }
            "complete_msg2"  { Write-Host "  Visit http://localhost" -ForegroundColor Cyan }
            "complete_msg3"  { Write-Host "  Username: Administrator" -ForegroundColor White }
            "complete_msg4"  { Write-Host "  Password: $AdminPassword" -ForegroundColor White }
        }
    }
}

# ============================
# License Validation
# ============================
function Verify-License {
    Msg "license_title"
    $key = Read-Host "`n$(Msg 'license_prompt')"

    if (-not (Test-Path $LicenseFile)) {
        Write-Host "[ERROR] License file not found!" -ForegroundColor Red
        pause; exit 1
    }

    $valid = Select-String -Path $LicenseFile -Pattern "^$key$" -SimpleMatch -Quiet
    if ($valid) {
        Msg "license_valid"
    } else {
        Msg "license_invalid"
        Msg "license_contact"
        pause; exit 1
    }
}

# ============================
# Main Install
# ============================
Select-Language
Verify-License

# ---- Docker Check ----
Msg "check_docker"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Msg "no_docker"
    Msg "install_docker"
    pause; exit 1
}
Msg "ok_docker"
docker --version

if (-not (docker compose version 2>$null)) {
    Write-Host "[ERROR] Docker Compose not available" -ForegroundColor Red
    pause; exit 1
}

# ---- Deploy ----
Msg "deploying"

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

Copy-Item "$ScriptDir\..\docker-compose.prod.yml" "$InstallDir\docker-compose.yml" -Force
Copy-Item "$ScriptDir\*" "$InstallDir\deploy\" -Force -Recurse

$env:SITE_NAME = $SiteName
$env:ADMIN_PASSWORD = $AdminPassword

Set-Location $InstallDir
docker compose up -d

# ---- Done ----
Msg "complete_title"
Msg "complete_msg1"
Msg "complete_title"
Msg "complete_msg2"
Msg "complete_msg3"
Msg "complete_msg4"
echo ""
pause

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$mariaRaiz = Join-Path $env:LOCALAPPDATA 'MariaDB-IoT'
if (-not (Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue)) {
    $ejecutable = Join-Path $mariaRaiz 'mariadb-11.4.13-winx64\bin\mariadbd.exe'
    $configuracion = Join-Path $mariaRaiz 'data\my.ini'
    if (-not (Test-Path $ejecutable)) { throw 'Inicia tu servidor MariaDB configurado en .env.' }
    Start-Process -FilePath $ejecutable -ArgumentList "--defaults-file=$configuracion" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}
& .\.venv\Scripts\python.exe manage.py runserver 8003

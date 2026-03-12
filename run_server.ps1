$ScriptDir = $PSScriptRoot
Set-Location $ScriptDir
Write-Host "Starting CultureLog Server from $ScriptDir..."
& "$ScriptDir\..\.venv\Scripts\python.exe" manage.py runserver

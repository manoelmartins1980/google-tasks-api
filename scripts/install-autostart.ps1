# Register (or remove) the scheduled task that starts the API at Windows login.
# Usage: .\scripts\install-autostart.ps1            # install/update and start now
#        .\scripts\install-autostart.ps1 -Remove    # uninstall
param([switch]$Remove)

$Name = "google-tasks-api"
$Dir = Split-Path -Parent $PSScriptRoot

if ($Remove) {
    Unregister-ScheduledTask -TaskName $Name -Confirm:$false
    Write-Output "Task '$Name' removed."
    return
}

# pythonw = no console window; scripts.serve runs without reload and writes logs/api.log
$Action = New-ScheduledTaskAction -Execute "$Dir\.venv\Scripts\pythonw.exe" `
    -Argument "-m scripts.serve" -WorkingDirectory $Dir
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Trigger -Settings $Settings `
    -Description "Local Google Tasks API at http://127.0.0.1:8001" -Force | Out-Null
Start-ScheduledTask -TaskName $Name
Write-Output "Task '$Name' registered and started: http://127.0.0.1:8001/health"

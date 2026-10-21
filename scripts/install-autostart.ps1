# Registra (ou remove) a tarefa agendada que inicia a API no login do Windows.
# Uso:  .\scripts\install-autostart.ps1            # instala/atualiza e inicia agora
#       .\scripts\install-autostart.ps1 -Remove    # remove
param([switch]$Remove)

$Name = "google-tasks-api"
$Dir = Split-Path -Parent $PSScriptRoot

if ($Remove) {
    Unregister-ScheduledTask -TaskName $Name -Confirm:$false
    Write-Output "Tarefa '$Name' removida."
    return
}

# pythonw = sem janela de console; scripts.serve roda sem reload e grava logs/api.log
$Action = New-ScheduledTaskAction -Execute "$Dir\.venv\Scripts\pythonw.exe" `
    -Argument "-m scripts.serve" -WorkingDirectory $Dir
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Trigger -Settings $Settings `
    -Description "API local do Google Tasks em http://127.0.0.1:8001" -Force | Out-Null
Start-ScheduledTask -TaskName $Name
Write-Output "Tarefa '$Name' registrada e iniciada: http://127.0.0.1:8001/health"

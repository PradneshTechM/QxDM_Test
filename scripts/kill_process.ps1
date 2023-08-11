param (
    [int]$pidToKill,
    [string]$processName
)

if ($pidToKill -eq "" -and -not $processName) {
    Write-Host "Both PID and process name are missing."
    exit 1
}

Write-Host "Attempting to kill process with PID: $pidToKill or name: $processName"

# Try to terminate by PID using taskkill
if ($pidToKill -ne "") {
    try {
        $taskkillResult = Start-Process -FilePath "taskkill" -ArgumentList "/PID $pidToKill /F" -Wait -NoNewWindow -PassThru
        if ($taskkillResult.ExitCode -eq 0) {
            Write-Host "Process with PID $pidToKill terminated successfully using taskkill."
            exit 0
        }
    } catch {
        Write-Error "Failed to terminate process with PID $pidToKill using taskkill."
        Write-Error $_.Exception.Message
    }
}

# Try to terminate by process name using taskkill
if ($processName) {
    try {
        $taskkillResult = Start-Process -FilePath "taskkill" -ArgumentList "/IM $processName /F" -Wait -NoNewWindow -PassThru
        if ($taskkillResult.ExitCode -eq 0) {
            Write-Host "Process '$processName' terminated successfully using taskkill."
            exit 0
        }
    } catch {
        Write-Error "Failed to terminate process '$processName' using taskkill."
        Write-Error $_.Exception.Message
    }

    # If taskkill by name fails, use wmic by name
    try {
        $wmicCommand = "wmic process where ""Name='$processName'"" delete"
        $wmicResult = Invoke-Expression $wmicCommand 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Process '$processName' terminated successfully using wmic by name."
            exit 0
        }
    } catch {
        Write-Error "Failed to terminate process '$processName' using wmic by name."
        Write-Error "Error: $wmicResult"
    }
}

Write-Host "Failed to terminate process with both taskkill and wmic."
exit 1

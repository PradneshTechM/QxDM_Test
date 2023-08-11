param (
    [string]$arg1
)

# Validate input
if (-not $arg1 -or -not $arg1 -match '^\d+$') {
    Write-Host "Invalid or missing process ID."
    exit 1
}

$pidToKill = [int]$arg1

Write-Host "Attempting to kill process with PID: $pidToKill"

try {
    $taskkillResult = Start-Process -FilePath "taskkill" -ArgumentList "/PID $pidToKill /F" -Wait -NoNewWindow -PassThru
    if ($taskkillResult.ExitCode -eq 0) {
        Write-Host "Process with PID $pidToKill finished successfully."
    } else {
        Write-Host "Failed to terminate process with PID $pidToKill. Exit code: $($taskkillResult.ExitCode)"
    }
} catch {
    Write-Host "An error occurred while trying to terminate process with PID $pidToKill."
    Write-Host $_.Exception.Message
}

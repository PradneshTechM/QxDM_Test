param (
  [string]$arg1
)

# Validate input
if (-not $arg1 -or -not $arg1 -match '^\d+$') {
  Throw "Invalid or missing process ID."
  exit 1
}

$pidToKill = [int]$arg1

Write-Host "Attempting to kill process with PID: $pidToKill"

# Try taskkill first
try {
  $taskkillResult = Start-Process -FilePath "taskkill" -ArgumentList "/PID $pidToKill /F" -Wait -NoNewWindow -PassThru
  if ($taskkillResult.ExitCode -eq 0) {
    Write-Host "Process with PID $pidToKill finished successfully."
    exit 0
  }
} catch {
  Write-Error "Taskkill failed. Using wmic."
}

# If taskkill fails, use wmic
$wmicCommand = "wmic process where ""ProcessId=$pidToKill"" delete"
$wmicResult = Invoke-Expression $wmicCommand 2>&1

# Check the result of the wmic command
if ($LASTEXITCODE -eq 0) {
  Write-Host "Process with PID $pidToKill terminated successfully."
  exit 0
} else {
  Write-Error "Failed to terminate process with PID $pidToKill using both taskkill and wmic."
  Throw "Error: $wmicResult"
  exit 1
}

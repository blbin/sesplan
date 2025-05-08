<#
.SYNOPSIS
Generates an Alembic migration inside the running backend container and copies it to the local filesystem.

.DESCRIPTION
This script automates the steps described in the project's README for creating a new database migration.
It executes 'alembic revision --autogenerate' inside the container specified by the 'sesplan-backend' name filter
and then uses 'docker cp' to copy the generated migration file to the local 'backend/alembic/versions/' directory.

.PARAMETER Message
A mandatory string describing the changes the migration makes (e.g., "Add user profile fields"). This message
will be used in the 'alembic revision' command and often becomes part of the filename.

.EXAMPLE
.\generate_migration.ps1 -Message "Add owner_id to worlds table"

.NOTES
- Make sure Docker Desktop is running and the 'sesplan-backend' container is up ('docker compose up -d backend').
- Assumes the script is run from the project root directory (where docker-compose.yml is located).
- Requires Docker Compose V2 (commands like 'docker compose' instead of 'docker-compose').
- Basic error handling included, but review output carefully.
#>
param(
    [Parameter(Mandatory=$true, HelpMessage="Description of the migration changes.")]
    [string]$Message
)

Write-Host "--- Starting Migration Generation ---"

# --- Step 1: Run Alembic Revision ---
Write-Host "Running 'alembic revision --autogenerate' in the backend container..."
$AlembicCommand = "docker compose exec backend alembic revision --autogenerate -m ""$Message"""
Write-Verbose "Executing: $AlembicCommand" # Verbose output for debugging

try {
    # Execute and capture all output streams (stdout and stderr)
    $revisionOutput = Invoke-Expression $AlembicCommand 2>&1 | Out-String
    Write-Host $revisionOutput -ForegroundColor Cyan # Display output to user
} catch {
    Write-Error "Failed to execute 'alembic revision'. Error: $($_.Exception.Message)"
    # Display captured output even on failure, if any
    if ($revisionOutput) { Write-Warning "Output from failed command:`n$revisionOutput" }
    exit 1
}

# Basic check if the command output indicates an error or no changes detected
if ($LASTEXITCODE -ne 0 -or $revisionOutput -match "ERROR|Target database is not up to date|No changes detected") {
     Write-Warning "Alembic revision command exited with code $LASTEXITCODE or indicated potential issues (Error/No changes). Please review the output above."
     # Decide whether to exit or continue based on 'No changes detected'
     if ($revisionOutput -notmatch "No changes detected") {
        exit 1 # Exit on actual errors
     } else {
         Write-Host "'No changes detected' by Alembic. Exiting script."
         exit 0 # Exit successfully if no changes
     }
}

# --- Step 2: Extract Generated Filename ---
Write-Host "Extracting generated migration filename..."
$generationLine = $revisionOutput.Split([System.Environment]::NewLine) | Where-Object { $_ -like "Generating *" }

if (-not $generationLine) {
    Write-Error "Could not find 'Generating ...' line in Alembic output. Unable to determine filename. Please check output manually."
    exit 1
}

# Extract the path (e.g., /app/alembic/versions/abcdef12345_my_migration.py)
# Regex might be more robust, but splitting works for the expected format
try {
    $generatedPath = ($generationLine -split ' ')[1].Trim()
    $generatedFilename = Split-Path -Leaf $generatedPath
} catch {
     Write-Error "Error parsing filename from '$generationLine': $($_.Exception.Message)"
     exit 1
}


if ([string]::IsNullOrWhiteSpace($generatedFilename)) {
    Write-Error "Could not extract a valid filename from path: '$generatedPath'"
    exit 1
}
Write-Host "Detected migration file: $generatedFilename" -ForegroundColor Green

# --- Step 3: Find Container ID ---
Write-Host "Finding backend container ID..."
$Filter = "name=sesplan-backend" # Filter as per README
$DockerPsCommand = "docker ps --filter '$Filter' -q"
Write-Verbose "Executing: $DockerPsCommand"

try {
    $containerIdOutput = Invoke-Expression $DockerPsCommand 2>&1 | Out-String
    $containerIds = $containerIdOutput.Split([System.Environment]::NewLine) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    if ($containerIds.Length -eq 0) {
        throw "No running container found with filter '$Filter'."
    } elseif ($containerIds.Length -gt 1) {
        Write-Warning "Multiple containers found with filter '$Filter'. Using the first one: $($containerIds[0])"
        $containerId = $containerIds[0]
    } else {
        $containerId = $containerIds[0]
    }
    $containerId = $containerId.Trim()
    Write-Host "Using container ID: $containerId" -ForegroundColor Green
} catch {
     Write-Error "Failed to find container ID. Error: $($_.Exception.Message)"
     if ($containerIdOutput) { Write-Warning "Output from failed command:`n$containerIdOutput" }
     exit 1
}

# --- Step 4: Copy File from Container ---
$sourcePath = "/app/alembic/versions/$generatedFilename" # Path inside the container
$destinationPath = "backend/alembic/versions/"       # Local destination directory

Write-Host "Copying '$sourcePath' from container '$containerId' to local '$destinationPath'..."
$DockerCpCommand = "docker cp '$containerId`:$sourcePath' '$destinationPath'" # Use backtick ` to escape : in PS
Write-Verbose "Executing: $DockerCpCommand"

try {
    Invoke-Expression $DockerCpCommand 2>&1 | Out-String # Capture output, but don't display unless error
    if ($LASTEXITCODE -ne 0) { throw "docker cp command failed." } # Check exit code
    Write-Host "Migration file copied successfully." -ForegroundColor Green
} catch {
     Write-Error "Failed to copy migration file '$generatedFilename'. Error: $($_.Exception.Message)"
     exit 1
}

Write-Host "--- Migration Generation Script Finished Successfully ---"
Write-Host "Don't forget to check the generated migration file and commit it to Git."
exit 0

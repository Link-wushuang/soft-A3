$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dest = Join-Path $root "submission_package"

if (Test-Path $dest) {
    Remove-Item -Recurse -Force $dest
}

New-Item -ItemType Directory -Path $dest | Out-Null

function Copy-CleanDirectory {
    param(
        [string]$Source,
        [string]$Target,
        [string[]]$ExcludeDirs = @(),
        [string[]]$ExcludeFiles = @()
    )

    New-Item -ItemType Directory -Path $Target -Force | Out-Null
    Get-ChildItem -Path $Source -Recurse -Force | ForEach-Object {
        $relative = $_.FullName.Substring($Source.Length).TrimStart('\')
        if (-not $relative) { return }

        foreach ($dir in $ExcludeDirs) {
            if ($relative -eq $dir -or $relative.StartsWith("$dir\") -or $relative.Contains("\$dir\") -or $relative.EndsWith("\$dir")) { return }
        }
        if (-not $_.PSIsContainer -and ($ExcludeFiles -contains $_.Name)) { return }
        if (-not $_.PSIsContainer -and $_.Extension -in @(".pyc", ".db", ".sqlite3", ".log")) { return }

        $targetPath = Join-Path $Target $relative
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        } else {
            New-Item -ItemType Directory -Path (Split-Path -Parent $targetPath) -Force | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $targetPath -Force
        }
    }
}

Copy-CleanDirectory -Source (Join-Path $root "backend") -Target (Join-Path $dest "backend") -ExcludeDirs @("__pycache__", ".pytest_cache") -ExcludeFiles @(".env")
Copy-CleanDirectory -Source (Join-Path $root "frontend") -Target (Join-Path $dest "frontend") -ExcludeDirs @("node_modules", "dist")
Copy-CleanDirectory -Source (Join-Path $root "data") -Target (Join-Path $dest "data")
Copy-CleanDirectory -Source (Join-Path $root "docs") -Target (Join-Path $dest "docs")
Copy-CleanDirectory -Source (Join-Path $root "scripts") -Target (Join-Path $dest "scripts")

Copy-Item -LiteralPath (Join-Path $root "README.md") -Destination (Join-Path $dest "README.md") -Force
Copy-Item -LiteralPath (Join-Path $root ".gitignore") -Destination (Join-Path $dest ".gitignore") -Force

$patterns = @(
    "^\s*SPARK_API_KEY\s*=\s*\S+",
    "^\s*SPARK_API_SECRET\s*=\s*\S+",
    "^\s*DEEPSEEK_API_KEY\s*=\s*\S+",
    "sk-[A-Za-z0-9]{16,}"
)

$hits = foreach ($pattern in $patterns) {
    Get-ChildItem -Path $dest -Recurse -File | Select-String -Pattern $pattern -CaseSensitive
}

if ($hits) {
    Write-Warning "Found potential secrets in submission_package:"
    $hits | ForEach-Object { Write-Warning "$($_.Path):$($_.LineNumber)" }
    exit 1
}

Write-Host "No secrets found. Package ready at $dest"

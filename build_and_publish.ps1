# 0. check git-status
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Error "❌ The working directory is not clean! Commit or revert the changes:"
    git status -s
    exit 1
}

# --- 1. Bump version ---
$versionFile = "pyproject.toml"
$content = Get-Content $versionFile -Raw

# Remove BOM if present
if ($content.Length -gt 0 -and $content[0] -eq [char]0xFEFF) {
    Write-Host "BOM detected in pyproject.toml - removing..."
    $content = $content.Substring(1)
}

# Extract current version
$versionMatch = [regex]::Match($content, "version\s*=\s*""([\d\.]+)""")
if (-not $versionMatch.Success) {
    Write-Host "ERROR: version not found in pyproject.toml"
    exit 1
}

$version = $versionMatch.Groups[1].Value

$parts = $version.Split(".")
$major = [int]$parts[0]
$minor = [int]$parts[1]
$patch = [int]$parts[2]

# PATCH bump
$patch++
$newVersion = "$major.$minor.$patch"

# Update version in pyproject.toml (BOM-safe)
$content = $content -replace "version\s*=\s*""[\d\.]+""", "version = ""$newVersion"""

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($versionFile, $content, $utf8NoBom)

Write-Host "Version bumped: $version -> $newVersion"

# --- Generate version.py inside package folder ---
$currentDir = Get-Location
$parentFolderName = Split-Path $currentDir -Leaf
$versionPyPath = Join-Path $parentFolderName "version.py"

$versionPyContent = "__version__ = ""$newVersion"""
[System.IO.File]::WriteAllText($versionPyPath, $versionPyContent, $utf8NoBom)

Write-Host "version.py generated: $versionPyPath"

# -----------------------------
# 6. Git commit
# -----------------------------
git add pyproject.toml $VersionPyPath
git commit -m "chore: bump version to v$newVersion"

# --- 2. Build & Publish to PyPI ---
poetry build
poetry publish

# --- 3. Read version from version.py ---
$currentDir = Get-Location
$parentFolderName = Split-Path $currentDir -Leaf

$versionFile = Join-Path $parentFolderName "version.py"
$version = Get-Content $versionFile

$version = ($version | Select-String "__version__\s*=\s*""(.+)""").Matches[0].Groups[1].Value

Write-Host "Package name: $parentFolderName"
Write-Host "Version: $version"



$tag = "v$newVersion"

git tag $tag
git push
git push origin $tag

# -----------------------------# -----------------------------
# 10. Generate Release Notes
# -----------------------------

$previousTag = git describe --tags --abbrev=0 $tag~1 2>$null

if ($LASTEXITCODE -eq 0 -and $previousTag) {
    $commits = git log $previousTag..HEAD --pretty=format:"%s"
} else {
    $commits = git log --pretty=format:"%s"
}

$added = @()
$fixed = @()
$changed = @()
$others = @()

foreach ($c in $commits) {
    if ($c -match "^feat") { $added += "- $c" }
    elseif ($c -match "^fix") { $fixed += "- $c" }
    elseif ($c -match "^refactor|^chore") { $changed += "- $c" }
    else { $others += "- $c" }
}

$releaseNotes = "## Release v$newVersion`n`n"
if ($added.Count -gt 0)   { $releaseNotes += "### Added`n"   + ($added -join "`n")   + "`n`n" }
if ($fixed.Count -gt 0)   { $releaseNotes += "### Fixed`n"   + ($fixed -join "`n")   + "`n`n" }
if ($changed.Count -gt 0) { $releaseNotes += "### Changed`n" + ($changed -join "`n") + "`n`n" }
if ($others.Count -gt 0)  { $releaseNotes += "### Other`n"   + ($others -join "`n")  + "`n`n" }

# -----------------------------
# 11. Collect ALL latest dist assets ✅
# -----------------------------

$assets = Get-ChildItem dist -File | ForEach-Object { $_.FullName }

$assets = Get-ChildItem dist -File | Where-Object { $_.Name -match [regex]::Escape($newVersion) } | ForEach-Object { $_.FullName }

if ($assets.Count -eq 0) {
    Write-Error "❌ No files found in dist/ for version $newVersion!"
    exit 1
}

Write-Host "✅ Release assets:"
$assets | ForEach-Object { Write-Host " - $_" }

# -----------------------------
# 12. Create GitHub Release via gh ✅
# -----------------------------

$ghExists = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghExists) {
    Write-Host "ERROR: GitHub CLI (gh) is not installed. Skipping GitHub Release."
    Write-Host "Install with: winget install --id GitHub.cli"
    exit 0
}

# ✅ Properly check if release already exists
$releaseExists = gh release view $tag 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitHub Release $tag already exists. Skipping creation."
} else {
    Write-Host "🚀 Creating GitHub Release $tag ..."

    gh release create $tag $assets `
        --title "v$newVersion" `
        --notes "$releaseNotes"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub Release $tag successfully created."
    } else {
        Write-Host "❌ ERROR: Failed to create GitHub Release."
    }
}
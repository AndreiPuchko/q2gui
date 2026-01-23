param (
    [string]$SrcDir = "q2gui",
    [string]$LocaleDir = "q2gui/locale",
    [string]$Domain = "q2gui",
    [string[]]$Languages = @("de", "ru")
)

# --- config ---
$XGETTEXT = "xgettext"
$MSGMERGE = "msgmerge"
$MSGFMT   = "msgfmt"

$PotFile = Join-Path $LocaleDir "$Domain.pot"

Write-Host "== i18n update ==" -ForegroundColor Cyan

# --- collect python files ---
$PyFiles = Get-ChildItem -Path $SrcDir -Recurse -Filter *.py | ForEach-Object {
    $_.FullName
}

if ($PyFiles.Count -eq 0) {
    Write-Error "No Python files found in $SrcDir"
    exit 1
}

# --- extract strings ---
Write-Host "Extracting strings → $PotFile"

& $XGETTEXT `
    -L Python `
    --from-code=UTF-8 `
    --keyword=_ `
    --keyword=tr `
    --keyword=ngettext:1,2 `
    --keyword=pgettext:1c,2 `
    --add-comments=TRANSLATORS `
    -o $PotFile `
    $PyFiles

if ($LASTEXITCODE -ne 0) {
    Write-Error "xgettext failed"
    exit 1
}

# --- update languages ---
foreach ($Lang in $Languages) {
    $PoDir = Join-Path $LocaleDir $Lang
    $PoFile = Join-Path $PoDir "$Lang.po"
    $MoDir = Join-Path $LocaleDir "$Lang\LC_MESSAGES"
    $MoFile = Join-Path $MoDir "$Domain.mo"

    if (!(Test-Path $PoDir)) {
        New-Item -ItemType Directory -Path $PoDir | Out-Null
    }

    if (!(Test-Path $PoFile)) {
        Write-Host "Creating $PoFile"
        msginit --no-translator -i $PotFile -l $Lang -o $PoFile
    }
    else {
        Write-Host "Updating $PoFile"
        & $MSGMERGE -U $PoFile $PotFile
    }

    # compile .mo
    New-Item -ItemType Directory -Path $MoDir -Force | Out-Null
    & $MSGFMT $PoFile -o $MoFile
}

Write-Host "Done *" -ForegroundColor Green

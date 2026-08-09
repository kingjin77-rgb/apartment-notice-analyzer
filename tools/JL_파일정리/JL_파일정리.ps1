# =====================================================================
#  법무법인 제이엘 · 분양공고 분석 파일 자동정리
#  ---------------------------------------------------------------
#  받은 파일을 D드라이브에 단지별 폴더로 자동 분류·저장합니다.
#  사용법:  JL_파일정리_실행.bat (1회 정리) / JL_자동감시_시작.bat (상시)
# =====================================================================

param(
    [string]$SourceDir = "",                       # 비워두면 아래 기본 감시 폴더 사용
    [string]$RootDir   = "D:\JL_분양공고분석",      # ★ 저장 위치 (여기만 바꾸면 됩니다)
    [switch]$Watch,                                # 상시 감시 모드
    [switch]$Copy,                                 # 이동 대신 복사 (원본 유지)
    [switch]$WhatIf                                # 실제로 옮기지 않고 결과만 보기
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ── 감시 대상 폴더 (여러 곳 가능) ────────────────────────────────
$DefaultSources = @(
    (Join-Path $env:USERPROFILE "Downloads"),
    "D:\DDownloads"
)
$Sources = if ($SourceDir) { @($SourceDir) } else { $DefaultSources | Where-Object { Test-Path $_ } }

# ── 사전 로드 ────────────────────────────────────────────────────
$DictPath = Join-Path $PSScriptRoot "projects.json"
if (-not (Test-Path $DictPath)) { Write-Host "[오류] projects.json 이 없습니다: $DictPath" -ForegroundColor Red; exit 1 }
$Dict = Get-Content $DictPath -Raw -Encoding UTF8 | ConvertFrom-Json

$LogPath = Join-Path $RootDir "_정리기록.csv"

function Write-Log($action, $src, $dst, $proj, $cat) {
    $dir = Split-Path $LogPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    if (-not (Test-Path $LogPath)) {
        "일시,동작,단지,분류,원본파일,저장위치" | Out-File $LogPath -Encoding UTF8
    }
    $line = '{0},{1},{2},{3},"{4}","{5}"' -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $action, $proj, $cat, $src, $dst
    $line | Out-File $LogPath -Append -Encoding UTF8
}

# ── 파일명 정규화(공백·기호 제거, 소문자) ────────────────────────
function Normalize($s) { ($s -replace '[\s_\-\.\(\)\[\]]', '').ToLower() }

# ── 단지 판별 ────────────────────────────────────────────────────
function Get-Project($fileName) {
    $n = Normalize $fileName
    $best = $null; $bestHits = 0
    foreach ($p in $Dict.projects) {
        $hits = 0
        foreach ($k in $p.keywords) { if ($n.Contains((Normalize $k))) { $hits++ } }
        if ($hits -gt $bestHits) { $bestHits = $hits; $best = $p.folder }
    }
    if ($best) { return $best } else { return "_미분류" }
}

# ── 분류(하위 폴더) 판별 ─────────────────────────────────────────
function Get-Category($fileName) {
    $n   = Normalize $fileName
    $ext = [System.IO.Path]::GetExtension($fileName).ToLower()
    foreach ($c in $Dict.categories) {
        foreach ($m in $c.match_name) { if ($n.Contains((Normalize $m))) { return $c.folder } }
    }
    foreach ($c in $Dict.categories) {
        if ($c.ext -and ($c.ext -contains $ext)) { return $c.folder }
    }
    return "00_기타"
}

# ── 중복 이름 회피 ───────────────────────────────────────────────
function Get-UniquePath($dir, $name) {
    $target = Join-Path $dir $name
    if (-not (Test-Path $target)) { return $target }
    $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
    $ext  = [System.IO.Path]::GetExtension($name)
    $stamp = Get-Date -Format "yyyyMMdd_HHmm"
    $target = Join-Path $dir ("{0}_{1}{2}" -f $base, $stamp, $ext)
    $i = 2
    while (Test-Path $target) {
        $target = Join-Path $dir ("{0}_{1}_{2}{3}" -f $base, $stamp, $i, $ext); $i++
    }
    return $target
}

# ── 파일 1건 처리 ────────────────────────────────────────────────
$Handled = @('.pptx','.ppt','.pdf','.docx','.doc','.hwp','.xlsx','.xls','.csv','.json','.html','.htm','.bundle','.zip','.txt','.md','.png','.jpg')

function Move-One($file) {
    try {
        if (-not (Test-Path $file)) { return }
        $item = Get-Item -LiteralPath $file
        if ($item.PSIsContainer) { return }
        $ext = $item.Extension.ToLower()
        if ($Handled -notcontains $ext) { return }
        if ($item.Name -like "~$*" -or $ext -eq ".crdownload" -or $ext -eq ".tmp" -or $ext -eq ".part") { return }

        # 다운로드가 끝날 때까지 잠깐 대기 (잠금 해제 확인)
        for ($t = 0; $t -lt 20; $t++) {
            try { $fs = [System.IO.File]::Open($item.FullName,'Open','Read','None'); $fs.Close(); break }
            catch { Start-Sleep -Milliseconds 500 }
        }

        $proj = Get-Project $item.Name
        $cat  = Get-Category $item.Name
        $destDir = Join-Path (Join-Path $RootDir $proj) $cat
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        $dest = Get-UniquePath $destDir $item.Name

        $verb = if ($Copy) { "복사" } else { "이동" }
        if ($WhatIf) {
            Write-Host ("  [미리보기] {0} → {1}\{2}" -f $item.Name, $proj, $cat) -ForegroundColor DarkGray
            return
        }
        if ($Copy) { Copy-Item -LiteralPath $item.FullName -Destination $dest -Force }
        else       { Move-Item -LiteralPath $item.FullName -Destination $dest -Force }

        $color = if ($proj -eq "_미분류") { "Yellow" } else { "Green" }
        Write-Host ("  [{0}] {1}" -f $verb, $item.Name) -ForegroundColor $color
        Write-Host ("         → {0}\{1}" -f $proj, $cat) -ForegroundColor DarkGray
        Write-Log $verb $item.FullName $dest $proj $cat
    }
    catch {
        Write-Host ("  [실패] {0} : {1}" -f (Split-Path $file -Leaf), $_.Exception.Message) -ForegroundColor Red
    }
}

# ── 시작 ─────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  법무법인 제이엘 · 분양공고 분석 파일 자동정리" -ForegroundColor Cyan
Write-Host "  ---------------------------------------------" -ForegroundColor DarkCyan
Write-Host ("  저장 위치 : {0}" -f $RootDir)
Write-Host ("  감시 폴더 : {0}" -f ($Sources -join " , "))
Write-Host ""

if (-not (Test-Path $RootDir)) {
    New-Item -ItemType Directory -Path $RootDir -Force | Out-Null
    Write-Host "  저장 폴더를 새로 만들었습니다." -ForegroundColor DarkGray
}

# 단지 폴더 미리 생성
foreach ($p in $Dict.projects) {
    $d = Join-Path $RootDir $p.folder
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# ── 1회 정리 ─────────────────────────────────────────────────────
Write-Host "  기존 파일부터 정리합니다..." -ForegroundColor White
$count = 0
foreach ($s in $Sources) {
    Get-ChildItem -LiteralPath $s -File -ErrorAction SilentlyContinue | ForEach-Object {
        $before = $_.FullName
        Move-One $before
        if (-not (Test-Path $before)) { $count++ }
    }
}
Write-Host ("  정리 완료 — {0}건" -f $count) -ForegroundColor Cyan
Write-Host ""

# ── 상시 감시 ────────────────────────────────────────────────────
if ($Watch) {
    Write-Host "  이제부터 새로 들어오는 파일을 자동으로 정리합니다." -ForegroundColor White
    Write-Host "  이 창을 닫으면 감시가 멈춥니다.  (종료: Ctrl + C)" -ForegroundColor DarkGray
    Write-Host ""

    $watchers = @()
    foreach ($s in $Sources) {
        $w = New-Object System.IO.FileSystemWatcher
        $w.Path = $s
        $w.IncludeSubdirectories = $false
        $w.EnableRaisingEvents = $true
        $watchers += $w
        Register-ObjectEvent -InputObject $w -EventName Created -SourceIdentifier ("JL_" + [guid]::NewGuid()) | Out-Null
        Register-ObjectEvent -InputObject $w -EventName Renamed -SourceIdentifier ("JL_" + [guid]::NewGuid()) | Out-Null
    }

    try {
        while ($true) {
            $ev = Wait-Event -Timeout 2
            if ($ev) {
                $path = $ev.SourceEventArgs.FullPath
                Remove-Event -EventIdentifier $ev.EventIdentifier
                Start-Sleep -Milliseconds 800
                Move-One $path
            }
        }
    }
    finally {
        Get-EventSubscriber | Where-Object { $_.SourceIdentifier -like "JL_*" } | Unregister-Event
        $watchers | ForEach-Object { $_.EnableRaisingEvents = $false; $_.Dispose() }
    }
}

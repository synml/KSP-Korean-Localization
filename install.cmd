@echo off
rem ---------------------------------------------------------------
rem  KSP Korean Localization - one click manual installer
rem  https://github.com/synml/KSP-Korean-Localization
rem
rem  Usage: just double click. It downloads the latest release itself.
rem    install.cmd [release-zip] [ksp-root]   (args are for the elevated re-run)
rem  This file is a cmd/PowerShell hybrid. Keep it UTF-8 *without* BOM.
rem ---------------------------------------------------------------
chcp 65001 >nul
setlocal
set "KSPCMD=%~f0"
set "KSPZIP=%~1"
set "KSPDIR=%~2"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=[IO.File]::ReadAllText($env:KSPCMD,[Text.Encoding]::UTF8); Invoke-Expression $s.Substring($s.LastIndexOf('#:PSBEGIN'))"
echo.
pause
endlocal
exit /b

#:PSBEGIN
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$Repo = 'synml/KSP-Korean-Localization'
$ModDir = 'KSPKorean'

function Say([string]$msg, [string]$color = 'Gray') { Write-Host $msg -ForegroundColor $color }
function Fail([string]$msg) { Say '' ; Say "[실패] $msg" 'Red' ; exit 1 }

Say ''
Say '================================================' 'Cyan'
Say '  KSP 한국어 패치 설치 도우미' 'Cyan'
Say '================================================' 'Cyan'
Say ''

# ---------------------------------------------------------------
# 1. KSP 설치 경로 찾기
# ---------------------------------------------------------------
function Test-KspRoot([string]$path) {
    if ([string]::IsNullOrWhiteSpace($path)) { return $false }
    try {
        return (Test-Path (Join-Path $path 'KSP_x64.exe')) -or (Test-Path (Join-Path $path 'KSP.exe'))
    } catch { return $false }
}

function Get-SteamLibrary {
    $libs = @()
    foreach ($key in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam')) {
        $root = $null
        try { $root = (Get-ItemProperty -Path $key -ErrorAction Stop).InstallPath } catch {}
        if ([string]::IsNullOrWhiteSpace($root)) { continue }
        $libs += $root
        $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            $text = Get-Content -LiteralPath $vdf -Raw -Encoding UTF8
            foreach ($m in [regex]::Matches($text, '"path"\s*"([^"]+)"')) {
                $libs += $m.Groups[1].Value -replace '\\\\', '\'
            }
        }
    }
    $libs | Select-Object -Unique
}

function Find-KspRoot {
    $found = New-Object System.Collections.Generic.List[string]

    foreach ($lib in Get-SteamLibrary) {
        $found.Add((Join-Path $lib 'steamapps\common\Kerbal Space Program'))
    }

    $subPaths = @(
        'Kerbal Space Program',
        'KSP',
        'Games\Kerbal Space Program',
        'Program Files\Kerbal Space Program',
        'Program Files (x86)\Kerbal Space Program',
        'Program Files (x86)\Steam\steamapps\common\Kerbal Space Program',
        'GOG Games\Kerbal Space Program',
        'Program Files (x86)\GOG Galaxy\Games\Kerbal Space Program',
        'SteamLibrary\steamapps\common\Kerbal Space Program'
    )
    # 로컬 고정 드라이브만 (네트워크 드라이브는 느려서 제외)
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Root -match '^[A-Za-z]:\\$' -and -not $_.DisplayRoot }
    foreach ($drive in $drives) {
        foreach ($sub in $subPaths) { $found.Add((Join-Path $drive.Root $sub)) }
    }

    $found | Where-Object { Test-KspRoot $_ } |
        ForEach-Object { (Resolve-Path -LiteralPath $_).Path } |
        Select-Object -Unique
}

$kspRoot = $null
if ($env:KSPDIR -and (Test-KspRoot $env:KSPDIR)) { $kspRoot = (Resolve-Path -LiteralPath $env:KSPDIR).Path }

if (-not $kspRoot) {
    Say 'KSP 설치 위치를 찾는 중...' 'DarkGray'
    $candidates = @(Find-KspRoot)

    if ($candidates.Count -eq 1) {
        $kspRoot = $candidates[0]
        Say "  발견: $kspRoot" 'Green'
        $answer = Read-Host '이 위치에 설치할까요? [Y/n]'
        if ($answer -and $answer -notmatch '^[Yy]') { $kspRoot = $null }
    } elseif ($candidates.Count -gt 1) {
        Say '  KSP 설치본을 여러 개 찾았습니다.' 'Yellow'
        for ($i = 0; $i -lt $candidates.Count; $i++) { Say ("  [{0}] {1}" -f ($i + 1), $candidates[$i]) }
        $answer = Read-Host ("설치할 번호를 고르세요 [1-{0}] (직접 입력: 0)" -f $candidates.Count)
        $index = 0
        if ([int]::TryParse($answer, [ref]$index) -and $index -ge 1 -and $index -le $candidates.Count) {
            $kspRoot = $candidates[$index - 1]
        }
    } else {
        Say '  자동으로 찾지 못했습니다.' 'Yellow'
    }
}

while (-not $kspRoot) {
    Say ''
    Say 'KSP 설치 폴더(KSP_x64.exe가 있는 폴더)를 입력하거나 창에 끌어다 놓으세요.' 'Yellow'
    $input = (Read-Host '경로 (그냥 Enter 시 취소)').Trim('"', ' ')
    if ([string]::IsNullOrWhiteSpace($input)) { Fail '설치를 취소했습니다.' }
    if (Test-KspRoot $input) {
        $kspRoot = (Resolve-Path -LiteralPath $input).Path
    } else {
        Say "  그 폴더에는 KSP_x64.exe가 없습니다: $input" 'Red'
    }
}

$gameData = Join-Path $kspRoot 'GameData'
if (-not (Test-Path $gameData)) { Fail "GameData 폴더가 없습니다: $gameData" }
Say ''
Say "설치 위치: $kspRoot" 'Green'

# ---------------------------------------------------------------
# 2. 최신 릴리스 zip 내려받기
#    (KSPZIP 인자가 있으면 그 파일 사용 — 관리자 권한 재실행 시 재다운로드 방지용)
# ---------------------------------------------------------------
$zipPath = $null
$downloaded = $false

if ($env:KSPZIP -and (Test-Path -LiteralPath $env:KSPZIP -PathType Leaf)) {
    $zipPath = (Resolve-Path -LiteralPath $env:KSPZIP).Path
    Say ''
    Say "패치 파일: $zipPath" 'Green'
} else {
    Say ''
    Say 'GitHub에서 최신 패치를 내려받는 중...' 'DarkGray'
    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" `
            -Headers @{ 'User-Agent' = 'ksp-korean-installer' } -UseBasicParsing
        $asset = $release.assets | Where-Object { $_.name -like '*.zip' } | Select-Object -First 1
        if (-not $asset) { throw '릴리스에 zip 자산이 없습니다.' }
        $zipPath = Join-Path $env:TEMP $asset.name
        Say ("  {0} ({1}, {2:N1} MB)" -f $asset.name, $release.tag_name, ($asset.size / 1MB)) 'DarkGray'
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath -UseBasicParsing
        $downloaded = $true
        Say '  다운로드 완료' 'Green'
    } catch {
        Fail ("다운로드 실패: {0}`n    인터넷 연결을 확인하거나, 아래에서 zip을 직접 받아 수동 설치해 주세요.`n    https://github.com/$Repo/releases/latest" -f $_.Exception.Message)
    }
}

# ---------------------------------------------------------------
# 3. 압축 해제 후 GameData\KSPKorean 설치
# ---------------------------------------------------------------
$temp = Join-Path $env:TEMP ('kspko_' + [guid]::NewGuid().ToString('N'))
$target = Join-Path $gameData $ModDir

try {
    New-Item -ItemType Directory -Path $temp -Force | Out-Null
    Expand-Archive -LiteralPath $zipPath -DestinationPath $temp -Force

    $source = Get-ChildItem -LiteralPath $temp -Recurse -Directory -Filter $ModDir -ErrorAction SilentlyContinue |
        Where-Object { (Split-Path -Leaf $_.Parent.FullName) -eq 'GameData' } | Select-Object -First 1
    if (-not $source) { Fail "zip 안에서 GameData\$ModDir 폴더를 찾지 못했습니다: $zipPath" }

    if (Test-Path $target) {
        Say ''
        Say "기존 설치본이 있습니다: $target" 'Yellow'
        $answer = Read-Host '지우고 새로 설치할까요? [Y/n]'
        if ($answer -and $answer -notmatch '^[Yy]') { Fail '설치를 취소했습니다.' }
        Remove-Item -LiteralPath $target -Recurse -Force
    }

    Copy-Item -LiteralPath $source.FullName -Destination $gameData -Recurse -Force

    if (-not (Test-Path (Join-Path $target 'Localization\dictionary.ko.cfg'))) {
        Fail '파일 복사가 정상적으로 끝나지 않았습니다.'
    }
} catch [System.UnauthorizedAccessException] {
    Say ''
    Say '쓰기 권한이 없습니다. 관리자 권한으로 다시 실행해야 합니다.' 'Yellow'
    $answer = Read-Host '지금 관리자 권한으로 다시 실행할까요? [Y/n]'
    if (-not $answer -or $answer -match '^[Yy]') {
        $downloaded = $false  # 재실행 프로세스가 쓰도록 zip을 남겨 둔다 (재다운로드 방지)
        Start-Process -FilePath $env:ComSpec -Verb RunAs `
            -ArgumentList @('/c', $env:KSPCMD, $zipPath, $kspRoot)
        exit 0
    }
    Fail '설치를 취소했습니다. install.cmd를 마우스 오른쪽 클릭 → "관리자 권한으로 실행"해 주세요.'
} finally {
    if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
    if ($downloaded -and (Test-Path $zipPath)) { Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue }
}

Say ''
Say '================================================' 'Green'
Say '  설치 완료! KSP를 실행하면 한국어가 적용됩니다.' 'Green'
Say '================================================' 'Green'
Say ''
Say "설치 위치: $target" 'DarkGray'
Say '제거하려면 위 폴더를 삭제하면 됩니다.' 'DarkGray'

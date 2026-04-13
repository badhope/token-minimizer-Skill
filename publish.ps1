<#
.SYNOPSIS
One-click publish script for Token Minimizer Skill / 一键发布脚本
.DESCRIPTION
Automatically create version tag, push to GitHub, trigger release workflow
自动创建版本标签，推送到GitHub，触发发布工作流
#>

param(
    [string]$Version = "v1.0.0",
    [switch]$PreRelease = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "💰 Token Minimizer - One Click Publish Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Check-GitStatus {
    Write-Host "📋 Checking git status..." -ForegroundColor Yellow
    $status = git status --porcelain
    if ($status) {
        Write-Host "❌ Uncommitted changes found:" -ForegroundColor Red
        Write-Host $status
        Write-Host ""
        Write-Host "Please commit or stash changes first" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Working directory clean" -ForegroundColor Green
}

function Create-Release {
    param([string]$v)
    
    Write-Host ""
    Write-Host "🏷️  Creating version tag: $v" -ForegroundColor Yellow
    
    if ($DryRun) {
        Write-Host "📌 [DryRun] Would create tag: $v" -ForegroundColor Gray
        Write-Host "📌 [DryRun] Would push tag to origin" -ForegroundColor Gray
        return
    }
    
    git tag -a $v -m "Release $v"
    git push origin $v
    
    Write-Host "✅ Tag $v pushed to GitHub" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 GitHub Actions will automatically:" -ForegroundColor Cyan
    Write-Host "   • Create GitHub Release with release notes" -ForegroundColor Gray
    Write-Host "   • Generate changelog from commits" -ForegroundColor Gray
    Write-Host "   • Deploy documentation to GitHub Pages" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔗 View release workflow:" -ForegroundColor Yellow
    Write-Host "   https://github.com/badhope/token-minimizer-Skill/actions" -ForegroundColor Blue
}

Check-GitStatus

Write-Host ""
Write-Host "📦 Release Information:" -ForegroundColor Cyan
Write-Host "   Version:     $Version" -ForegroundColor Gray
Write-Host "   Pre-release: $PreRelease" -ForegroundColor Gray
Write-Host "   Dry run:     $DryRun" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "❌ Publish cancelled" -ForegroundColor Red
    exit 0
}

Create-Release -v $Version

Write-Host ""
Write-Host "🎉 Publish initiated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🌍 Your package is AUTOMATICALLY PUBLISHED to these CDNs:" -ForegroundColor Cyan
Write-Host "   (No account, no click, no registration needed! Just wait 5-15 minutes)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   📦 jsDelivr:" -ForegroundColor White
Write-Host "      https://cdn.jsdelivr.net/gh/badhope/token-minimizer-Skill/" -ForegroundColor Blue
Write-Host "   📦 unpkg:" -ForegroundColor White
Write-Host "      https://unpkg.com/token-minimizer-skill/" -ForegroundColor Blue
Write-Host "   📦 Skypack (ESM):" -ForegroundColor White
Write-Host "      https://cdn.skypack.dev/token-minimizer-skill" -ForegroundColor Blue
Write-Host ""
Write-Host "💡 After release, you can:" -ForegroundColor Cyan
Write-Host "   • Monitor release progress: https://github.com/badhope/token-minimizer-Skill/actions" -ForegroundColor Gray
Write-Host "   • Say '抠门' to test your new skill!" -ForegroundColor Gray

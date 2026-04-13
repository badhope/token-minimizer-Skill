#!/bin/bash
# 💰 Token Minimizer - One Click Publish Script / 一键发布脚本
# 自动创建版本标签，推送到GitHub，触发发布工作流
# Usage: ./publish.sh [version] [--dry-run]

set -e

VERSION=${1:-v1.0.0}
DRY_RUN=0

if [[ "$2" == "--dry-run" ]]; then
    DRY_RUN=1
fi

echo -e "\033[0;36m💰 Token Minimizer - One Click Publish Script\033[0m"
echo -e "\033[0;36m========================================\033[0m"
echo ""

echo -e "\033[0;33m📋 Checking git status...\033[0m"
if [[ -n $(git status --porcelain) ]]; then
    echo -e "\033[0;31m❌ Uncommitted changes found:\033[0m"
    git status --porcelain
    echo ""
    echo -e "\033[0;31mPlease commit or stash changes first\033[0m"
    exit 1
fi
echo -e "\033[0;32m✅ Working directory clean\033[0m"

echo ""
echo -e "\033[0;36m📦 Release Information:\033[0m"
echo -e "   Version:     $VERSION"
echo -e "   Dry run:     $DRY_RUN"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\033[0;31m❌ Publish cancelled\033[0m"
    exit 0
fi

echo ""
echo -e "\033[0;33m🏷️  Creating version tag: $VERSION\033[0m"

if [[ $DRY_RUN -eq 1 ]]; then
    echo -e "\033[0;37m📌 [DryRun] Would create tag: $VERSION\033[0m"
    echo -e "\033[0;37m📌 [DryRun] Would push tag to origin\033[0m"
else
    git tag -a "$VERSION" -m "Release $VERSION"
    git push origin "$VERSION"
    
    echo -e "\033[0;32m✅ Tag $VERSION pushed to GitHub\033[0m"
    echo ""
    echo -e "\033[0;36m🚀 GitHub Actions will automatically:\033[0m"
    echo -e "   • Create GitHub Release with release notes"
    echo -e "   • Generate changelog from commits"
    echo -e "   • Deploy documentation to GitHub Pages"
    echo ""
    echo -e "\033[0;33m🔗 View release workflow:\033[0m"
    echo -e "\033[0;34m   https://github.com/badhope/token-minimizer-Skill/actions\033[0m"
fi

echo ""
echo -e "\033[0;32m🎉 Publish initiated successfully!\033[0m"
echo ""
echo -e "\033[0;36m🌍 Your package is AUTOMATICALLY PUBLISHED to these CDNs:\033[0m"
echo -e "\033[0;90m   (No account, no click, no registration needed! Just wait 5-15 minutes)\033[0m"
echo ""
echo -e "   📦 jsDelivr:"
echo -e "\033[0;34m      https://cdn.jsdelivr.net/gh/badhope/token-minimizer-Skill/\033[0m"
echo -e "   📦 unpkg:"
echo -e "\033[0;34m      https://unpkg.com/token-minimizer-skill/\033[0m"
echo -e "   📦 Skypack (ESM):"
echo -e "\033[0;34m      https://cdn.skypack.dev/token-minimizer-skill\033[0m"
echo ""
echo -e "\033[0;36m💡 After release, you can:\033[0m"
echo -e "   • Monitor release progress: https://github.com/badhope/token-minimizer-Skill/actions"
echo -e "   • Say '抠门' to test your new skill!"

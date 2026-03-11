#!/bin/bash
# GitHub推送脚本
# 使用方法: ./push-to-github.sh <your-github-username> <your-github-token>

USERNAME=${1:-}
TOKEN=${2:-}

if [ -z "$USERNAME" ] || [ -z "$TOKEN" ]; then
    echo "用法: ./push-to-github.sh <github-username> <github-token>"
    echo ""
    echo "或者手动执行以下步骤:"
    echo "1. 在GitHub创建仓库: https://github.com/new"
    echo "2. 仓库名称: doc-manager"
    echo "3. 不勾选 'Initialize this repository with a README'"
    echo "4. 执行:"
    echo "   git remote set-url origin https://$USERNAME:$TOKEN@github.com/$USERNAME/doc-manager.git"
    echo "   git push -u origin main"
    exit 1
fi

REPO_URL="https://$USERNAME:$TOKEN@github.com/$USERNAME/doc-manager.git"

echo "设置远程仓库..."
git remote set-url origin "$REPO_URL"

echo "推送到GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 推送成功!"
    echo "仓库地址: https://github.com/$USERNAME/doc-manager"
else
    echo ""
    echo "✗ 推送失败，请检查用户名和token"
fi

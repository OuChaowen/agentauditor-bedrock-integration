#!/bin/bash
# 推送到 GitHub 的自动化脚本

set -e

echo "=================================================="
echo "推送 AgentAuditor-Bedrock 到 GitHub"
echo "=================================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否已经创建了仓库
echo -e "\n${YELLOW}步骤 1: 检查 GitHub 仓库${NC}"
echo "请先在 GitHub 上创建仓库:"
echo "  1. 访问: https://github.com/new"
echo "  2. Repository name: agentauditor-bedrock-integration"
echo "  3. Description: AWS Bedrock integration for AgentAuditor"
echo "  4. Public (公开)"
echo "  5. 不要添加 README, .gitignore, license"
echo ""
read -p "已经创建好仓库了吗？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${RED}请先创建 GitHub 仓库${NC}"
    exit 1
fi

# 添加新的 remote
echo -e "\n${YELLOW}步骤 2: 配置 remote${NC}"

REPO_URL="https://github.com/OuChaowen/agentauditor-bedrock-integration.git"

# 检查是否已存在 my-repo remote
if git remote | grep -q "my-repo"; then
    echo "移除旧的 my-repo remote..."
    git remote remove my-repo
fi

echo "添加新的 remote: my-repo"
git remote add my-repo $REPO_URL

echo -e "${GREEN}✓ Remote 配置完成${NC}"
git remote -v

# 推送到 GitHub
echo -e "\n${YELLOW}步骤 3: 推送代码${NC}"
echo "推送到: $REPO_URL"
echo ""

# 尝试推送
if git push my-repo main; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ 成功推送到 GitHub！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "仓库地址: https://github.com/OuChaowen/agentauditor-bedrock-integration"
    echo ""
    echo "下一步："
    echo "  1. 访问仓库查看代码"
    echo "  2. 重命名 README_DEPLOYMENT.md 为 README.md"
    echo "  3. 添加 Topics 标签"
    echo "  4. 添加 MIT License"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}✗ 推送失败${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "可能的原因："
    echo "  1. 需要 GitHub 认证"
    echo "  2. 仓库名称不匹配"
    echo "  3. 网络问题"
    echo ""
    echo "解决方法："
    echo "  1. 配置 GitHub token:"
    echo "     git remote set-url my-repo https://YOUR_TOKEN@github.com/OuChaowen/agentauditor-bedrock-integration.git"
    echo ""
    echo "  2. 或使用 SSH:"
    echo "     git remote set-url my-repo git@github.com:OuChaowen/agentauditor-bedrock-integration.git"
    echo ""
    echo "  3. 然后重新运行:"
    echo "     git push my-repo main"
    exit 1
fi

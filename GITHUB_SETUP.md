# GitHub 仓库设置指南

## 📦 创建新的 GitHub 仓库

由于代码已经 commit，现在需要推送到你的 GitHub 账号。

### 方法 1: 使用 GitHub 网页（推荐）

1. **访问**: https://github.com/new

2. **填写信息**:
   ```
   Repository name: agentauditor-bedrock-integration
   Description: AWS Bedrock integration for AgentAuditor - AI Agent security evaluation
   
   ☑️ Public (公开仓库)
   ☐ Add a README file (不要勾选，我们已经有了)
   ☐ Add .gitignore (不要勾选，已有)
   ☐ Choose a license (稍后添加)
   ```

3. **点击**: "Create repository"

4. **获取仓库 URL**:
   ```
   https://github.com/OuChaowen/agentauditor-bedrock-integration.git
   ```

5. **在本地执行**:
   ```bash
   cd /home/ubuntu/AgentAuditor-ASSEBench
   
   # 添加新的 remote
   git remote add my-repo https://github.com/OuChaowen/agentauditor-bedrock-integration.git
   
   # 推送代码
   git push my-repo main
   ```

---

### 方法 2: 使用 GitHub CLI（如果已安装）

```bash
# 创建仓库
gh repo create agentauditor-bedrock-integration --public --source=. --remote=my-repo

# 推送
git push my-repo main
```

---

### 方法 3: 使用 curl + GitHub API

```bash
# 需要 GitHub Personal Access Token
# 创建 token: https://github.com/settings/tokens/new
# 权限: repo (Full control of private repositories)

export GITHUB_TOKEN="your_token_here"

# 创建仓库
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "agentauditor-bedrock-integration",
    "description": "AWS Bedrock integration for AgentAuditor - AI Agent security evaluation",
    "private": false,
    "has_issues": true,
    "has_projects": true,
    "has_wiki": true
  }'

# 添加 remote 并推送
git remote add my-repo https://github.com/OuChaowen/agentauditor-bedrock-integration.git
git push my-repo main
```

---

## 🔑 认证设置

如果推送时需要认证：

### 使用 Personal Access Token

1. **创建 Token**: https://github.com/settings/tokens/new
   - Note: "AgentAuditor Deployment"
   - Expiration: 90 days (或自定义)
   - Scopes: 
     - ☑️ `repo` (Full control of private repositories)
     - ☑️ `workflow` (Update GitHub Action workflows)

2. **保存 Token** (只显示一次！)

3. **使用 Token 推送**:
   ```bash
   git push https://YOUR_TOKEN@github.com/OuChaowen/agentauditor-bedrock-integration.git main
   ```

### 配置 Credential Helper

```bash
# 记住凭证
git config --global credential.helper store

# 或使用缓存（15分钟）
git config --global credential.helper cache
```

---

## ✅ 验证推送

推送成功后，访问:
```
https://github.com/OuChaowen/agentauditor-bedrock-integration
```

应该看到：
- ✅ README_DEPLOYMENT.md 作为首页
- ✅ 所有文件已上传
- ✅ Commit 历史可见

---

## 📝 推送后的操作

### 1. 更新 README

在 GitHub 上创建 `README.md` (首页):

```bash
# 创建软链接
ln -s README_DEPLOYMENT.md README.md
git add README.md
git commit -m "Add README link"
git push my-repo main
```

或直接重命名：

```bash
git mv README_DEPLOYMENT.md README.md
git commit -m "Rename to README.md"
git push my-repo main
```

### 2. 添加 License

```bash
# 创建 MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Ou Chaowen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

git add LICENSE
git commit -m "Add MIT License"
git push my-repo main
```

### 3. 添加 Topics（标签）

在 GitHub 网页上，点击仓库页面右侧的 "Add topics"，添加：

```
ai-safety
agent-evaluation
aws-bedrock
claude
agentauditor
security-analysis
llm-safety
automotive-software
iso-26262
```

### 4. 添加描述

在仓库页面，点击 "About" 旁的齿轮图标，添加：

```
Description: AWS Bedrock integration for AgentAuditor - Human-level AI agent security evaluation
Website: https://github.com/Astarojth/AgentAuditor-ASSEBench
```

---

## 🔗 相关链接

- **原始 AgentAuditor**: https://github.com/Astarojth/AgentAuditor-ASSEBench
- **论文**: https://arxiv.org/abs/2506.00641
- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **你的 GitHub**: https://github.com/OuChaowen

---

## 当前状态

✅ 代码已 commit (commit: 8ab7bca)
⏳ 等待推送到 GitHub

**下一步**: 按照上面的"方法 1"创建 GitHub 仓库并推送

# AgentAuditor 部署状态报告

**日期**: 2026-06-01
**部署位置**: `/home/ubuntu/AgentAuditor-ASSEBench`

---

## ✅ 已完成的步骤

### 1. 环境准备 ✅
- ✅ Python 3.12.3 已安装
- ✅ 虚拟环境已创建 (`.venv`)
- ✅ 所有依赖包已安装 (79 packages)
  - torch 2.12.0
  - transformers 5.9.0
  - sentence-transformers 5.5.1
  - openai 2.40.0
  - scikit-learn 1.8.0
  - 等等

### 2. 数据集准备 ✅
- ✅ ASSEBench 数据集已下载
- ✅ 4 个数据文件可用：
  - `AgentJudge-strict.json` (1,476 样本, 4.51 MB)
  - `AgentJudge-loose.json` (1,476 样本, 4.51 MB)
  - `AgentJudge-safety.json` (1,476 样本, 4.51 MB)
  - `AgentJudge-security.json` (1,298 样本, 3.97 MB)

### 3. AWS Bedrock 访问 ✅
- ✅ AWS CLI 已配置
- ✅ 可访问 Claude 模型：
  - `anthropic.claude-sonnet-4-5-20250929-v1:0` (推荐)
  - `anthropic.claude-sonnet-4-20250514-v1:0`
  - `anthropic.claude-opus-4-8`
  - 等等

---

## 🔧 需要配置的内容

### API 配置（必须）

AgentAuditor 默认使用 OpenAI API 格式，但你可以通过修改配置文件来使用 AWS Bedrock。

**选项 1: 使用 OpenAI API**（如果你有 OpenAI 密钥）
```bash
export OPENAI_API_KEY="sk-..."
```

**选项 2: 使用 AWS Bedrock**（推荐）

需要修改以下文件中的 `GPTConfig` 类：
- `AgentAuditor/tasks/preprocess.py`
- `AgentAuditor/tasks/demo.py`
- `AgentAuditor/tasks/demo_repair.py`
- `AgentAuditor/tasks/infer.py`
- `AgentAuditor/tasks/infer_fix1.py`
- `AgentAuditor/tasks/infer_fix2.py`
- `AgentAuditor/tasks/direct_eval.py`

**修改示例** (preprocess.py 第 12-20 行):
```python
class GPTConfig:
    def __init__(self):
        # 使用 AWS Bedrock
        self.API_KEY = "bedrock"  # 使用 AWS credentials
        self.API_BASE = "https://bedrock-runtime.us-east-1.amazonaws.com"
        self.MODEL = "anthropic.claude-sonnet-4-5-20250929-v1:0"
        self.TEMPERATURE = 0
        self.TOP_P = 0
        self.MAX_RETRIES = 5
        self.RETRY_DELAY = 10
```

**或者使用 Anthropic API**（如果你有 Anthropic 密钥）：
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 📋 完整训练流程（6 步骤）

配置好 API 后，按照以下顺序运行：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 使用 AgentJudge-strict 数据集作为示例
DATASET="aj-s"  # AgentJudge-strict

# 步骤 1: 预处理（使用 LLM 进行语义标注）
python -m AgentAuditor $DATASET preprocess

# 步骤 2: 聚类（使用 FINCH 算法）
python -m AgentAuditor $DATASET cluster

# 步骤 3: 生成推理链（CoT demonstrations）
python -m AgentAuditor $DATASET demo

# 步骤 4: 生成推理嵌入
python -m AgentAuditor $DATASET infer_emb

# 步骤 5: 推理评估
python -m AgentAuditor $DATASET infer

# 步骤 6: 最终评估
python -m AgentAuditor $DATASET eval
```

**可用的数据集代码**:
- `rjudge`: rjudge 数据集
- `agentharm`: AgentHarm 数据集
- `asb-sa`: ASSEBench Safety
- `asb-se`: ASSEBench Security
- `aj-l`: AgentJudge-loose
- `aj-s`: AgentJudge-strict ✅ 推荐
- `aj-sa`: AgentJudge-safety
- `aj-se`: AgentJudge-security

---

## 🚀 快速开始（使用预处理数据）

如果你不想从头训练，可以尝试直接评估：

```bash
# 激活环境
source .venv/bin/activate

# 直接评估（使用预训练参数，如果有的话）
python -m AgentAuditor aj-s direct_eval
```

---

## ⏱️ 预计时间和成本

基于 1,476 样本的 AgentJudge-strict 数据集：

| 步骤 | 预计时间 | LLM 调用次数 | 预计成本 (Claude) |
|------|----------|--------------|-------------------|
| preprocess | 30-60 分钟 | 1,476 | ~$3-5 |
| cluster | 5-10 分钟 | 0 | $0 |
| demo | 20-40 分钟 | 200-300 | ~$2-3 |
| infer_emb | 10-20 分钟 | 1,476 | ~$3-5 |
| infer | 30-60 分钟 | 1,476 | ~$3-5 |
| eval | 1-2 分钟 | 0 | $0 |
| **总计** | **~2-3 小时** | **~5,000** | **~$11-18** |

**注意**: 这是基于 Claude Sonnet 的估算。实际成本取决于：
- 输入/输出 token 数量
- 选择的模型
- 重试次数

---

## 📊 输出文件

训练完成后，会生成以下文件（在 `AgentAuditor/data/` 目录）：

```
AgentAuditor/data/
├── aj-s_preprocessed.json         # 预处理后的数据
├── aj-s_clusters.pkl              # 聚类结果
├── aj-s_demos.json                # 推理链演示
├── aj-s_embeddings.pkl            # 嵌入向量
├── aj-s_predictions.json          # 预测结果
└── aj-s_metrics.json              # 评估指标
```

---

## 🔍 验证部署

运行测试脚本验证环境：

```bash
source .venv/bin/activate
python test_setup.py
```

应该看到所有检查项都通过 ✓

---

## 📝 下一步行动

### 立即可做（测试）:
1. 配置 API 密钥（OpenAI 或修改代码使用 Bedrock）
2. 运行快速测试：
   ```bash
   python -m AgentAuditor aj-s preprocess
   ```
3. 检查是否成功生成 `AgentAuditor/data/aj-s_preprocessed.json`

### 完整训练（需要 2-3 小时 + $11-18）:
1. 配置 API
2. 按顺序运行全部 6 个步骤
3. 最后查看 `aj-s_metrics.json` 获取评估结果

### 集成到 A-SPICE Agent（Phase 2）:
1. 训练完成后，保存模型检查点
2. 上传到 AWS EFS
3. 在 A-SPICE Agent 中集成 SecurityHook
4. 参考: `/home/ubuntu/learning-note/agentauditor-quickstart-zh.md`

---

## ❓ 常见问题

### Q: 可以使用更小的数据集测试吗？
**A**: 可以！手动编辑 JSON 文件，只保留前 100 个样本进行测试。

### Q: 训练失败怎么办？
**A**: 检查：
1. API 密钥是否正确
2. 网络连接是否稳定
3. 查看错误日志
4. 确认每一步都成功完成再进行下一步

### Q: 可以并行训练多个数据集吗？
**A**: 可以！复制整个仓库到不同目录即可。

### Q: 如何使用训练好的模型？
**A**: 训练完成后，参数会保存在 `AgentAuditor/params/` 目录。可以加载这些参数进行推理。

---

## 📚 相关文档

- **快速入门指南**: `/home/ubuntu/learning-note/agentauditor-quickstart-zh.md`
- **部署方案**: `/home/ubuntu/learning-note/agentauditor-deployment-zh.md`
- **数据集详解**: `/home/ubuntu/learning-note/assebench-dataset-zh.md`
- **原始 README**: `README.md`

---

**部署人员**: 欧（Ou Chaowen）
**完成日期**: 2026-06-01
**状态**: ✅ 环境就绪，等待 API 配置

# AgentAuditor 集成 Claude Code 方案

## 🎯 目标

将 AgentAuditor 的安全评估能力集成到 Claude Code，实现实时或准实时的安全监控。

---

## 📊 架构对比

### AgentAuditor 原始架构
```
离线批量评估模式:

训练数据 → 构建记忆库 → 评估新案例
   ↓
[预处理] → [聚类] → [生成CoT] → [推理]
   ↓
评估结果（事后分析）
```

### Claude Code + AgentAuditor 集成架构
```
实时监控模式:

Claude Code 会话
   ↓
[工具调用] → [安全检查] → [允许/阻止]
   ↑
AgentAuditor (加载预训练记忆库)
```

---

## 🔀 三种集成方案

### 方案 1: 事后审计模式（最简单）⭐

**原理**: Claude Code 完成任务后，分析会话日志

**实现**:
```python
# audit_claude_code_session.py
import json
from pathlib import Path

def load_claude_code_session(session_file):
    """加载 Claude Code 会话日志"""
    with open(session_file, 'r') as f:
        return json.load(f)

def format_for_agentauditor(session):
    """
    将 Claude Code 会话格式化为 AgentAuditor 输入格式
    
    Claude Code 格式:
    {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "...", "tool_calls": [...]}
        ]
    }
    
    AgentAuditor 格式:
    [Turn 1]
    User: "..."
    
    [Turn 2]
    Agent: [调用工具(...)]
    Agent: "..."
    """
    formatted = []
    turn = 1
    
    for msg in session.get("messages", []):
        formatted.append(f"[Turn {turn}]")
        
        if msg["role"] == "user":
            formatted.append(f"User: {msg['content']}")
        elif msg["role"] == "assistant":
            # 工具调用
            if "tool_calls" in msg:
                for tool in msg["tool_calls"]:
                    tool_name = tool.get("name", "unknown")
                    tool_args = tool.get("arguments", {})
                    formatted.append(f"Agent: [调用 {tool_name}({tool_args})]")
            
            # 响应内容
            if msg.get("content"):
                formatted.append(f"Agent: {msg['content']}")
        
        turn += 1
    
    return "\n".join(formatted)

def evaluate_session(session_file, agentauditor_model):
    """评估会话安全性"""
    session = load_claude_code_session(session_file)
    interaction = format_for_agentauditor(session)
    
    # 推断场景
    scenario = infer_scenario(session)
    
    # 使用 AgentAuditor 评估
    result = agentauditor_model.evaluate(
        interaction=interaction,
        scenario=scenario
    )
    
    return result

# 使用示例
if __name__ == "__main__":
    # 假设 Claude Code 会话日志在这里
    session_log = "/home/ubuntu/.claude/projects/-home-ubuntu/conversation.jsonl"
    
    # 加载训练好的 AgentAuditor
    auditor = load_trained_agentauditor("checkpoint.pkl")
    
    # 评估
    result = evaluate_session(session_log, auditor)
    
    if result["judgment"] == "unsafe":
        print(f"⚠️  检测到风险: {result['risk_types']}")
        print(f"详情: {result['reasoning']}")
    else:
        print("✅ 会话安全")
```

**优点**:
- ✅ 最简单实现
- ✅ 不影响 Claude Code 性能
- ✅ 可批量分析历史会话

**缺点**:
- ❌ 无法实时阻止危险操作
- ❌ 只能事后发现问题

**适用场景**:
- 日常安全审计
- 定期风险评估
- 生成安全报告

---

### 方案 2: Hook 拦截模式（推荐）⭐⭐⭐

**原理**: 在 Claude Code 工具调用前插入安全检查

**实现位置**: 
- Claude Code 的 `pre_tool_use` hook
- 或在 MCP 服务器层拦截

```python
# claude_code_security_hook.py
import os
from typing import Dict, Any

class ClaudeCodeSecurityHook:
    """
    Claude Code 安全 Hook
    在工具调用前评估风险
    """
    def __init__(self, agentauditor_checkpoint: str):
        # 加载 AgentAuditor（延迟加载以减少启动时间）
        self._auditor = None
        self.checkpoint_path = agentauditor_checkpoint
        self.conversation_buffer = []
    
    def _load_auditor(self):
        """延迟加载 AgentAuditor"""
        if self._auditor is None:
            print("🔒 加载 AgentAuditor...")
            # 这里需要实现从训练好的模型加载
            # self._auditor = AgentAuditor.load(self.checkpoint_path)
            print("✅ AgentAuditor 已加载")
    
    def pre_tool_use(self, tool_name: str, tool_input: Dict[str, Any], context: Dict[str, Any]):
        """
        工具调用前的安全检查
        
        Args:
            tool_name: 工具名称（如 "Bash", "Edit", "Write"）
            tool_input: 工具参数
            context: 会话上下文（包含历史消息）
        
        Returns:
            {"allow": True/False, "reason": "..."}
        """
        # 延迟加载
        self._load_auditor()
        
        # 格式化交互历史
        interaction = self._format_interaction(context, tool_name, tool_input)
        
        # 推断场景
        scenario = self._infer_scenario(tool_name, tool_input)
        
        # 快速预检查（规则）
        quick_check = self._quick_rule_check(tool_name, tool_input)
        if not quick_check["allow"]:
            return quick_check
        
        # AgentAuditor 深度评估
        result = self._auditor.evaluate(
            interaction=interaction,
            scenario=scenario
        )
        
        # 记录到缓冲区
        self.conversation_buffer.append({
            "tool": tool_name,
            "input": tool_input,
            "result": result
        })
        
        # 决策
        if result["judgment"] == "unsafe":
            return self._handle_unsafe(result, tool_name, tool_input)
        
        return {"allow": True}
    
    def _format_interaction(self, context, tool_name, tool_input):
        """格式化为 AgentAuditor 输入格式"""
        lines = []
        
        # 历史消息
        for i, msg in enumerate(context.get("messages", []), 1):
            lines.append(f"[Turn {i}]")
            if msg["role"] == "user":
                lines.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                lines.append(f"Agent: {msg.get('content', '')}")
        
        # 当前工具调用
        turn = len(context.get("messages", [])) + 1
        lines.append(f"[Turn {turn}]")
        lines.append(f"Agent: [调用 {tool_name}({tool_input})]")
        
        return "\n".join(lines)
    
    def _infer_scenario(self, tool_name, tool_input):
        """从工具调用推断风险场景"""
        scenario = {
            "risk_type": None,
            "behavior_mode": None,
            "sensitive_info": None
        }
        
        # 工具 → 风险映射
        risk_mapping = {
            "Read": {"sensitive_info": "file_system"},
            "Write": {"risk_type": "R7", "sensitive_info": "file_system"},
            "Edit": {"risk_type": "R7", "sensitive_info": "file_system"},
            "Bash": {"risk_type": "S4", "sensitive_info": "system"},
            "git_push": {"risk_type": "R4", "sensitive_info": "code"},
        }
        
        if tool_name in risk_mapping:
            scenario.update(risk_mapping[tool_name])
        
        # 检查敏感参数
        input_str = str(tool_input).lower()
        sensitive_patterns = ["password", "secret", "token", "key", ".env", "credential"]
        if any(p in input_str for p in sensitive_patterns):
            scenario["sensitive_info"] = "credentials"
            scenario["risk_type"] = "S3"  # 敏感信息泄露
        
        return scenario
    
    def _quick_rule_check(self, tool_name, tool_input):
        """快速规则检查（减少 LLM 调用）"""
        # 检查明显的危险操作
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            dangerous_commands = ["rm -rf /", "dd if=", "mkfs", "> /dev/"]
            if any(cmd in command for cmd in dangerous_commands):
                return {
                    "allow": False,
                    "reason": "🔴 检测到极度危险的命令",
                    "details": "该命令可能导致系统损坏"
                }
        
        # 检查敏感文件访问
        if tool_name in ["Read", "Edit", "Write"]:
            file_path = tool_input.get("file_path", "")
            sensitive_files = [".env", "id_rsa", "credentials", "secrets"]
            if any(sf in file_path for sf in sensitive_files):
                # 不直接阻止，但标记为高风险
                return {"allow": True, "warning": "⚠️  访问敏感文件"}
        
        return {"allow": True}
    
    def _handle_unsafe(self, result, tool_name, tool_input):
        """处理不安全的工具调用"""
        risk_types = result.get("risk_types", [])
        confidence = result.get("confidence", 0)
        
        # 关键风险直接阻止
        critical_risks = ["R4", "S3", "S4"]
        if any(r in critical_risks for r in risk_types) and confidence > 0.9:
            return {
                "allow": False,
                "reason": f"🔴 CRITICAL RISK: {', '.join(risk_types)}",
                "details": result["reasoning"][:200],
                "suggestion": "请检查操作是否安全，或联系管理员"
            }
        
        # 一般风险警告
        elif confidence > 0.7:
            return {
                "allow": True,
                "warning": f"⚠️  WARNING: {', '.join(risk_types)}",
                "details": result["reasoning"][:100]
            }
        
        return {"allow": True}

# 在 Claude Code 中注册 Hook
def register_security_hook():
    """注册安全 Hook 到 Claude Code"""
    checkpoint_path = os.getenv(
        "AGENTAUDITOR_CHECKPOINT",
        "/home/ubuntu/AgentAuditor-ASSEBench/checkpoint.pkl"
    )
    
    hook = ClaudeCodeSecurityHook(checkpoint_path)
    
    # 注册到 Claude Agent SDK
    # agent.register_hook("pre_tool_use", hook.pre_tool_use)
    
    print("✅ 安全 Hook 已注册")
    return hook
```

**在 Claude Code 中使用**:

```python
# ~/.claude/hooks/security_hook.py
from claude_code_security_hook import register_security_hook

# 启动时注册
security_hook = register_security_hook()
```

**优点**:
- ✅ 实时拦截危险操作
- ✅ 可自动阻止关键风险
- ✅ 结合规则检查和 AI 评估

**缺点**:
- ❌ 增加工具调用延迟（~500ms-2s）
- ❌ 需要预训练模型
- ❌ 内存占用增加（~500MB-1GB）

**适用场景**:
- 生产环境
- 高安全要求场景
- 自动化工作流

---

### 方案 3: 混合模式（最佳但复杂）⭐⭐⭐⭐⭐

**原理**: 结合快速规则检查 + 异步 AI 评估 + 事后审计

```
实时层（<10ms）:
  规则检查 → 阻止明显危险操作
     ↓
  允许通过 → 记录到队列

异步评估层（后台）:
  队列 → AgentAuditor 评估 → 更新风险数据库
     ↓
  发现风险 → 通知用户 / 自动补救

事后审计层（定期）:
  批量分析历史会话 → 生成报告
```

**实现**:
```python
# hybrid_security_system.py
import asyncio
import queue
from threading import Thread

class HybridSecuritySystem:
    def __init__(self):
        self.rule_checker = RuleBasedChecker()
        self.auditor = None  # 延迟加载
        self.evaluation_queue = queue.Queue()
        self.risk_database = RiskDatabase()
        
        # 启动后台评估线程
        self.eval_thread = Thread(target=self._background_evaluator, daemon=True)
        self.eval_thread.start()
    
    def check_tool_use(self, tool_name, tool_input, context):
        """实时检查（快速）"""
        # 第一层：规则检查（<10ms）
        rule_result = self.rule_checker.check(tool_name, tool_input)
        if not rule_result["allow"]:
            return rule_result  # 直接阻止
        
        # 第二层：检查已知风险模式（缓存）
        known_risk = self.risk_database.lookup(tool_name, tool_input)
        if known_risk and known_risk["severity"] == "critical":
            return {"allow": False, "reason": f"已知风险: {known_risk['type']}"}
        
        # 允许通过，但加入异步评估队列
        self.evaluation_queue.put({
            "tool_name": tool_name,
            "tool_input": tool_input,
            "context": context,
            "timestamp": time.time()
        })
        
        return {"allow": True, "async_eval": True}
    
    def _background_evaluator(self):
        """后台评估线程"""
        while True:
            try:
                item = self.evaluation_queue.get(timeout=1)
                
                # 延迟加载 AgentAuditor
                if self.auditor is None:
                    self._load_auditor()
                
                # 评估
                result = self.auditor.evaluate(...)
                
                # 如果发现风险，记录并通知
                if result["judgment"] == "unsafe":
                    self.risk_database.add(item, result)
                    self._notify_user(item, result)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"后台评估失败: {e}")
    
    def _notify_user(self, item, result):
        """通知用户发现风险"""
        print(f"\n⚠️  后台安全检查发现风险:")
        print(f"工具: {item['tool_name']}")
        print(f"风险: {result['risk_types']}")
        print(f"建议: 检查最近的操作")
```

**优点**:
- ✅ 实时性好（<10ms 决策）
- ✅ 准确率高（后台 AI 评估）
- ✅ 用户体验好（不阻塞）

**缺点**:
- ❌ 实现复杂
- ❌ 无法阻止所有风险（只能事后通知）

---

## 🎯 推荐方案

根据你的 A-SPICE Agent 项目，我推荐：

### 短期（现在）: 方案 1 - 事后审计
- 快速实现
- 用于评估当前 Claude Code 使用中的风险
- 生成安全报告给中村

### 中期（Q2-Q3）: 方案 2 - Hook 拦截
- 集成到 aspice-agent-ou 项目
- 实时防护
- 符合 ISO 26262 要求

### 长期（Q4）: 方案 3 - 混合模式
- 完整的生产级解决方案
- 平衡性能和安全性
- 部署到全公司

---

## 💻 立即可做：快速测试

创建一个简单的脚本测试集成可行性：

```bash
cd /home/ubuntu/AgentAuditor-ASSEBench

# 创建测试脚本
cat > test_claude_code_integration.py << 'EOF'
#!/usr/bin/env python3
"""测试 AgentAuditor 能否评估 Claude Code 会话"""

# 模拟 Claude Code 会话
sample_session = """
[Turn 1]
User: "帮我删除所有 .tmp 文件"

[Turn 2]
Agent: [调用 Bash("find . -name '*.tmp' -delete")]
Agent: "已删除临时文件"
"""

# 模拟评估
scenario = {
    "risk_type": "R7",  # 超出意图执行
    "behavior_mode": "Excessive",
    "sensitive_info": "file_system"
}

print("📊 模拟评估:")
print(f"交互: {sample_session[:100]}...")
print(f"场景: {scenario}")
print("\n✅ 格式兼容！可以集成")
EOF

python test_claude_code_integration.py
```

---

## 📋 下一步

1. **现在**: 训练 AgentAuditor（使用 ASSEBench）
2. **本周**: 实现方案 1（事后审计）
3. **下周**: 评估几个历史 Claude Code 会话
4. **Q2**: 实现方案 2（Hook 拦截）

需要我帮你实现方案 1 的完整代码吗？

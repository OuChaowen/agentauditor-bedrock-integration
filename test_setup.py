#!/usr/bin/env python3
"""
AgentAuditor 环境测试脚本
"""
import sys
import json

print("=" * 60)
print("AgentAuditor 环境检查")
print("=" * 60)

# 1. 检查 Python 版本
print(f"\n✓ Python 版本: {sys.version}")

# 2. 检查依赖包
required_packages = [
    'numpy', 'torch', 'sklearn', 'openai',
    'sentence_transformers', 'requests', 'backoff',
    'jsonschema', 'tqdm', 'diskcache'
]

print("\n依赖包检查:")
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} (未安装)")

# 3. 检查数据集
import os

print("\nASSEBench 数据集检查:")
dataset_dir = "ASSEBench/dataset"
if os.path.exists(dataset_dir):
    files = os.listdir(dataset_dir)
    for f in files:
        if f.endswith('.json'):
            file_path = os.path.join(dataset_dir, f)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"  ✓ {f} ({file_size:.2f} MB)")
else:
    print(f"  ✗ 数据集目录不存在")

# 4. 检查 API 配置
print("\nAPI 配置检查:")
api_keys = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    'AWS_REGION': os.getenv('AWS_REGION'),
}

for key, value in api_keys.items():
    if value:
        print(f"  ✓ {key}: {'*' * 10} (已设置)")
    else:
        print(f"  ○ {key}: 未设置")

# 5. 加载一个示例数据
print("\n数据加载测试:")
try:
    with open('ASSEBench/dataset/AgentJudge-strict.json', 'r') as f:
        data = json.load(f)
        print(f"  ✓ 成功加载 AgentJudge-strict")
        print(f"  ✓ 样本数量: {len(data)}")
        if data:
            sample = data[0]
            print(f"  ✓ 示例字段: {list(sample.keys())}")
except Exception as e:
    print(f"  ✗ 加载失败: {e}")

print("\n" + "=" * 60)
print("环境检查完成！")
print("=" * 60)

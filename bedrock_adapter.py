#!/usr/bin/env python3
"""
AWS Bedrock 适配器 for AgentAuditor
将 Bedrock API 适配为 OpenAI 兼容格式
"""
import json
import boto3
import time
from typing import Optional, Dict, Any

class BedrockAdapter:
    """
    AWS Bedrock Claude 适配器
    提供 OpenAI 兼容的接口
    """
    def __init__(
        self,
        model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        region: str = "us-east-1",
        max_tokens: int = 4096,
        temperature: float = 0.0
    ):
        self.model_id = model_id
        self.region = region
        self.max_tokens = max_tokens
        self.temperature = temperature

        # 初始化 Bedrock 客户端
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )

        print(f"✅ Bedrock 适配器已初始化")
        print(f"   模型: {model_id}")
        print(f"   区域: {region}")

    def create_completion(
        self,
        messages: list,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        OpenAI 兼容的 completion 接口

        Args:
            messages: [{"role": "user/assistant", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            {"choices": [{"message": {"content": "..."}}]}
        """
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        # 转换为 Bedrock Claude 格式
        bedrock_messages = []
        system_prompt = None

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                bedrock_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # 构造请求
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": bedrock_messages
        }

        if system_prompt:
            request_body["system"] = system_prompt

        # 调用 Bedrock
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # 解析响应
            response_body = json.loads(response['body'].read())

            # 转换为 OpenAI 格式
            content = response_body['content'][0]['text']

            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": response_body.get('stop_reason', 'stop')
                }],
                "usage": {
                    "prompt_tokens": response_body.get('usage', {}).get('input_tokens', 0),
                    "completion_tokens": response_body.get('usage', {}).get('output_tokens', 0),
                    "total_tokens": response_body.get('usage', {}).get('input_tokens', 0) +
                                   response_body.get('usage', {}).get('output_tokens', 0)
                }
            }

        except Exception as e:
            print(f"❌ Bedrock 调用失败: {e}")
            raise

    def chat_completions_create(self, **kwargs):
        """OpenAI chat.completions.create 兼容接口"""
        return self.create_completion(**kwargs)


class BedrockClient:
    """
    模拟 OpenAI Client 的接口
    用于替换 AgentAuditor 中的 OpenAI 客户端
    """
    def __init__(self, model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"):
        self.adapter = BedrockAdapter(model_id=model_id)
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        """OpenAI client.chat.completions.create 接口"""
        return self.adapter.create_completion(**kwargs)


# 测试函数
def test_adapter():
    """测试 Bedrock 适配器"""
    print("\n" + "="*60)
    print("测试 Bedrock 适配器")
    print("="*60)

    try:
        # 初始化适配器
        client = BedrockClient()

        # 测试调用
        print("\n发送测试请求...")
        response = client.create(
            messages=[
                {"role": "user", "content": "Say 'Hello, AgentAuditor!' in one sentence."}
            ],
            temperature=0.0,
            max_tokens=100
        )

        # 输出结果
        content = response['choices'][0]['message']['content']
        usage = response.get('usage', {})

        print(f"\n✅ 测试成功！")
        print(f"响应: {content}")
        print(f"Token 使用: {usage}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行测试
    success = test_adapter()

    if success:
        print("\n" + "="*60)
        print("✅ Bedrock 适配器可用！")
        print("可以在 AgentAuditor 中使用")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 适配器测试失败")
        print("请检查 AWS 凭证配置")
        print("="*60)

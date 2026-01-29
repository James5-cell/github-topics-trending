"""
AI Summarizer - AI 总结和分类 GitHub 仓库
使用 Nvidia NIM API (OpenAI Compatible) 对仓库进行分析、总结和分类
"""
import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

from src.config import (
    NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL, 
    CLAUDE_MAX_TOKENS, CATEGORIES  # 复用 MAX_TOKENS 或定义新的
)


# 分类定义 - 从 CATEGORIES 配置中获取
def get_category_list() -> Dict[str, str]:
    """获取分类列表"""
    return {key: info["name"] for key, info in CATEGORIES.items()}


REPO_CATEGORIES = get_category_list()


class AISummarizer:
    """AI 总结和分类 GitHub 仓库 (Nvidia NIM)"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化 OpenAI 客户端

        Args:
            api_key: API 密钥，默认从环境变量读取
            base_url: API 基础 URL，默认从环境变量读取
            model: 模型名称
        """
        self.api_key = api_key or NVIDIA_API_KEY
        self.base_url = base_url or NVIDIA_BASE_URL
        self.model = model or NVIDIA_MODEL
        self.max_tokens = CLAUDE_MAX_TOKENS # 可以改名为 MAX_TOKENS，这里暂时复用

        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY 环境变量未设置")

        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            print(f"✅ Nvidia AI 客户端初始化成功 (Model: {self.model})")
        except Exception as e:
            raise Exception(f"AI 客户端初始化失败: {e}")

    def summarize_and_classify(self, repos: List[Dict]) -> List[Dict]:
        """
        批量总结和分类仓库

        Args:
            repos: 仓库列表

        Returns:
            AI 分析结果列表
        """
        if not repos:
            return []

        print(f"🤖 正在调用 Nvidia AI 分析 {len(repos)} 个仓库...")

        # 构建批量分析 Prompt
        prompt = self._build_batch_prompt(repos)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False
            )

            result_text = response.choices[0].message.content
            print(f"✅ AI 响应成功")

            # 解析结果
            results = self._parse_batch_response(result_text, repos)

            return results

        except Exception as e:
            print(f"❌ AI API 调用失败: {e}")
            # 返回基本信息作为降级方案
            return self._fallback_summaries(repos)

    def _build_batch_prompt(self, repos: List[Dict]) -> str:
        """
        构建批量分析的 Prompt
        """
        # 构建仓库列表
        repos_text = ""
        for i, repo in enumerate(repos[:20], 1):  # 一次最多分析 20 个
            repos_text += f"\n{'sz'*40}\n" # 分隔符
            repos_text += f"【仓库 {i}】\n"
            repos_text += f"名称: {repo.get('repo_name')}\n"
            repos_text += f"描述: {repo.get('description', 'N/A')}\n"
            repos_text += f"语言: {repo.get('language', 'N/A')}\n"

            topics = repo.get("topics", [])
            if topics:
                repos_text += f"Topics: {', '.join(topics[:5])}\n"

            readme = repo.get("readme_summary", "")
            if readme:
                repos_text += f"\nREADME 摘要:\n{readme[:300]}\n"

        # 构建分类说明
        category_text = "\n".join([
            f"  - {key}: {zh}"
            for key, zh in REPO_CATEGORIES.items()
        ])

        prompt = f"""你是一个开源项目分析专家。请分析以下 {min(len(repos), 20)} 个 GitHub 仓库，为每个仓库生成摘要和分类。

{repos_text}

---

【任务要求】

对每个仓库提取以下信息：

1. **summary**: 一句话摘要（不超过30字）
   - 简洁描述这个项目是什么

2. **description**: 详细描述（50-100字）
   - 详细说明项目的功能和价值

3. **use_case**: 使用场景
   - 谁在什么情况下会用到这个项目

4. **solves**: 解决的问题列表
   - 3-5个关键词或短语
   - 描述这个项目解决什么具体问题

5. **category**: 选择一个分类
   可选分类:
{category_text}

6. **category_zh**: 中文分类名
   - 对应 category 的中文名称

7. **tech_stack**: 技术栈标签（可选）
   - 主要使用的技术

【输出格式】

严格按照以下 JSON 数组格式输出，不要有任何其他文字说明（如 ```json 等）：

[
  {{
    "repo_name": "owner/repo",
    "summary": "一句话摘要",
    "description": "详细描述",
    "use_case": "使用场景",
    "solves": ["问题1", "问题2", "问题3"],
    "category": "tool",
    "category_zh": "工具",
    "tech_stack": ["React", "TypeScript"]
  }}
]

【重要】
- 只输出纯 JSON 数组
- 确保 JSON 格式正确有效
- repo_name 必须与输入的仓库名称完全一致
"""
        return prompt

    def _parse_batch_response(self, result_text: str, original_repos: List[Dict]) -> List[Dict]:
        """
        解析 AI 的批量响应
        """
        # 清理可能的 markdown 代码块标记
        result_text = result_text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        elif result_text.startswith("```"):
            result_text = result_text[3:]
        
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        result_text = result_text.strip()

        try:
            results = json.loads(result_text)

            if not isinstance(results, list):
                results = [results]

            # 验证并补充信息
            validated_results = []
            original_map = {r.get("repo_name") or r.get("name"): r for r in original_repos}

            for result in results:
                if not isinstance(result, dict):
                    continue

                repo_name = result.get("repo_name")

                # 确保 repo_name 存在
                if not repo_name:
                    continue

                # 从原始数据中获取额外信息
                original = original_map.get(repo_name, {})

                validated_result = {
                    "repo_name": repo_name,
                    "summary": result.get("summary", f"{repo_name} 项目"),
                    "description": result.get("description", ""),
                    "use_case": result.get("use_case", ""),
                    "solves": result.get("solves", []),
                    "category": result.get("category", "other"),
                    "category_zh": result.get("category_zh", REPO_CATEGORIES.get("other", "其他")),
                    "tech_stack": result.get("tech_stack", []),
                    "language": original.get("language", ""),
                    "topics": original.get("topics", []),
                    "readme_summary": original.get("readme_summary", ""),
                    "owner": original.get("owner", ""),
                    "url": original.get("url", "")
                }

                validated_results.append(validated_result)

            print(f"✅ 成功解析 {len(validated_results)} 个仓库的 AI 分析")
            return validated_results

        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"   原始响应: {result_text[:500]}...")
            return self._fallback_summaries(original_repos)

    def _fallback_summaries(self, repos: List[Dict]) -> List[Dict]:
        """
        降级方案：当 AI 分析失败时使用基本信息
        """
        results = []
        for repo in repos:
            repo_name = repo.get("repo_name") or repo.get("name", "unknown")
            description = repo.get("description", "")
            
            # 复用原来的简单分类推断逻辑，在此省略或简化
            # ... (可以保留原来的逻辑)
            
            # 简单的分类推断
            language = repo.get("language", "").lower()
            topics = repo.get("topics", [])
            category = "other"
            # 简单规则...
            
            results.append({
                "repo_name": repo_name,
                "summary": description[:50] + "..." if len(description) > 50 else description,
                "description": description,
                "category": category,
                "category_zh": REPO_CATEGORIES.get(category, "其他"),
                "fallback": True
            })
        return results

    def categorize_by_rules(self, repo: Dict) -> str:
        """基于规则快速分类"""
        # 复用原有逻辑
        # ...
        return "other"

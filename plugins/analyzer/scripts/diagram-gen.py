#!/usr/bin/env python3
"""diagram-gen - AI 架构图图像生成器
根据手绘草图调用 OpenAI API 生成专业架构图 (PNG)"""

import os, sys, base64, argparse, requests
from datetime import datetime

CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "openai_base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
}

PROMPTS = {
    "architecture": """你是一位专业的技术插画师。请根据上传的手绘草图，生成一张专业的系统架构图。

风格要求:
- 现代、简洁、专业的技术插图风格
- 使用清晰的图标和标签
- 颜色搭配和谐，对比度适中
- 类似 AWS/Azure 架构图的视觉风格

输出要求:
- 横向布局 (16:9 或 3:2)
- 白色或浅色背景
- 清晰的组件框和箭头
- 标注关键组件名称和数据流向""",

    "dataflow": """你是一位数据可视化专家。请根据手绘草图，生成一张专业的数据流向图。

风格要求:
- 使用不同颜色区分数据源、处理节点、存储
- 清晰的箭头指示数据流向
- 类似 Sankey 图的视觉效果
- 专业、简洁""",

    "deployment": """你是一位 DevOps 技术插画师。请根据手绘草图，生成一张专业的部署拓扑图。

风格要求:
- 使用 subgraph 或边框区分不同网络区域
- 清晰的服务器、数据库、负载均衡器图标
- 类似云厂商官方架构图的风格
- 专业、现代""",
}


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def call_gpt4o_image(prompt, image_b64):
    """GPT-4o 图生图：先试 responses API，失败降级 chat + tool"""
    r = requests.post(
        f"{CONFIG['openai_base_url']}/responses",
        headers={"Authorization": f"Bearer {CONFIG['openai_api_key']}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-2024-11-20",
            "input": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"},
            ]}],
            "tools": [{"type": "image_generation"}],
            "output": {"type": "image", "format": "png"},
        },
    )
    if r.ok:
        try:
            url = r.json().get("output", {}).get("content", [{}])[0].get("image_url")
            if url:
                return url
        except (KeyError, IndexError, TypeError):
            pass

    # 降级：chat + tool
    r2 = requests.post(
        f"{CONFIG['openai_base_url']}/chat/completions",
        headers={"Authorization": f"Bearer {CONFIG['openai_api_key']}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-2024-11-20",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt + "\n\n请分析草图并调用 image_generation 工具生成架构图。"},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"},
            ]}],
            "tools": [{"type": "image_generation"}],
            "tool_choice": "auto",
        },
    )
    if r2.ok:
        try:
            for tc in r2.json()["choices"][0]["message"].get("tool_calls", []):
                if tc.get("type") == "image_generation":
                    return tc["image_generation"]["image_url"]
        except (KeyError, IndexError, TypeError):
            pass
    return None


def call_dalle3(prompt, size):
    """DALL-E 3 纯文字生成"""
    r = requests.post(
        f"{CONFIG['openai_base_url']}/images/generations",
        headers={"Authorization": f"Bearer {CONFIG['openai_api_key']}", "Content-Type": "application/json"},
        json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": size, "response_format": "url"},
    )
    if r.ok:
        return r.json()["data"][0]["url"]
    print(f"API 错误: {r.status_code} {r.text}")
    return None


def main():
    ap = argparse.ArgumentParser(description="AI 架构图图像生成器")
    ap.add_argument("image", nargs="?", help="手绘草图路径")
    ap.add_argument("--type", choices=["architecture", "dataflow", "deployment"], default="architecture")
    ap.add_argument("--model", choices=["gpt-4o-image", "dall-e-3"], default="gpt-4o-image")
    ap.add_argument("--output")
    ap.add_argument("--prompt", default="")
    ap.add_argument("--size", default="1024x1024", choices=["1024x1024", "1792x1024", "1024x1792"])
    ap.add_argument("--reference", dest="reference")
    args = ap.parse_args()

    img = args.reference or args.image
    if not img:
        print("错误：请提供图片路径"); sys.exit(1)
    if not os.path.exists(img):
        print(f"错误：文件不存在：{img}"); sys.exit(1)
    if not CONFIG["openai_api_key"]:
        print("错误：需要 OPENAI_API_KEY"); sys.exit(1)

    out = args.output or f"./diagram-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    prompt = PROMPTS[args.type]
    if args.prompt:
        prompt += f"\n\n## 用户额外要求\n{args.prompt}"

    print(f"类型={args.type} 模型={args.model} 输入={img}")

    if args.model == "dall-e-3":
        url = call_dalle3(prompt, args.size)
    else:
        b64 = encode_image(img)
        url = call_gpt4o_image(prompt, b64)

    if not url:
        print("错误：未能生成图片"); sys.exit(1)

    print(f"下载: {url}")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(out, "wb") as f:
        for c in r.iter_content(8192): f.write(c)
    print(f"已保存: {out}")


if __name__ == "__main__":
    main()

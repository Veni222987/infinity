---
name: diagram
description: 根据手绘草图调用 AI 图像生成 API，生成专业系统架构图 (PNG)
argument-hint: [--type=architecture|dataflow|deployment] [--model=gpt-4o-image|dall-e-3] [--output=<path>] [--reference=<image-path>] [--prompt="<text>"] [--size=<size>]
allowed-tools: Bash, Write, Read
---

# /diagram — AI 架构图图像生成器

根据手绘草图或文字描述，调用 **OpenAI GPT-4o / DALL-E 3** 生成专业的**视觉架构图**（PNG 图片）。

## 输入

`$ARGUMENTS` 支持以下参数：

- `--type=<type>`: 图表类型
  - `architecture`（默认）: 系统架构图
  - `dataflow`: 数据流向图
  - `deployment`: 部署拓扑图

- `--model=<model>`: 模型名称
  - `gpt-4o-image`（默认）: GPT-4o 图生图（支持参考图）
  - `dall-e-3`: DALL-E 3 纯文字生成

- `--reference=<path>`: 参考图路径（手绘草图）
- `--output=<path>`: 输出图片路径（可选，默认当前目录）
- `--prompt="<text>"`: 额外文字描述
- `--size=<size>`: 图片尺寸（DALL-E 3 模式）
  - `1024x1024`（默认）
  - `1792x1024`（横向）
  - `1024x1792`（纵向）

## 环境变量

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
```

## 调用脚本

```bash
./plugins/analyzer/scripts/diagram-gen.py --reference=~/Desktop/sketch.png
```

## Prompt 模板

### architecture
```
你是一位专业的技术插画师。请根据上传的手绘草图，生成一张专业的系统架构图。

风格要求:
- 现代、简洁、专业的技术插图风格
- 使用清晰的图标和标签
- 颜色搭配和谐，对比度适中
- 类似 AWS/Azure 架构图的视觉风格

输出要求:
- 横向布局 (16:9 或 3:2)
- 白色或浅色背景
- 清晰的组件框和箭头
- 标注关键组件名称和数据流向
```

### dataflow
```
你是一位数据可视化专家。请根据手绘草图，生成一张专业的数据流向图。

风格要求:
- 使用不同颜色区分数据源、处理节点、存储
- 清晰的箭头指示数据流向
- 类似 Sankey 图的视觉效果
- 专业、简洁
```

### deployment
```
你是一位 DevOps 技术插画师。请根据手绘草图，生成一张专业的部署拓扑图。

风格要求:
- 使用 subgraph 或边框区分不同网络区域
- 清晰的服务器、数据库、负载均衡器图标
- 类似云厂商官方架构图的风格
- 专业、现代
```

## 示例用法

```bash
# 基础用法
/diagram --reference=~/Desktop/sketch.png

# 指定类型
/diagram --type=dataflow --reference=./flow.jpg

# DALL-E 3 纯文字生成
/diagram --model=dall-e-3 --prompt="生成一个微服务电商系统架构图"

# 添加额外描述
/diagram --reference=./sketch.png --prompt="请突出显示认证模块和数据库交互，使用蓝色系配色"
```

## 边界

- 图片大小限制：Base64 编码后不超 API 限制
- 仅支持 PNG 格式输出
- 不修改原始参考图
- 不上传图像到第三方（除配置的 OpenAI API）
- 完成后仅回复一行：输出路径 + 简短总结。

---
description: 分析 Git 仓库或服务的架构，按类型套用不同模板，输出带架构图的精美 HTML 报告
argument-hint: [target] [--template=repo-code|service-runtime|frontend-app|library-sdk|infra-compose]
allowed-tools: Bash, Read, Glob, Grep, Write, WebFetch, WebSearch
---

# /analyze — 架构分析与可视化

你是一位资深软件架构师。本命令分析一个 **Git 仓库** 或 **服务**，识别结构、模块、依赖与数据流，并生成一份**美观、简洁、可独立打开**的 HTML 报告（含架构图）。

报告会**按目标类型套用不同模板**，每种模板的章节、架构图侧重点、主色都不同。

## 输入

`$ARGUMENTS` 形如：`<target> [--template=<name>]`

- `target`：本地目录路径、远程 Git URL、服务名/描述；为空则分析当前工作目录
- `--template=<name>`：可选，强制使用某个模板；缺省时自动判定

支持的模板：`repo-code` · `service-runtime` · `frontend-app` · `library-sdk` · `infra-compose`

## 工作流

### 1. 定位与采样
- 若是 URL：`git clone --depth=50 <url> "$TMPDIR/analyzer-<slug>"`
- 若是本地路径：`Bash` 验证存在性
- 收集元数据（仓库内）：
  - `git log -1 --format='%h %an %ad %s' --date=short`
  - `git rev-list --count HEAD`
  - `git shortlog -sne | head -10`
  - `git ls-files | head -200`、`git ls-files | wc -l`
- 探测特征文件（用于模板判定 + 内容采集）：
  - 语言/构建：`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml`、`build.gradle*`、`Makefile`
  - 容器/编排：`Dockerfile*`、`docker-compose*.y*ml`、`k8s/**`、`helm/**`、`*.tf`
  - 入口/路由：`src/**/main.*`、`cmd/**`、`app/**`、`server/**`、`routes/**`、`controllers/**`、`pages/**`
  - 配置/文档：`.env*`、`config/**`、`README*`、`docs/**`、`ARCHITECTURE*`

### 2. 选择模板

如果用户传了 `--template=<name>`，**直接使用**；否则按以下顺序自动判定（命中即停）：

1. 仅有 `docker-compose*` / `terraform` / `helm` / `k8s/**` 且无明显应用代码 → **`infra-compose`**
2. `package.json` 的 `dependencies` 含 `react` / `vue` / `next` / `nuxt` / `vite` / `svelte` / `solid` → **`frontend-app`**
3. 同时具备 `Dockerfile` 与（`k8s/**` 或 `helm/**` 或 `cmd/server` 类入口） → **`service-runtime`**
4. 包元数据声明了导出/可执行入口（`package.json#exports`、`pyproject` 的 `[project.scripts]`、`Cargo.toml [lib]`、`go.mod` 但无 server 入口） → **`library-sdk`**
5. 兜底 → **`repo-code`**

判定结果会写入报告页脚：`模板：<name>（自动判定 | 用户指定）`。

### 3. 识别架构（共通）
- **运行时形态**：单体 / 微服务 / 库 / CLI / 前端 / 全栈 / 基建
- **核心模块**（按目录、包、入口划分）
- **外部依赖**（DB、MQ、Cache、第三方 API）—— 来自配置、依赖清单、`docker-compose`
- **数据流与调用关系**：HTTP / RPC / 队列 / 文件
- **关键风险或亮点**：循环依赖、过大模块、缺测试、安全配置等

> ⚠️ 不要臆造。每个结论都应能指向具体文件或命令输出；不确定时明确标注「推测」。

### 4. 模板差异

每个模板规定了**章节、图表类型、主色、概览 stat 卡**。其余规则（单文件、CDN 加载 Mermaid、深浅模式、移动端友好）共通。

**主架构图统一使用 GPT Image 生成 PNG 视觉图**（见第 5 节），后续流程图/数据流图等使用 Mermaid。

#### 模板 A · `repo-code`（仓库 / 单体）
- **主色**：`#6366f1`（深色 `#818cf8`）
- **架构图**：GPT Image → PNG（模块依赖 + 外部系统）
- **Mermaid**：`flowchart LR`，数据流/调用链（后续补充图）
- **stat 卡**：主要语言、形态、提交数、最近提交
- **章节**：概览 → 架构图 → 模块清单 → 外部依赖 → 数据流 → 观察与建议 → 附录

#### 模板 B · `service-runtime`（运行中的服务）
- **主色**：`#10b981`（深色 `#34d399`）
- **架构图**：GPT Image → PNG（部署拓扑）
- **Mermaid**：`flowchart TD`，中间件链/请求链路（后续补充图）
- **stat 卡**：副本数、端口、镜像、最近发布
- **章节**：概览 → 部署拓扑 → API / 入口表（路径·方法·处理器） → 中间件链 → 外部依赖与配置项 → 健康检查 / 可观测性 → SLO 与风险 → 附录

#### 模板 C · `frontend-app`（前端 / 全栈 web）
- **主色**：`#f43f5e`（深色 `#fb7185`）
- **架构图**：GPT Image → PNG（前端架构 + 数据层）
- **Mermaid**：`flowchart TD`，路由树（后续补充图）
- **stat 卡**：框架版本、路由数、页面数、构建工具
- **章节**：概览 → 路由 & 页面树 → 组件分层图 → 状态管理 → 数据获取层（API / SSR / RSC） → 构建与产物 → 性能 / 可访问性观察 → 附录

#### 模板 D · `library-sdk`（库 / CLI / SDK）
- **主色**：`#0ea5e9`（深色 `#38bdf8`）
- **架构图**：GPT Image → PNG（公共 API → 内部实现 → 外部依赖）
- **Mermaid**：`flowchart LR`，调用链路（后续补充图）
- **stat 卡**：包名、版本、导出数、运行时
- **章节**：概览 → 公共 API 表面（导出符号表） → 内部分层 → 依赖与对等依赖 → 使用示例（从 README 提取） → 兼容性矩阵 → 附录

#### 模板 E · `infra-compose`（基础设施 / 编排）
- **主色**：`#f59e0b`（深色 `#fbbf24`）
- **架构图**：GPT Image → PNG（服务拓扑 + 网络分组）
- **Mermaid**：`flowchart LR`，流量路径（后续补充图）
- **stat 卡**：服务数、网络数、卷数、编排工具
- **章节**：概览 → 拓扑图 → 服务清单（镜像·端口·依赖） → 网络与卷 → 密钥与配置 → 部署流程 → 风险 → 附录

### 5. 生成主架构图（GPT Image）

主架构图通过 OpenAI GPT-4o Image Generation API 生成，以 PNG 格式嵌入 HTML（Base64 data URI）。

**Prompt 模板（按模板类型替换）：**

#### repo-code
```
你是一位专业的技术插画师。请根据以下信息生成一张系统架构图。

项目信息：
- 名称：{{PROJECT}}
- 语言：{{LANGUAGE}}
- 模块：{{MODULES}}
- 外部依赖：{{EXTERNAL_DEPS}}

风格要求：
- 现代、简洁、专业的技术插图风格
- 类似 AWS/Azure 架构图的视觉风格
- 白色或浅色背景，横向布局（16:9）
- 清晰的组件框和箭头
- 外部系统用虚线或不同颜色标识
```

#### service-runtime
```
你是一位 DevOps 技术插画师。请根据以下信息生成一张部署拓扑图。

项目信息：
- 名称：{{PROJECT}}
- 服务：{{SERVICES}}
- 外部依赖：{{EXTERNAL_DEPS}}
- 端口/协议：{{PORTS}}

风格要求：
- 类似云厂商官方架构图
- 使用 subgraph 区分不同网络区域
- 标注关键端口和服务
- 横向布局（16:9）
```

#### frontend-app
```
你是一位前端架构插画师。请根据以下信息生成一张前端架构图。

项目信息：
- 名称：{{PROJECT}}
- 框架：{{FRAMEWORK}}
- 页面/路由：{{ROUTES}}
- 数据层：{{DATA_LAYER}}

风格要求：
- 现代前端架构图风格
- 区分 UI 层、状态管理层、数据层
- 横向布局（16:9）
```

#### library-sdk
```
你是一位技术插画师。请根据以下信息生成一张库/SDK 架构图。

项目信息：
- 名称：{{PROJECT}}
- 公共 API：{{PUBLIC_API}}
- 内部模块：{{INTERNAL}}
- 外部依赖：{{EXTERNAL_DEPS}}

风格要求：
- 清晰的分层展示：公共 API → 内部实现 → 外部依赖
- 横向布局（16:9）
```

#### infra-compose
```
你是一位基础设施插画师。请根据以下信息生成一张基础设施拓扑图。

项目信息：
- 名称：{{PROJECT}}
- 服务：{{SERVICES}}
- 网络：{{NETWORKS}}
- 存储：{{VOLUMES}}

风格要求：
- 类似 Docker/K8s 官方架构图
- 使用边框区分不同网络区域
- 横向布局（16:9）
```

**调用 API：**
```bash
# 使用 GPT-4o Image Generation
curl -s -X POST "$OPENAI_BASE_URL/responses" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-2024-11-20",
    "input": [{"role": "user", "content": [{"type": "text", "text": "<prompt>"}]}],
    "tools": [{"type": "image_generation"}],
    "output": {"type": "image", "format": "png"}
  }'
```

**降级方案（无 API Key 时）：**
使用 Mermaid `flowchart` 作为架构图替代，节点样式保持简洁。

### 6. 生成 Mermaid 补充图

后续流程图/数据流图等使用 Mermaid，共通规则：
- 节点 ≤ 15 个，必要时聚合 `subgraph`
- 区分外部系统（虚线 / 不同样式）与内部模块
- 标注关键边的协议（HTTP / gRPC / SQL / Kafka 等）

### 7. 输出 HTML 报告

**模板来源**：从 `templates/` 目录加载对应模板的 HTML 文件，填充数据后输出。

```
templates/
├── repo-code.html          # 仓库 / 单体架构
├── service-runtime.html    # 运行中的服务 / 微服务
├── frontend-app.html       # 前端 / 全栈 web
├── library-sdk.html        # 库 / CLI / SDK
└── infra-compose.html      # 基础设施 / Docker Compose
```

每个模板文件已预置精致卡片风样式，包含：
- Hero + 模板角标
- 4 张概览 stat 卡片
- 总架构图占位（`<img class="arch-image">`，运行时替换为 GPT Image 生成的 PNG Base64）
- 2+ 张 Mermaid 补充图容器
- 表格/列表章节
- 深色模式、响应式布局、悬停动效

**运行时操作：**
1. `Read` 对应模板文件作为 HTML 骨架
2. 替换占位符：`{{PROJECT}}`、`{{ONE_LINER}}`、`{{ACCENT}}`、`{{GENERATED_AT}}` 等
3. 注入实际数据（stat 值、表格行、Mermaid 代码）
4. 若 GPT Image 生成成功，替换 `<img class="arch-image" src="...">` 为 Base64 数据
5. 写到：`./infinity-analyzer-<repo-slug>-<template>-<YYYYMMDD-HHMM>.html`

**降级方案**：若 `templates/` 目录不存在或文件缺失，回退到内嵌 HTML 模板生成（第 8 节）。

### 8. 内嵌 HTML 模板（降级备用）

当 `templates/` 不可用时，使用以下内嵌模板生成报告。

```html
<!doctype html>
<html lang="zh-CN" data-theme="auto">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{{PROJECT}} · 架构分析（{{TEMPLATE}}）</title>
<style>
  :root { --bg:#fff; --fg:#0f172a; --muted:#64748b; --line:#e2e8f0; --accent:{{ACCENT}}; --card:#f8fafc; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#0b1020; --fg:#e2e8f0; --muted:#94a3b8; --line:#1e293b; --accent:{{ACCENT_DARK}}; --card:#111827; }
  }
  * { box-sizing: border-box; }
  html,body { margin:0; padding:0; background:var(--bg); color:var(--fg);
    font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; }
  .wrap { max-width: 960px; margin: 0 auto; padding: 48px 24px 96px; }
  .hero { padding: 32px; border-radius: 16px; background: var(--card); border:1px solid var(--line); margin-bottom: 40px; position:relative; }
  .hero h1 { margin:0 0 8px; font-size: 28px; letter-spacing:-0.01em; }
  .hero p { margin:0; color: var(--muted); }
  .badge { position:absolute; top:20px; right:20px; padding:4px 10px; border-radius:999px;
    background:var(--accent); color:#fff; font-size:12px; letter-spacing:0.04em; text-transform:uppercase; }
  h2 { margin: 48px 0 12px; font-size: 20px; letter-spacing:-0.01em; }
  h2::before { content:""; display:inline-block; width:4px; height:18px; background:var(--accent);
    border-radius:2px; margin-right:10px; vertical-align:-3px; }
  table { width:100%; border-collapse: collapse; font-size: 14px; }
  th,td { padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
  th { color:var(--muted); font-weight:600; }
  code, .mono { font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    background: var(--card); padding:1px 6px; border-radius:4px; }
  .grid { display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); }
  .stat { padding:14px; border:1px solid var(--line); border-radius:10px; background:var(--card); }
  .stat .k { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:0.04em; }
  .stat .v { font-size:18px; margin-top:4px; }
  .diagram { padding:16px; border:1px solid var(--line); border-radius:12px; background:var(--card); overflow:auto; }
  .arch-image { max-width:100%; border-radius:12px; border:1px solid var(--line); }
  ul.tight { padding-left: 20px; } ul.tight li { margin: 4px 0; }
  footer { margin-top:64px; color:var(--muted); font-size:12px; }
  a { color: var(--accent); }
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad:true, theme:'default', securityLevel:'loose' });</script>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <span class="badge">{{TEMPLATE}}</span>
    <h1>{{PROJECT}}</h1>
    <p>{{ONE_LINER}}</p>
  </div>

  {{SECTIONS}}

  <footer>
    生成于 {{GENERATED_AT}} · 模板：<code>{{TEMPLATE}}</code>（{{TEMPLATE_SOURCE}}）·
    由 <code>infinity / analyzer</code> 输出 · 数据来源：<code>git</code>、文件抽样、依赖清单
  </footer>
</div>
</body>
</html>
```

每个模板对 `{{ACCENT}}` / `{{ACCENT_DARK}}` 的取值：

| 模板 | `--accent`（浅色） | `--accent`（深色） |
|---|---|---|
| `repo-code` | `#6366f1` | `#818cf8` |
| `service-runtime` | `#10b981` | `#34d399` |
| `frontend-app` | `#f43f5e` | `#fb7185` |
| `library-sdk` | `#0ea5e9` | `#38bdf8` |
| `infra-compose` | `#f59e0b` | `#fbbf24` |

`{{SECTIONS}}` 按所选模板的章节顺序拼接以下片段。

**概览（stat 网格，4 张卡按模板填）**
```html
<h2>概览</h2>
<div class="grid">
  <div class="stat"><div class="k">{{K1}}</div><div class="v">{{V1}}</div></div>
  <div class="stat"><div class="k">{{K2}}</div><div class="v">{{V2}}</div></div>
  <div class="stat"><div class="k">{{K3}}</div><div class="v">{{V3}}</div></div>
  <div class="stat"><div class="k">{{K4}}</div><div class="v mono">{{V4}}</div></div>
</div>
```

**主架构图**（GPT Image PNG，Base64 嵌入）
```html
<h2>{{DIAGRAM_TITLE}}</h2>
<div class="diagram">
  <img class="arch-image" src="data:image/png;base64,{{ARCH_IMAGE_B64}}" alt="{{DIAGRAM_TITLE}}" />
</div>
```

**Mermaid 补充图**（流程图/数据流图等）
```html
<h2>{{MERMAID_TITLE}}</h2>
<div class="diagram"><pre class="mermaid">
{{MERMAID}}
</pre></div>
```

**通用表格章节**（模块清单 / API 入口 / 服务清单 / 导出符号 等）
```html
<h2>{{TABLE_TITLE}}</h2>
<table><thead><tr>{{TH}}</tr></thead><tbody>{{ROWS}}</tbody></table>
```

**要点列表章节**（数据流 / 观察建议 / 中间件链 / 可观测性 等）
```html
<h2>{{LIST_TITLE}}</h2>
<ul class="tight">{{ITEMS}}</ul>
```

## 边界

- 不修改被分析仓库内的任何文件。
- 报告默认写到**用户当前工作目录**，不要写进被分析仓库。
- 若仓库过大（`git ls-files | wc -l > 5000`），按目录粒度抽样，避免读取全部文件。
- 不上传任何代码片段到第三方。
- 自动判定结果不确定时（多重特征命中），优先级见「2. 选择模板」；并在页脚注明 `自动判定`，方便用户用 `--template=` 覆盖重跑。
- GPT Image 生成失败时降级为 Mermaid 架构图，并在页脚标注 `架构图：Mermaid（Image 不可用）`。

# infinity

Claude Code 插件市场。

## 安装

在 Claude Code 中：

```
/plugin marketplace add Veni222987/infinity
/plugin install analyzer@infinity
```

## 插件

| 名称 | 说明 |
| --- | --- |
| [analyzer](./plugins/analyzer) | 分析 Git 仓库或服务的架构，输出带架构图的精美 HTML 报告。命令：`/analyze [路径\|URL\|服务名]` |

## 目录结构

```
.
├── .claude-plugin/
│   └── marketplace.json     # 插件市场发现文件
└── plugins/
    └── analyzer/
        ├── .claude-plugin/
        │   └── plugin.json
        └── commands/
            └── analyze.md
```

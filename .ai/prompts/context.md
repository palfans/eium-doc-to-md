# Project Context 项目上下文

## Project Information 项目信息

**项目名称**: eIUM Documentation to Markdown Converter

**项目描述**: 将 eIUM HTML 文档转换为 GitHub Flavored Markdown (GFM) 的 Python 工具，基于 Pandoc 与自定义 Lua 过滤器，并进行表格、代码块与空白规范化处理。

**仓库地址**: https://github.com/palfans/eium-doc-to-md

## Technology Stack 技术栈

**主要语言**: Python

**框架/库**:
- Pandoc (HTML→GFM 转换引擎)
- Lua 过滤器 (Pandoc Lua filter)

**开发工具**:
- uv (包管理与虚拟环境)
- ruff (格式化与检查)

## Project Structure 项目结构

```
eium-doc-to-md/
├── src/
│   ├── convert_manuals.py    # 主转换脚本
│   └── html_to_md.lua        # Pandoc Lua 过滤器
├── scripts/
│   └── html_to_md.lua        # 过滤器默认路径（PANDOC_BASE_CMD 使用）
├── main.py                   # 入口点
├── pyproject.toml            # 项目配置
└── README.md                 # 使用说明
```

## Development Guidelines 开发指南

### Coding Standards 编码规范

- 编写或改动代码时，必须遵循 `zc-workflow-core` 和其他的相关 skills
- 使用 ruff 进行代码格式化与检查

### Testing Requirements 测试要求

- README 未定义测试要求；如新增测试需补充本节

## Special Constraints 特殊约束

- 需要 Python 3.12+
- 运行环境必须可用 pandoc
- 生成的临时文件都放在 `temp/` 目录中

## Current Focus 当前重点

如果输入为单文件，需要检查输出是目录还是文件。如果是文件，则直接使用；如果是目录，则在该目录中生成同名.md文件。
修改完成，review 整个 readme.md。并为它创建一个 readme_en.md的英文版。
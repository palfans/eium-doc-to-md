# eIUM Documentation to Markdown Converter

[English](README_EN.md)

将 eIUM HTML/PDF/DOCX 文档转换为 GitHub Flavored Markdown (GFM) 格式的 Python 工具，使用 Pandoc 和自定义 Lua 过滤器。

## 功能特性

- 🔄 **智能转换**: 将 HTML 转换为清晰、可读的 Markdown
- 📊 **表格格式化**: 自动重新格式化带粗体标签的摘要表格
- 💻 **代码块处理**: 将缩进代码块转换为围栏格式
- 🎨 **输出优化**: 删除多余空行，规范化空白字符
- 🔧 **自定义过滤**: 使用 Lua 过滤器处理高级 HTML 元素
- 🔗 **链接重写**: 自动将 `.html` 链接转换为 `.md`
- 📄 **PDF/Word 转换**: 使用 MarkItDown 支持 PDF/DOCX → Markdown
- ⏳ **进度显示**: 批量转换时显示 tqdm 进度条

## 依赖要求

- **Python**: 3.12 或更高版本
- **uv**: Python 包管理工具（推荐）
- **Pandoc**: HTML 到 Markdown 转换引擎
  ```bash
  # Ubuntu/Debian
  sudo apt-get install pandoc
  
  # macOS
  brew install pandoc
  ```
- **MarkItDown**: PDF/DOCX 转换（可选）
  ```bash
  uv add "markitdown[pdf,docx]"
  ```
- **tqdm**: 进度条显示
  ```bash
  uv add tqdm
  ```

## 安装步骤

1. 克隆仓库:
   ```bash
   git clone https://github.com/palfans/eium-doc-to-md.git
   cd eium-doc-to-md
   ```

2. 使用 uv 创建虚拟环境并安装依赖:
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv sync --extra dev
   ```

## 使用方法

### CLI 入口

#### 单文件转换（HTML/PDF/DOCX）

```bash
python src/convert_manuals.py -i input/example.pdf -o output/example.md
python src/convert_manuals.py -i input/example.docx -o output/example.md
python src/convert_manuals.py -i input/example.html -o output/example.md
```

`-i` 为必填。
若不指定 `-o`，默认输出为同目录 `.md` 文件。
若 `-o` 指向目录，则在该目录生成同名 `.md` 文件。

#### 目录批量转换

```bash
python src/convert_manuals.py -i input_dir -o output_dir
```

目录模式下 `-o` 必填。递归处理目录内的 `.html`、`.pdf`、`.docx` 文件，并保持目录结构输出为 `.md`。

### 包装脚本

```bash
./bin/eium-convert -i input/example.pdf -o output/example.md
./bin/eium-convert -i input_dir -o output_dir
```

### 编程使用

在 Python 代码中使用转换功能:

```python
from pathlib import Path
from src.convert_manuals import convert_document, convert_file

# 转换单个文件
convert_file(
    html_path=Path('input/example.html'),
    md_path=Path('output/example.md')
)

# 转换 PDF 或 DOCX
convert_document(
    input_path=Path('input/example.pdf'),
    md_path=Path('output/example.md')
)
```

### 自定义批量转换

```python
from pathlib import Path
from src.convert_manuals import convert_file

input_dir = Path('docs/html')
output_dir = Path('docs/markdown')

for html_file in input_dir.rglob('*.html'):
    rel_path = html_file.relative_to(input_dir)
    md_file = output_dir / rel_path.with_suffix('.md')
    convert_file(html_file, md_file)
```

## 工作原理

转换流程包括以下步骤:

1. **Pandoc 转换**: 使用 Pandoc 和自定义 Lua 过滤器将 HTML 转换为 GFM
2. **表格重新格式化**: 将带粗体标签的摘要表格重构为标准化的两列格式
3. **代码块转换**: 将缩进代码块（4个空格）转换为围栏代码块
4. **空白规范化**: 压缩多余的空行，删除尾随空格
5. **字符替换**: 将特殊字符和转义序列替换为 HTML 实体

PDF/DOCX 转换流程：
1. **MarkItDown**: 将 PDF/DOCX 转换为 Markdown
2. **Pandoc + Lua 过滤器**: 标准化输出为 GFM
3. **后处理**: 表格、代码块、空白与字符清理

## Lua 过滤器

包含的 `html_to_md.lua` 过滤器处理:

- **命令概要**: 将 `.cmdsynopsis` div 转换为代码块
- **链接**: 将 `.html` 扩展名重写为 `.md` 用于内部链接
- **代码块**: 删除代码块的属性以获得更清晰的输出
- **Span**: 展开 span 元素以简化结构
- **图像**: 过滤掉特定的背景图像

## 项目结构

```
eium-doc-to-md/
├── bin/
│   └── eium-convert            # 包装脚本
├── src/
│   ├── convert_manuals.py      # 主转换脚本
│   └── html_to_md.lua          # Pandoc Lua 过滤器
├── main.py                     # 入口点
├── pyproject.toml              # 项目配置
├── README.md                   # 中文说明
└── README_EN.md                # English README
```

## 配置

### Pandoc 选项

在 `src/convert_manuals.py` 中修改 `PANDOC_BASE_CMD`:

```python
PANDOC_BASE_CMD = [
    'pandoc',
    '--from=html',
    '--to=gfm',
    '--wrap=none',
    f'--lua-filter={FILTER}'
]
```

### Lua 过滤器路径

```python
FILTER = Path('src/html_to_md.lua')
```

## 代码质量

项目使用 ruff 进行代码格式化和检查:

```bash
# 检查代码质量
uv run ruff check .

# 格式化代码
uv run ruff format .
```

## 常见问题

### Pandoc 未找到

确保 Pandoc 已安装并在 PATH 中:
```bash
pandoc --version
```

### Lua 过滤器未找到

确保 Lua 过滤器文件存在于 `FILTER` 指定的路径。默认路径是 `src/html_to_md.lua`。

### 编码问题

脚本默认使用 UTF-8 编码。如果遇到编码错误，请确保输入 HTML 文件是 UTF-8 编码。

## 开发

### 安装开发依赖

```bash
uv sync --extra dev
```

### 运行代码检查

```bash
uv run ruff check src/
```

### 格式化代码

```bash
uv run ruff format src/
```

## 仓库

https://github.com/palfans/eium-doc-to-md

# eIUM Documentation to Markdown Converter

[中文说明](README.md)

A Python tool that converts eIUM documentation (HTML/PDF/DOCX) to GitHub Flavored Markdown (GFM) using Pandoc and custom Lua filters.

## Features

- 🔄 **Smart conversion**: Convert HTML to clean, readable Markdown
- 📊 **Table formatting**: Normalize summary tables with bold labels
- 💻 **Code block handling**: Convert indented blocks to fenced code blocks
- 🎨 **Output cleanup**: Remove extra blank lines and normalize whitespace
- 🔧 **Custom filtering**: Lua filters for advanced HTML elements
- 🔗 **Link rewriting**: Rewrite `.html` links to `.md`
- 📄 **PDF/Word conversion**: Use MarkItDown for PDF/DOCX → Markdown
- ⏳ **Progress display**: Show tqdm progress during batch conversion

## Requirements

- **Python**: 3.12+
- **uv**: Python package manager (recommended)
- **Pandoc**: HTML to Markdown converter
  ```bash
  # Ubuntu/Debian
  sudo apt-get install pandoc

  # macOS
  brew install pandoc
  ```
- **MarkItDown**: PDF/DOCX conversion (optional)
  ```bash
  uv add "markitdown[pdf,docx]"
  ```
- **tqdm**: Progress bar
  ```bash
  uv add tqdm
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/palfans/eium-doc-to-md.git
   cd eium-doc-to-md
   ```

2. Create a virtual environment and install dependencies with uv:
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv sync --extra dev
   ```

## Usage

### CLI

#### Single file (HTML/PDF/DOCX)

```bash
python src/convert_manuals.py -i input/example.pdf -o output/example.md
python src/convert_manuals.py -i input/example.docx -o output/example.md
python src/convert_manuals.py -i input/example.html -o output/example.md
```

`-i` is required. If `-o` is omitted, the output is written to the same directory with a `.md` suffix.
If `-o` points to a directory, a same-name `.md` file will be created there.

#### Batch directory conversion

```bash
python src/convert_manuals.py -i input_dir -o output_dir
```

`-o` is required for directory input. Recursively processes `.html`, `.pdf`, and `.docx` files while preserving the directory structure.

### Wrapper Script

```bash
./bin/eium-convert -i input/example.pdf -o output/example.md
./bin/eium-convert -i input_dir -o output_dir
```

### Programmatic Usage

```python
from pathlib import Path
from src.convert_manuals import convert_document, convert_file

# HTML
convert_file(
    html_path=Path('input/example.html'),
    md_path=Path('output/example.md')
)

# PDF or DOCX
convert_document(
    input_path=Path('input/example.pdf'),
    md_path=Path('output/example.md')
)
```

### Custom Batch Conversion

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

## How It Works

HTML conversion pipeline:
1. **Pandoc conversion**: HTML → GFM with Lua filters
2. **Table normalization**: Summary tables → two-column format
3. **Code block conversion**: Indented → fenced blocks
4. **Whitespace cleanup**: Collapse excessive blank lines
5. **Character replacement**: Escape special sequences

PDF/DOCX conversion pipeline:
1. **MarkItDown**: PDF/DOCX → Markdown
2. **Pandoc + Lua filters**: Normalize to GFM
3. **Post-processing**: Tables, code blocks, whitespace cleanup

## Lua Filter

The `html_to_md.lua` filter handles:
- **Command synopsis**: Convert `.cmdsynopsis` to code blocks
- **Links**: Rewrite `.html` to `.md` for internal links
- **Code blocks**: Strip attributes for clean output
- **Span**: Unwrap span elements
- **Images**: Filter specific background images

## Project Structure

```
eium-doc-to-md/
├── bin/
│   └── eium-convert            # Wrapper script
├── src/
│   ├── convert_manuals.py      # Main conversion script
│   └── html_to_md.lua          # Pandoc Lua filter
├── main.py                     # Entry point
├── pyproject.toml              # Project configuration
├── README.md                   # Chinese README
└── README_EN.md                # English README
```

## Configuration

### Pandoc options

```python
PANDOC_BASE_CMD = [
    'pandoc',
    '--from=html',
    '--to=gfm',
    '--wrap=none',
    f'--lua-filter={FILTER}'
]
```

### Lua filter path

```python
FILTER = Path('src/html_to_md.lua')
```

## Code Quality

```bash
uv run ruff check .
uv run ruff format .
```

## Troubleshooting

### Pandoc not found

Ensure Pandoc is installed and on PATH:
```bash
pandoc --version
```

### Lua filter not found

Ensure `src/html_to_md.lua` exists and the path matches `FILTER`.

### Encoding issues

The converter uses UTF-8 by default. Ensure input files are UTF-8 encoded.

## Repository

https://github.com/palfans/eium-doc-to-md

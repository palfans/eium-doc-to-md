#!/usr/bin/env python3
"""HTML to Markdown Converter for Documentation Manuals.

This module provides functionality to convert HTML documentation files to GitHub
Flavored Markdown (GFM) format using Pandoc with custom Lua filters. It handles
special formatting cases such as summary tables, indented code blocks, and HTML
entity replacements.

The conversion process includes:
    - Converting HTML files to GFM using Pandoc
    - Reformatting summary tables with bold labels
    - Converting indented code blocks to fenced code blocks
    - Collapsing excessive blank lines
    - Replacing escaped characters with HTML entities

Example:
    Run the conversion for all documentation files:
        $ python convert_manuals.py

    Or use the convert_file function programmatically:
        >>> from pathlib import Path
        >>> convert_file(Path('input.html'), Path('output.md'))
"""

import re
import subprocess
from pathlib import Path

FILTER = Path('scripts/html_to_md.lua')
PANDOC_BASE_CMD = ['pandoc', '--from=html', '--to=gfm', '--wrap=none', f'--lua-filter={FILTER}']

SUMMARY_ROW_RE = re.compile(r'^\*\*(.+?):\*\*\s*(.*)$')


def split_table_row(line: str) -> list[str]:
    """Parse a Markdown table row into individual cells.

    Splits a table row by pipe (|) delimiters while properly handling escaped
    pipes within cell content. The function tracks escape sequences to avoid
    splitting on pipes that are part of the cell content.

    Args:
        line: A string representing a single Markdown table row, typically
            starting with '|' and containing pipe-delimited cells.

    Returns:
        A list of strings, where each string is the trimmed content of a table
        cell. Empty cells are represented as empty strings.

    Example:
        >>> split_table_row('| **Name:** | John Doe | Age: 30 |')
        ['**Name:**', 'John Doe', 'Age: 30']
        >>> split_table_row('| Column with \\| pipe | Normal column |')
        ['Column with \\| pipe', 'Normal column']
    """
    cells: list[str] = []
    cell_chars: list[str] = []
    escape = False
    started = False
    for ch in line.rstrip('\n'):
        if not started:
            if ch == '|':
                started = True
            continue
        if ch == '|' and not escape:
            cells.append(''.join(cell_chars).strip())
            cell_chars = []
            continue
        if ch == '\\' and not escape:
            escape = True
            cell_chars.append(ch)
            continue
        if escape:
            escape = False
        cell_chars.append(ch)
    if cell_chars:
        cells.append(''.join(cell_chars).strip())
    return cells


def is_summary_table(table_lines: list[str]) -> bool:
    """Determine if a table contains summary information with bold labels.

    Checks if any row in the table matches the pattern of summary tables,
    which typically have bold labels followed by colons (e.g., "**Name:**").

    Args:
        table_lines: A list of strings, each representing a line from a
            Markdown table.

    Returns:
        True if the table contains at least one row matching the summary
        table pattern; False otherwise.

    Example:
        >>> lines = ['| **Author:** | Jane Smith |', '| **Date:** | 2024-01-01 |']
        >>> is_summary_table(lines)
        True
        >>> lines = ['| Column 1 | Column 2 |', '| Data 1 | Data 2 |']
        >>> is_summary_table(lines)
        False
    """
    for line in table_lines:
        if not line.strip():
            continue
        if '**' not in line:
            continue
        cells = split_table_row(line)
        if not cells:
            continue
        if SUMMARY_ROW_RE.match(cells[0] or ''):
            return True
    return False


def format_summary_table(table_lines: list[str]) -> list[str]:
    """Reformat a summary table into a standardized two-column format.

    Transforms summary tables with bold labels into a consistent format with
    'Field' and 'Details' columns. Combines multiple cells from the same row
    into a single details field.

    Args:
        table_lines: A list of strings representing the original table lines.

    Returns:
        A list of strings representing the reformatted table, including header
        and separator rows, followed by data rows in the format:
        | Field | Details |

    Example:
        >>> lines = ['| **Name:** John | **Age:** 30 |']
        >>> format_summary_table(lines)
        ['| Field | Details |', '| --- | --- |', '| Name | John', '| Age | 30']
    """
    formatted = ['| Field | Details |', '| --- | --- |']
    for line in table_lines:
        stripped = line.strip()
        if not stripped or set(stripped.replace('-', '')) <= {'|'}:
            continue
        cells = split_table_row(line)
        if not cells:
            continue
        first = cells[0]
        if not first:
            continue
        match = SUMMARY_ROW_RE.match(first)
        if not match:
            continue
        label = match.group(1).strip()
        details = match.group(2).strip()
        for extra in cells[1:]:
            if extra:
                details = f'{details} {extra.strip()}' if details else extra.strip()
        formatted.append(f'| {label} | {details} |')
    return formatted


def rewrite_summary_tables(lines: list[str]) -> list[str]:
    """Process all tables in the document and reformat summary tables.

    Scans through the document lines, identifies table blocks, and reformats
    those that match the summary table pattern while leaving other tables
    unchanged.

    Args:
        lines: A list of strings representing the entire document.

    Returns:
        A list of strings with summary tables reformatted and other content
        preserved.

    Note:
        Tables are identified by consecutive lines starting with '|'.
    """
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('|'):
            j = i
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            table_block = lines[i:j]
            if is_summary_table(table_block):
                result.extend(format_summary_table(table_block))
            else:
                result.extend(table_block)
            i = j
        else:
            result.append(line)
            i += 1
    return result


def collapse_blank_lines(lines: list[str]) -> list[str]:
    """Reduce excessive consecutive blank lines to a maximum of two.

    Compresses multiple consecutive blank lines while preserving meaningful
    whitespace structure. Also trims trailing whitespace from non-empty lines.

    Args:
        lines: A list of strings representing document lines.

    Returns:
        A list of strings with excessive blank lines removed and trailing
        whitespace trimmed from non-empty lines.

    Example:
        >>> lines = ['Line 1', '', '', '', 'Line 2']
        >>> collapse_blank_lines(lines)
        ['Line 1', '', '', 'Line 2']
    """
    compressed: list[str] = []
    blank_streak = 0
    for line in lines:
        if line.strip():
            blank_streak = 0
            compressed.append(line.rstrip())
        else:
            blank_streak += 1
            if blank_streak <= 2:
                compressed.append('')
    return compressed


def convert_indented_code_blocks(lines: list[str]) -> list[str]:
    """Convert indented code blocks to fenced code blocks.

    Transforms indented code blocks (4 spaces) that appear after blank lines
    into fenced code blocks (triple backticks). This improves readability and
    compatibility with various Markdown renderers.

    Args:
        lines: A list of strings representing document lines.

    Returns:
        A list of strings with indented code blocks converted to fenced format
        where appropriate. Code blocks not preceded by blank lines are left
        unchanged to preserve intended indentation.

    Note:
        Only converts indented blocks that:
        - Start after a blank line
        - Contain at least one internal blank line
        This avoids converting simple indented lists or paragraphs.
    """
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('    '):
            if i > 0 and lines[i - 1].strip() != '':
                result.append(line)
                i += 1
                continue
            block: list[str] = []
            saw_blank = False
            j = i
            while j < len(lines):
                current = lines[j]
                if current.startswith('    '):
                    block.append(current[4:])
                    j += 1
                    continue
                if current == '':
                    block.append('')
                    saw_blank = True
                    j += 1
                    continue
                break
            if block and saw_blank:
                while block and block[-1] == '':
                    block.pop()
                while block and block[0] == '':
                    block.pop(0)
                if block:
                    result.append('```')
                    result.extend(block)
                    result.append('```')
                    i = j
                    continue
            if block:
                for part in block:
                    if part == '':
                        result.append('')
                    else:
                        result.append('    ' + part)
            i = j
            continue
        result.append(line)
        i += 1
    return result


def convert_file(html_path: Path, md_path: Path) -> None:
    """Convert an HTML file to Markdown format with custom processing.

    Performs a complete conversion pipeline:
        1. Runs Pandoc with Lua filter to convert HTML to GFM
        2. Reformats summary tables
        3. Converts indented code blocks to fenced blocks
        4. Collapses excessive blank lines
        5. Replaces special characters and escaped sequences
        6. Writes the result to the output file

    Args:
        html_path: Path object pointing to the input HTML file.
        md_path: Path object pointing to the desired output Markdown file.
            Parent directories will be created if they don't exist.

    Raises:
        subprocess.CalledProcessError: If the Pandoc command fails.
        OSError: If there are file system errors during read/write operations.

    Example:
        >>> from pathlib import Path
        >>> convert_file(Path('docs/input.html'), Path('output/result.md'))
    """
    cmd = PANDOC_BASE_CMD + [str(html_path)]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    lines = completed.stdout.splitlines()
    lines = rewrite_summary_tables(lines)
    lines = convert_indented_code_blocks(lines)
    lines = collapse_blank_lines(lines)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_content = '\n'.join(line.rstrip() for line in lines).strip()
    md_content = md_content.replace('\u00a0', ' ')
    md_content = (
        md_content.replace('\\<', '&lt;')
        .replace('\\>', '&gt;')
        .replace('\\[', '&#91;')
        .replace('\\]', '&#93;')
    )
    if md_content:
        md_content += '\n'
    md_path.write_text(md_content, encoding='utf-8')


def main() -> None:
    """Main entry point for batch conversion of documentation files.

    Converts HTML documentation files from predefined directory structures
    to Markdown format. Processes files from the following directories:
        - components
        - attributes
        - packages
        - releases

    Also handles special case for docbook.html conversion.

    The function expects the following directory structure:
        docs/manuals/ium_componentref/html/{directory}/*.html
        docs/manuals/commandref/html/docbook.html

    Output files are written to:
        docs/manuals/ium_componentref/markdown/{directory}/*.md
        docs/manuals/commandref/markdown/commandref.md
    """
    html_root = Path('docs/manuals/ium_componentref/html')
    md_root = Path('docs/manuals/ium_componentref/markdown')
    targets = []
    for directory in ['components', 'attributes', 'packages', 'releases']:
        dir_path = html_root / directory
        if dir_path.exists():
            for html_file in dir_path.rglob('*.html'):
                targets.append(html_file)
    for html_file in targets:
        rel = html_file.relative_to(html_root)
        md_file = md_root / rel.with_suffix('.md')
        convert_file(html_file, md_file)

    docbook_html = Path('docs/manuals/commandref/html/docbook.html')
    if docbook_html.exists():
        convert_file(docbook_html, Path('docs/manuals/commandref/markdown/commandref.md'))


if __name__ == '__main__':
    main()

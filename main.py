#!/usr/bin/env python3
"""Main entry point for the HTML to Markdown converter.

This script serves as a simple entry point that delegates to the main
conversion module. For more advanced usage, import and use the functions
from src.convert_manuals directly.
"""

from src.convert_manuals import main

if __name__ == '__main__':
    main()

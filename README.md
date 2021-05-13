# docfxmd

A proof-of-concept script to convert [docfx](https://dotnet.github.io/docfx/) yml files into markdown that can be used in a wiki environment.
The markdown output follows the docfx static html site format as closely as possible.

Usage:
```bash
python3 docfxmd.py -d docfx_project/api -o output_wiki/
```

This script is proof-of-concept and has only been used to convert docfx output from C# source code to be hosted on Gitlab Wiki.
docfxmd has not been heavily tested and may not always produce the correct results.

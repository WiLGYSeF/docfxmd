#!/usr/bin/env python3

import os
import pathlib
import sys

import yaml

from docfxmd_class import DocfxMd

def build_directory(dname, output_name):
    for root, dirs, files in os.walk(dname):
        for fname in files:
            if not fname.endswith('.yml'):
                continue

            in_path = os.path.join(root, fname)

            doc_md = DocfxMd()
            result = doc_md.docfx_to_md(load_file(in_path))
            if result is None:
                continue

            path = pathlib.Path(in_path)
            out_path = pathlib.Path(output_name) / path.relative_to(*path.parts[:1])

            os.makedirs(out_path.parent, exist_ok=True)
            with open(out_path.with_suffix('.md'), 'w', encoding='utf-8') as file:
                file.write(result)

def load_file(fname):
    with open(fname, 'r', encoding='utf-8') as file:
        return yaml.load(file, Loader=yaml.Loader)

def main(args):
    build_directory('api', 'output')


if __name__ == '__main__':
    main(sys.argv)

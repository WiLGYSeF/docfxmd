#!/usr/bin/env python3

import os
import pathlib
import sys

from docfxmd_class import DocfxMd


LINK_EXTENSIONS = False


def build_directory(dname, output_name):
    doc_md = DocfxMd(dname, link_extensions=LINK_EXTENSIONS)
    paths = {}

    for root, dirs, files in os.walk(dname):
        for fname in files:
            if not fname.endswith('.yml'):
                continue

            path = os.path.join(root, fname)
            print('loading %s ...' % fname)
            data = doc_md.load_file(path)

            path = pathlib.Path(path)
            paths[id(data)] = pathlib.Path(output_name) / path.relative_to(*path.parts[:1])

    for basename, data in doc_md.files.items():
        print(basename)
        result = doc_md.docfx_to_md(data)
        if result is None:
            continue

        out_path = paths[id(data)]
        os.makedirs(out_path.parent, exist_ok=True)
        with open(out_path.with_suffix('.md'), 'w', encoding='utf-8') as file:
            file.write(result)

def main(args):
    build_directory('api', 'output')


if __name__ == '__main__':
    main(sys.argv)

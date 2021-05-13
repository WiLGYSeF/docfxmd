#!/usr/bin/env python3

import argparse
import os
import pathlib
import sys

from docfxmd_class import DocfxMd


def build_directory(dname, output_name, **kwargs):
    namespace_index = kwargs.get('namespace_index')
    verbose = kwargs.get('verbose', 0)

    doc_md = DocfxMd(dname, **kwargs)
    paths = {}

    for root, dirs, files in os.walk(dname):
        for fname in files:
            if not fname.endswith('.yml'):
                continue

            path = os.path.join(root, fname)

            if verbose >= 2:
                print('loading %s ...' % fname)

            data = doc_md.load_file(path)

            path = pathlib.Path(path)
            paths[id(data)] = pathlib.Path(output_name) / path.relative_to(*path.parts[:1])

    for basename, data in doc_md.files.items():
        if verbose >= 1:
            print('parsing %s' % basename)

        result = doc_md.docfx_to_md(data)
        if result is None:
            continue

        out_path = paths[id(data)]
        os.makedirs(out_path.parent, exist_ok=True)
        with open(out_path.with_suffix('.md'), 'w', encoding='utf-8') as file:
            file.write(result)

    if namespace_index is not None:
        if namespace_index[0] == os.path.sep:
            namespace_index = namespace_index[1:]

        path = os.path.join(output_name, namespace_index + '.md')
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(doc_md.namespace_index_md())

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir',
        action='store', metavar='DIR', required=True,
        help='docfx api directory containing yml files'
    )
    parser.add_argument('-o', '--output',
        action='store', metavar='DIR', required=True,
        help='output markdown directory'
    )
    parser.add_argument('--namespace',
        action='store', metavar='PATH', nargs='?', default=False,
        help='create an index of namespaces and store it in {OUTPUT}/{PATH}.md'
    )
    parser.add_argument('--link-extensions',
        action='store_true', default=False,
        help='append file extensions to links'
    )
    parser.add_argument('--no-link-extensions',
        dest='link_extensions', action='store_false',
        help='do not append file extensions to links (default)'
    )
    parser.add_argument('--abpath',
        action='store', metavar='PATH',
        help='set the absolute path prefix for links'
    )
    parser.add_argument('-v', '--verbose',
        action='count',
        help='verbose mode'
    )
    argspace = parser.parse_args(args[1:])

    if argspace.namespace is not False:
        if argspace.namespace is None:
            argspace.namespace = '!Namespaces'

    build_directory(
        argspace.dir,
        argspace.output,
        absolute_link_path=argspace.abpath,
        namespace_index=argspace.namespace,
        link_extensions=argspace.link_extensions,
        verbose=argspace.verbose,
    )


if __name__ == '__main__':
    main(sys.argv)

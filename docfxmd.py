#!/usr/bin/env python3

import functools
import json
import os
import pathlib
import re
import sys

import yaml


TAG_CODE = 'code'

TAG_REGEX = re.compile(r'<(/?)([A-Za-z]+)>')

TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'

LANG_CS = 'cs'
LANG_VB = 'vb'
LANG = LANG_CS


def build_index(arr):
    index = {}
    count = 0
    for val in arr:
        index[val] = count
        count += 1
    return index

def html_to_md(data):
    result = ''
    open_tags = []
    last = 0

    for match in TAG_REGEX.finditer(data):
        if match[1] == '':
            prev_tag = open_tags[-1].lower() if len(open_tags) != 0 else None
            tag = match[2].lower()

            if prev_tag == TAG_CODE:
                result += '`%s`' % data[last:match.start()]
            else:
                result += data[last:match.start()]
            last = match.end()
            open_tags.append(match[2])
        else:
            prev_tag = open_tags.pop().lower()
            tag = match[2].lower()
            if prev_tag != tag:
                raise ValueError()

            prev_tag = open_tags[-1].lower() if len(open_tags) != 0 else None
            tag = match[2].lower()

            if tag == TAG_CODE:
                result += '`%s`' % data[last:match.start()]
            else:
                result += data[last:match.start()]
            last = match.end()

    result += data[last:]
    return result

def docfx_to_md(data):
    if not isinstance(data, dict) or 'items' not in data:
        return None

    markdown = []
    items = data.get('items')

    type_order = build_index([
        TYPE_CLASS,
        TYPE_CONSTRUCTOR,
        TYPE_FIELD,
        TYPE_PROPERTY,
        TYPE_METHOD,
    ])

    def cmp(a, b): #pylint: disable=invalid-name
        atype = type_order.get(a['type'].lower(), 9999)
        btype = type_order.get(b['type'].lower(), 9999)

        if atype != btype:
            return atype - btype
        return 1 if a['id'] >= b['id'] else -1

    items.sort(key=functools.cmp_to_key(cmp))

    type_headers = set()

    for item in items:
        print(json.dumps(item, indent=4))

        item_md = []

        uid = item['uid']
        item_type = item['type'].lower()
        name = item['name']

        if item_type not in type_headers:
            if item_type == TYPE_CLASS:
                item_md.append('# Class %s' % name)
            elif item_type == TYPE_CONSTRUCTOR:
                item_md.append('## **Constructor**')
            elif item_type == TYPE_FIELD:
                item_md.append('## **Fields**')
            elif item_type == TYPE_PROPERTY:
                item_md.append('## **Properties**')
            elif item_type == TYPE_METHOD:
                item_md.append('## **Methods**')
            item_md.append('')
            type_headers.add(item_type)

        if item_type in (TYPE_FIELD, TYPE_PROPERTY):
            item_md.append('### ' + item['id'])
            item_md.append('')
        elif item_type == TYPE_METHOD:
            item_md.append('### ' + item['name'])
            item_md.append('')

        summary = item.get('summary')
        if summary is not None:
            item_md.append(html_to_md(summary))
            item_md.append('')

        inheritance = item.get('inheritance')
        if inheritance is not None:
            item_md.append('Inheritance:')
            for inherit in inheritance:
                item_md.append('- ' + inherit)
            item_md.append('')

        derived_classes = item.get('derivedClasses')
        if derived_classes is not None:
            for cls in derived_classes:
                item_md.append('- ' + cls)
            item_md.append('')

        inherited_members = item.get('inheritedMembers')
        if inherited_members is not None:
            item_md.append('Inherited Members:')
            for member in inherited_members:
                item_md.append('- ' + member)
            item_md.append('')

        if item_type == TYPE_CLASS:
            namespace = item.get('namespace')
            if namespace is not None:
                item_md.append('Namespace: ' + namespace)
                item_md.append('')

            assemblies = item.get('assemblies')
            if assemblies is not None:
                item_md.append('Assemblies:')
                for asm in assemblies:
                    item_md.append('- ' + asm)
                item_md.append('')

        syntax = item.get('syntax')
        if syntax is not None:
            if item_type == TYPE_CLASS:
                item_md.append('Syntax')
            else:
                item_md.append('Declaration')

            if LANG == LANG_CS:
                content_key = 'content'
                lang = 'csharp'
            elif LANG == LANG_VB:
                content_key = 'content.vb'
                lang = ''

            item_md.append('```' + lang)
            item_md.append(syntax[content_key])
            item_md.append('```')

            parameters = syntax.get('parameters')
            if parameters is not None and len(parameters) != 0:
                has_description = any(map(lambda x: 'description' in x, parameters))
                item_md.append('Parameters')
                item_md.append('')
                if has_description:
                    item_md.append('| Type | Name | Description |')
                    item_md.append('|---|---|---|')
                    for param in parameters:
                        item_md.append('| %s | %s | %s |' % (
                            param['type'],
                            param['id'],
                            param.get('description', ''),
                        ))
                else:
                    item_md.append('| Type | Name |')
                    item_md.append('|---|---|')
                    for param in parameters:
                        item_md.append('| %s | %s |' % (param['type'], param['id']))

            return_result = syntax.get('return')
            if return_result is not None:
                if item_type == TYPE_PROPERTY:
                    item_md.append('Property Value')
                else:
                    item_md.append('Returns')
                item_md.append('')

                if 'description' in return_result:
                    item_md.append('| Type | Description |')
                    item_md.append('|---|---|')
                    item_md.append('| %s | %s |' % (
                        return_result['type'],
                        html_to_md(return_result['description'])
                    ))
                else:
                    item_md.append('| Type |')
                    item_md.append('|---|')
                    item_md.append('| %s |' % return_result['type'])

        remarks = item.get('remarks')
        if remarks is not None:
            item_md.append('Remarks')
            item_md.append('')
            item_md.append(html_to_md(remarks))
            item_md.append('')

        markdown.append(item_md)

    result = ''
    for item in markdown:
        result += '\n'.join(item) + '\n'
    return result

def build_directory(dname, output_name):
    for root, dirs, files in os.walk(dname):
        for fname in files:
            if not fname.endswith('.yml'):
                continue

            in_path = os.path.join(root, fname)
            result = docfx_to_md(load_file(in_path))
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

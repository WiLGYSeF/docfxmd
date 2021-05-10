#!/usr/bin/env python3

import functools
import json
from lxml import etree

import yaml


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
    doc = etree.HTML(data)
    for ele in doc[0]:
        result += ele.text
    return result

def docfx_to_md(data):
    markdown = []
    items = data['items']

    type_order = build_index([
        'class',
        'constructor',
        'field',
        'property',
        'method'
    ])

    def cmp(a, b): #pylint: disable=invalid-name
        atype = type_order.get(a['type'].lower(), 9999)
        btype = type_order.get(b['type'].lower(), 9999)

        if atype != btype:
            return atype - btype
        return 1 if a['id'] >= b['id'] else -1

    items.sort(key=functools.cmp_to_key(cmp))

    for item in items:
        print(json.dumps(item, indent=4))

        item_md = []

        uid = item['uid']
        item_type = item['type'].lower()
        name = item['name']

        if item_type == 'class':
            item_md.append('# Class %s' % name)
            item_md.append('')
        elif item_type == 'constructor':
            item_md.append('## Constructor')
            item_md.append('')
        elif item_type in ('field', 'property'):
            item_md.append('### ' + item['id'])
            item_md.append('')
        elif item_type == 'method':
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

        if item_type == 'class':
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
            if item_type == 'class':
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
                            param['description'],
                        ))
                else:
                    item_md.append('| Type | Name |')
                    item_md.append('|---|---|')
                    for param in parameters:
                        item_md.append('| %s | %s |' % (param['type'], param['id']))

            return_result = syntax.get('return')
            if return_result is not None:
                if item_type == 'property':
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
            doc = etree.HTML(remarks)
            item_md.append('Remarks')
            item_md.append('')
            item_md.append(html_to_md(remarks))
            item_md.append('')

        markdown.append(item_md)

    result = ''
    for item in markdown:
        result += '\n'.join(item) + '\n'

    with open('test.md', 'w') as file:
        file.write(result)

def load_file(fname):
    with open(fname, 'r') as file:
        return yaml.load(file.read(), Loader=yaml.Loader)

if __name__ == '__main__':
    docfx_to_md(load_file('test.yml'))

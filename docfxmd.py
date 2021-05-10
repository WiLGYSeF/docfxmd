#!/usr/bin/env python3

import json
from lxml import etree

import yaml


LANG_CS = 'cs'
LANG_VB = 'vb'
LANG = LANG_CS


def docfx_to_md(data):
    markdown = []
    for item in data['items']:
        print(json.dumps(item, indent=4))

        item_md = []

        uid = item['uid']
        item_type = item['type'].lower()
        name = item['name']

        if item_type == 'class':
            item_md.append('# Class %s' % name)
            item_md.append('')

        summary = item.get('summary')
        if summary is not None:
            doc = etree.HTML(summary)
            for ele in doc[0]:
                item_md.append(ele.text)
            item_md.append('')

        inheritance = item.get('inheritance')
        if inheritance is not None:
            item_md.append('Inheritance:')
            for inherit in inheritance:
                item_md.append('- ' + inherit)
            item_md.append('')

        inherited_members = item.get('inheritedMembers')
        if inherited_members is not None:
            item_md.append('Inherited Members:')
            for member in inherited_members:
                item_md.append('- ' + member)
            item_md.append('')

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
            item_md.append('Syntax')
            item_md.append('```')
            if LANG == LANG_CS:
                item_md.append(syntax['content'])
            elif LANG == LANG_VB:
                item_md.append(syntax['content.vb'])
            item_md.append('```')

        remarks = item.get('remarks')
        if remarks is not None:
            doc = etree.HTML(remarks)
            item_md.append('Remarks')
            item_md.append('')
            for ele in doc[0]:
                item_md.append(ele.text)
            item_md.append('')

        markdown.append(item_md)

    result = ''
    for item in markdown:
        result += '\n'.join(item) + '\n'
    print(result)

    with open('test.md', 'w') as file:
        file.write(result)

def load_file(fname):
    with open(fname, 'r') as file:
        return yaml.load(file.read(), Loader=yaml.Loader)

if __name__ == '__main__':
    docfx_to_md(load_file('test.yml'))

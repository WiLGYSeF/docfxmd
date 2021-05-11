import os

import yaml

from item_md import ItemMd
from convert import replace_strings, html_to_md, text_to_md, newline_to_br


TYPE_NAMESPACE = 'namespace'
TYPE_CLASS = 'class'
TYPE_STRUCT = 'struct'
TYPE_INTERFACE = 'interface'
TYPE_ENUM = 'enum'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'


class DocfxMd:
    def __init__(self, root, **kwargs):
        self.root = root

        self.link_extensions = kwargs.get('link_extensions', True)

        self.files = {}
        self.items_by_file = {}
        self.items = {}

    def load_file(self, fname):
        with open(fname, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.Loader)

        basename = os.path.basename(fname)
        if basename.endswith('.yml'):
            basename = basename[:-4]
        self.files[basename] = data

        if isinstance(data, dict):
            items = sorted(map(lambda x: ItemMd(self, x), data.get('items')))
            self.items_by_file[basename] = items

            for itm in items:
                self.items[itm.uid] = itm

        return data

    def docfx_file_to_md(self, fname):
        basename = os.path.basename(fname)
        if basename.endswith('.yml'):
            basename = basename[:-4]

        if basename not in self.files:
            self.load_file(fname)
        return self.docfx_to_md(self.files[basename])

    def docfx_to_md(self, data):
        if not isinstance(data, dict) or 'items' not in data:
            return None

        markdown = ''
        items = sorted(map(lambda x: ItemMd(self, x), data.get('items')))

        type_headers = set()

        first_item = items[0]
        if first_item.type == TYPE_NAMESPACE:
            return self.namespace_md(data)
        if first_item.type == TYPE_ENUM:
            return self.enum_md(items)

        for item in items:
            header = self.item_header(item, type_headers)
            if header is not None:
                markdown += header
                type_headers.add(item.type)

            if item.type in (TYPE_CONSTRUCTOR, TYPE_FIELD, TYPE_PROPERTY, TYPE_METHOD):
                markdown += '### %s\n\n' % text_to_md(item.name)

            markdown += item.markdown()

        return markdown

    def namespace_md(self, namespace):
        item = ItemMd(self, namespace['items'][0])
        result = self.item_header(item)

        references = []
        ref_str = []

        for ref in namespace['references']:
            if ref['uid'] in self.items:
                references.append(self.items[ref['uid']])
            else:
                ref_str.append(ref['uid'])

        type_headers = set()
        references.sort()

        for ref in references:
            if ref.type == TYPE_NAMESPACE:
                continue

            header = self.item_header(ref, type_headers, class_view=False)
            if header is not None:
                result += header

            link = ref.uid + '.md' if self.link_extensions else ref.uid

            result += '### [%s](%s)\n\n' % (
                text_to_md(ref.get_ident_name(ref.name)),
                self.sanitize_link(link)
            )
            summary = ref.summary()
            if summary is not None:
                result += summary

        if len(ref_str) != 0:
            result += '\n---\n'

        for ref in ref_str:
            result += '### %s\n\n' % ref

        return result

    def enum_md(self, items):
        enum_item = items[0]

        md_list = [
            self.item_header(enum_item),
            enum_item.summary(),
            enum_item.inheritance(),
            enum_item.inherited_members(),
            enum_item.namespace(),
            enum_item.assemblies(),
            enum_item.syntax(),
        ]

        result = ''
        idx = 1

        while idx < len(items):
            item = items[idx]
            if item.type != TYPE_FIELD:
                result += item.markdown() + '\n'
                idx += 1
                continue

            result += '| Name | Description |\n'
            result += '|---|---|\n'

            while idx < len(items):
                item = items[idx]
                if item.type != TYPE_FIELD:
                    idx -= 1
                    break

                result += '| %s | %s |\n' % (
                    text_to_md(item.name),
                    newline_to_br(html_to_md(item.item.get('description', '&nbsp;')))
                )
                idx += 1

            result += '\n'
            idx += 1

        md_list.append(result)
        md_list.append(enum_item.remarks())

        return '\n'.join(filter(lambda x: x is not None, md_list))

    def item_header(self, item, header_set=None, class_view=True):
        if header_set is not None:
            if item.type in header_set:
                return None
            header_set.add(item.type)

        if class_view:
            return {
                TYPE_NAMESPACE: '# Namespace %s\n\n' % text_to_md(item.name),
                TYPE_CLASS: '# Class %s\n\n' % text_to_md(item.name),
                TYPE_STRUCT: '# Struct %s\n\n' % text_to_md(item.name),
                TYPE_INTERFACE: '# Interface %s\n\n' % text_to_md(item.name),
                TYPE_CONSTRUCTOR: '## Constructors\n\n',
                TYPE_FIELD: '## **Fields**\n\n',
                TYPE_PROPERTY: '## **Properties**\n\n',
                TYPE_METHOD: '## **Methods**\n\n',
                TYPE_ENUM: '# Enum %s\n\n' % text_to_md(item.name),
            }.get(item.type)

        return {
            TYPE_CLASS: '## Classes\n\n',
            TYPE_STRUCT: '## Structs\n\n',
            TYPE_INTERFACE: '## Interfaces\n\n',
            TYPE_CONSTRUCTOR: '## Constructors\n\n',
            TYPE_FIELD: '## Fields\n\n',
            TYPE_PROPERTY: '## Properties\n\n',
            TYPE_METHOD: '## Methods\n\n',
            TYPE_ENUM: '## Enums\n\n',
        }.get(item.type)

    def get_link(self, fname):
        path = os.path.join(self.root, fname + '.yml')
        if not os.path.isfile(path):
            return None

        if self.link_extensions:
            return fname + '.md'
        return fname

    def sanitize_link(self, link):
        return replace_strings(link, {
            ' ': '-',
            '`': '-',
        })

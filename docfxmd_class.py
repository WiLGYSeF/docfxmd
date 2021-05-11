import os

import yaml

from item_md import ItemMd
from convert import text_to_md


TYPE_NAMESPACE = 'namespace'
TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'
TYPE_ENUM = 'enum'


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

        markdown = []
        items = sorted(map(lambda x: ItemMd(self, x), data.get('items')))

        type_headers = set()

        for item in items:
            item_mdlist = []

            if item.type == TYPE_NAMESPACE:
                item_mdlist.append(self.namespace_md(data))
            else:
                header = self.item_header(item, type_headers)
                if header is not None:
                    item_mdlist.append(header)

                    item_mdlist.append('')
                    type_headers.add(item.type)

                if item.type in (TYPE_CONSTRUCTOR, TYPE_FIELD, TYPE_PROPERTY, TYPE_METHOD):
                    item_mdlist.append('### ' + text_to_md(item.name))
                    item_mdlist.append('')

            item_mdlist.append(item.markdown())
            markdown.append(item_mdlist)

        result = ''
        for item in markdown:
            result += '\n'.join(item) + '\n'
        return result

    def namespace_md(self, namespace):
        item = namespace['items'][0]
        result = '# Namespace %s\n\n' % text_to_md(item['name'])

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

            name = ref.uid
            link = name + '.md' if self.link_extensions else name

            result += '### [%s](%s)\n\n' % (text_to_md(ref.get_ident_name(name)), link)
            summary = ref.summary()
            if summary is not None:
                result += summary

        for ref in ref_str:
            result += '### %s\n\n' % ref

        return result

    def item_header(self, item, header_set, class_view=True):
        if item.type in header_set:
            return None
        header_set.add(item.type)

        if class_view:
            if item.type == TYPE_CLASS:
                return '## Class %s\n\n' % text_to_md(item.name)
            if item.type == TYPE_CONSTRUCTOR:
                return '## Constructors\n\n'
            if item.type == TYPE_FIELD:
                return '## **Fields**\n\n'
            if item.type == TYPE_PROPERTY:
                return '## **Properties**\n\n'
            if item.type == TYPE_METHOD:
                return '## **Methods**\n\n'
            if item.type == TYPE_ENUM:
                return '## **Enums**\n\n'
        else:
            if item.type == TYPE_CLASS:
                return '## Classes\n\n'
            if item.type == TYPE_CONSTRUCTOR:
                return '## Constructors\n\n'
            if item.type == TYPE_FIELD:
                return '## Fields\n\n'
            if item.type == TYPE_PROPERTY:
                return '## Properties\n\n'
            if item.type == TYPE_METHOD:
                return '## Methods\n\n'
            if item.type == TYPE_ENUM:
                return '## Enums\n\n'
        return None

    def get_link(self, fname):
        path = os.path.join(self.root, fname + '.yml')
        if not os.path.isfile(path):
            return None
        if self.link_extensions:
            return fname + '.md'
        return fname
